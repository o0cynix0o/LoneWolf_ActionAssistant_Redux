# Lone Wolf AA2 Agent Handoff

This repo is the clean rebuild target for **Lone Wolf Action Assistant Redux**.

## Current State

- Root: `C:\Scripts\LoneWolf_ActionAssistant_Redux`
- GitHub: `https://github.com/o0cynix0o/LoneWolf_ActionAssistant_Redux`
- Installed local book sources: `books\lw\01fftd` through `books\lw\29tsoc`, plus `books\lw\dotd`
- Status: Book 1 playable release candidate published as `v0.1.0-rc1`; Book 2 rules/handoff scan is complete and rulings are pending under GitHub issue #27

The folder was bootstrapped from the Grey Star Action Assistant workflow so the next agent can reuse the modern web GUI cards, receipt drawer, launcher shape, docs structure, packaging workflow, and audit/test conventions.

Book 1 rules, character creation, route helpers, automation, combat support, achievements, and wiki pages are now in place. Do not treat later books as supported until each one goes through the Lone Wolf book pipeline.

## Hard Rules

- Do not commit `books\lw`.
- Do not redistribute Project Aon book files in releases.
- Keep saves, runtime state, wiki checkout, and dist artifacts out of git.
- Use `books\lw\01fftd` as the first book audit source.
- Book text and rules are the authority.
- Public strategy docs should read like a friendly strategy guide, not a clinical report.
- Technical audit logs can be terse and mechanical.
- For bugs: open GitHub issue, fix, update docs, commit with issue closure, push, package if release-worthy, publish release, close/verify issue.

## Current Priorities

1. Resolve the Book 2 rulings in `testing\logs\LWBOOK2_RULINGS_QUEUE.md`.
2. Start Book 2 implementation only after those rulings are clear: setup/start-state first, then section-flow, automation, combat, achievements, docs, and tests.
3. Keep public docs in a friendly team voice; keep technical audit logs direct and factual.

## Useful Source Projects

- Grey Star workflow/template: `C:\Scripts\Grey Star`
- Original Lone Wolf project/reference: `C:\Scripts\Lone Wolf`

Use Grey Star for **workflow and UI architecture**. Use the original Lone Wolf project and Project Aon Book 1 files for **Lone Wolf rules**.

## Handoff Files

- `docs\AGENT_HANDOFF.md`
- `docs\LONE_WOLF_AA2_WORKFLOW.md`
- `testing\logs\BOOTSTRAP_HANDOFF.md`
