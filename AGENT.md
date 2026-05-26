# Lone Wolf AA2 Agent Handoff

This repo is the clean rebuild target for **Lone Wolf Action Assistant Redux**.

## Current State

- Root: `C:\Scripts\LoneWolf_ActionAssistant_Redux`
- GitHub: `https://github.com/o0cynix0o/LoneWolf_ActionAssistant_Redux`
- First book source: `books\lw\01fftd`
- Status: pre-alpha scaffold

The folder was bootstrapped from the Grey Star Action Assistant workflow so the next agent can reuse the modern web GUI cards, receipt drawer, launcher shape, docs structure, packaging workflow, and audit/test conventions.

The runtime still contains many Grey Star-specific rule assumptions. That is expected at this stage. Do not treat the assistant logic as Lone Wolf complete until those assumptions are removed.

## Hard Rules

- Do not commit `books\lw`.
- Do not redistribute Project Aon book files in releases.
- Keep saves, runtime state, wiki checkout, and dist artifacts out of git.
- Use `books\lw\01fftd` as the first book audit source.
- Book text and rules are the authority.
- Public strategy docs should read like a friendly strategy guide, not a clinical report.
- Technical audit logs can be terse and mechanical.
- For bugs: open GitHub issue, fix, update docs, commit with issue closure, push, package if release-worthy, publish release, close/verify issue.

## First Real Build Pass

1. Replace Grey Star character model with Lone Wolf Book 1 rules.
2. Replace Magicks/Willpower UI with Kai Disciplines, Gold Crowns, Meals, Backpack, Weapons, and Special Items.
3. Rebuild new character creation from `books\lw\01fftd\action.htm` and related rules pages.
4. Parse or audit the Book 1 rules pages:
   - `action.htm`
   - `cmbtrulz.htm`
   - `crtable.htm`
   - equipment/rules pages
   - numbered sections
5. Build `data\book1-simple-automations.json`.
6. Build `data\book1-section-flows.json`.
7. Add route checks only after the section audit identifies real stat/roll branch math.
8. Add playtests and strategy docs only after the basic assistant can create a valid Book 1 character and move sections.

## Useful Source Projects

- Grey Star workflow/template: `C:\Scripts\Grey Star`
- Original Lone Wolf project/reference: `C:\Scripts\Lone Wolf`

Use Grey Star for **workflow and UI architecture**. Use the original Lone Wolf project and Project Aon Book 1 files for **Lone Wolf rules**.

## Handoff Files

- `docs\AGENT_HANDOFF.md`
- `docs\LONE_WOLF_AA2_WORKFLOW.md`
- `testing\logs\BOOTSTRAP_HANDOFF.md`
