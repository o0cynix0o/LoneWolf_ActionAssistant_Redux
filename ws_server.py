#!/usr/bin/env python3
"""
WebSocket terminal bridge for the Lone Wolf Action Assistant Redux.

The browser sends raw terminal input to this server. The server starts
lonewolf_redux.py and streams terminal output back to xterm.js.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from websockets.asyncio.server import serve

try:
    import winpty  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    winpty = None

if os.name != "nt":
    import fcntl
    import pty
    import struct
    import termios


SCRIPT_DIR = Path(__file__).resolve().parent
ASSISTANT_SCRIPT = SCRIPT_DIR / "lonewolf_redux.py"
POWERSHELL_SCRIPT = SCRIPT_DIR / "lonewolf_redux.ps1"
WS_HOST = "localhost"
WS_PORT = int(os.environ.get("LONEWOLF_REDUX_WS_PORT", "8798"))
INIT_COLS = 120
INIT_ROWS = 30


def build_command() -> list[str]:
    last_save_txt = SCRIPT_DIR / "data" / "last-save.txt"
    load_args: list[str] = []
    try:
        if last_save_txt.exists():
            save_path = last_save_txt.read_text(encoding="utf-8").strip()
            if save_path and Path(save_path).exists():
                load_args = ["--load", save_path]
    except Exception:
        pass
    if os.name == "nt" and POWERSHELL_SCRIPT.exists():
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if powershell:
            ps_args = [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(POWERSHELL_SCRIPT)]
            if load_args:
                ps_args += ["-Load", load_args[1]]
            return ps_args
    return [sys.executable, "-u", str(ASSISTANT_SCRIPT)] + load_args


async def terminal_session(websocket):
    command = build_command()
    if os.name == "nt" and winpty is not None:
        await terminal_session_winpty(websocket, command)
    elif os.name != "nt":
        await terminal_session_posix_pty(websocket, command)
    else:
        await terminal_session_pipes(websocket, command)


async def terminal_session_winpty(websocket, command: list[str]) -> None:
    loop = asyncio.get_running_loop()
    try:
        pty_proc = winpty.PtyProcess.spawn(
            command,
            dimensions=(INIT_ROWS, INIT_COLS),
            cwd=str(SCRIPT_DIR),
        )
    except Exception as exc:
        await websocket.send(f"\r\nERROR: could not start Python assistant - {exc}\r\n")
        return

    out_queue: asyncio.Queue[str | None] = asyncio.Queue()
    stop_reader = threading.Event()

    def reader_thread() -> None:
        while not stop_reader.is_set():
            try:
                data = pty_proc.read(4096)
                if data:
                    asyncio.run_coroutine_threadsafe(out_queue.put(data), loop)
                elif not pty_proc.isalive():
                    break
            except (EOFError, OSError):
                break
            except Exception:
                break
        asyncio.run_coroutine_threadsafe(out_queue.put(None), loop)

    reader = threading.Thread(target=reader_thread, daemon=True)
    reader.start()

    async def pump_out() -> None:
        while True:
            data = await out_queue.get()
            if data is None:
                break
            try:
                await websocket.send(data)
            except Exception:
                break

    async def pump_in() -> None:
        try:
            async for msg in websocket:
                text = msg if isinstance(msg, str) else msg.decode("utf-8", errors="replace")
                if text.startswith("\x00"):
                    try:
                        obj = json.loads(text[1:])
                        if obj.get("type") == "resize":
                            rows = max(1, int(obj.get("rows", INIT_ROWS)))
                            cols = max(1, int(obj.get("cols", INIT_COLS)))
                            pty_proc.setwinsize(rows, cols)
                    except Exception:
                        pass
                else:
                    pty_proc.write(text)
        except Exception:
            pass

    out_task = asyncio.create_task(pump_out())
    in_task = asyncio.create_task(pump_in())
    await asyncio.wait([out_task, in_task], return_when=asyncio.FIRST_COMPLETED)

    stop_reader.set()
    out_task.cancel()
    in_task.cancel()
    await asyncio.gather(out_task, in_task, return_exceptions=True)

    try:
        pty_proc.terminate(force=True)
    except Exception:
        pass


def set_posix_pty_size(fd: int, rows: int, cols: int) -> None:
    if os.name == "nt":
        return
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


async def terminal_session_posix_pty(websocket, command: list[str]) -> None:
    loop = asyncio.get_running_loop()
    master_fd, slave_fd = pty.openpty()
    set_posix_pty_size(master_fd, INIT_ROWS, INIT_COLS)

    proc = subprocess.Popen(
        command,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=str(SCRIPT_DIR),
        close_fds=True,
    )
    os.close(slave_fd)

    out_queue: asyncio.Queue[str | None] = asyncio.Queue()
    stop_reader = threading.Event()

    def reader_thread() -> None:
        while not stop_reader.is_set():
            try:
                data = os.read(master_fd, 4096)
                if data:
                    text = data.decode("utf-8", errors="replace")
                    asyncio.run_coroutine_threadsafe(out_queue.put(text), loop)
                elif proc.poll() is not None:
                    break
            except OSError:
                break
        asyncio.run_coroutine_threadsafe(out_queue.put(None), loop)

    reader = threading.Thread(target=reader_thread, daemon=True)
    reader.start()

    async def pump_out() -> None:
        while True:
            data = await out_queue.get()
            if data is None:
                break
            try:
                await websocket.send(data)
            except Exception:
                break

    async def pump_in() -> None:
        try:
            async for msg in websocket:
                text = msg if isinstance(msg, str) else msg.decode("utf-8", errors="replace")
                if text.startswith("\x00"):
                    try:
                        obj = json.loads(text[1:])
                        if obj.get("type") == "resize":
                            rows = max(1, int(obj.get("rows", INIT_ROWS)))
                            cols = max(1, int(obj.get("cols", INIT_COLS)))
                            set_posix_pty_size(master_fd, rows, cols)
                    except Exception:
                        pass
                else:
                    os.write(master_fd, text.encode("utf-8", errors="replace"))
        except Exception:
            pass

    out_task = asyncio.create_task(pump_out())
    in_task = asyncio.create_task(pump_in())
    await asyncio.wait([out_task, in_task], return_when=asyncio.FIRST_COMPLETED)

    stop_reader.set()
    out_task.cancel()
    in_task.cancel()
    await asyncio.gather(out_task, in_task, return_exceptions=True)
    if proc.poll() is None:
        proc.terminate()
    try:
        os.close(master_fd)
    except OSError:
        pass


async def terminal_session_pipes(websocket, command: list[str]) -> None:
    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(SCRIPT_DIR),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except Exception as exc:
        await websocket.send(f"\r\nERROR: could not start Python assistant - {exc}\r\n")
        return

    async def pump_out() -> None:
        assert proc.stdout is not None
        while True:
            data = await proc.stdout.read(4096)
            if not data:
                break
            try:
                await websocket.send(data.decode("utf-8", errors="replace"))
            except Exception:
                break

    async def pump_in() -> None:
        assert proc.stdin is not None
        try:
            async for msg in websocket:
                text = msg if isinstance(msg, str) else msg.decode("utf-8", errors="replace")
                if text.startswith("\x00"):
                    continue
                proc.stdin.write(text.encode("utf-8", errors="replace"))
                await proc.stdin.drain()
        except Exception:
            pass

    out_task = asyncio.create_task(pump_out())
    in_task = asyncio.create_task(pump_in())
    await asyncio.wait([out_task, in_task], return_when=asyncio.FIRST_COMPLETED)
    out_task.cancel()
    in_task.cancel()
    await asyncio.gather(out_task, in_task, return_exceptions=True)
    if proc.returncode is None:
        proc.terminate()


def write_current_position() -> None:
    try:
        last_save_txt = SCRIPT_DIR / "data" / "last-save.txt"
        if not last_save_txt.exists():
            return
        save_path = last_save_txt.read_text(encoding="utf-8").strip()
        if not save_path or not Path(save_path).exists():
            return
        with Path(save_path).open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        book_num = int(data.get("Character", {}).get("BookNumber", 0))
        section = int(data.get("CurrentSection", 0))
        if book_num > 0 and section > 0:
            pos_file = SCRIPT_DIR / "current-position.json"
            pos_file.write_text(json.dumps({"book": book_num, "section": section}), encoding="utf-8")
            print(f"Position: Book {book_num}, Section {section}", flush=True)
    except Exception as exc:
        print(f"Could not read save position: {exc}", flush=True)


async def main() -> None:
    write_current_position()
    print(f"Lone Wolf WebSocket server: ws://{WS_HOST}:{WS_PORT}", flush=True)
    async with serve(terminal_session, WS_HOST, WS_PORT):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWebSocket server stopped.")
