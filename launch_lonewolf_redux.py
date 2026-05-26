#!/usr/bin/env python3
"""Cross-platform launcher for the Lone Wolf web assistant."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def start_process(args: list[str], env: dict[str, str] | None = None) -> subprocess.Popen:
    creationflags = 0
    startupinfo = None
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.Popen(
        args,
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=creationflags,
        startupinfo=startupinfo,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch the Lone Wolf web assistant.")
    parser.add_argument("--http-port", type=int, default=8797)
    parser.add_argument("--ws-port", type=int, default=8798, help="Port for the embedded CLI terminal bridge.")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    url = f"http://localhost:{args.http_port}"
    env = os.environ.copy()
    env["LONEWOLF_REDUX_HTTP_PORT"] = str(args.http_port)
    env["LONEWOLF_REDUX_WS_PORT"] = str(args.ws_port)

    print("")
    print("  =========================================")
    print("   LONE WOLF REDUX  --  Python Launcher")
    print("  =========================================")
    print("")

    app_proc = start_process(
        [sys.executable, str(ROOT / "app_server.py"), "--port", str(args.http_port)],
        env=env,
    )
    ws_proc = start_process(
        [sys.executable, str(ROOT / "ws_server.py")],
        env=env,
    )

    time.sleep(1.2)
    failed = False
    for name, proc in (("Web app", app_proc), ("CLI bridge", ws_proc)):
        if proc.poll() is not None:
            failed = True
            print(f"  ERROR: {name} server failed to start.")
            output = proc.stdout.read() if proc.stdout else ""
            if output.strip():
                print(output.rstrip())

    if failed:
        for proc in (app_proc, ws_proc):
            if proc.poll() is None:
                proc.terminate()
        return 1

    print(f"  Library:   {url}")
    print(f"  Web App:   {url}/assistant.html")
    print(f"  CLI WS:    ws://localhost:{args.ws_port}")
    print("")
    if not args.no_browser:
        webbrowser.open(url)
    print("  Press ENTER to stop everything and exit.")
    print("")

    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print("")
    finally:
        for proc in (app_proc, ws_proc):
            if proc.poll() is None:
                proc.terminate()
        time.sleep(0.5)
        for proc in (app_proc, ws_proc):
            if proc.poll() is None:
                proc.kill()
    print("  Servers stopped. Goodbye.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
