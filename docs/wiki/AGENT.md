# Lone Wolf Wiki Authoring Guide

This file is the operating guide for editing the Lone Wolf Action Assistant Redux wiki pages.

The Grey Star wiki is the style model: warm, practical, player-facing, and written like a good game guide. The Lone Wolf wiki should explain how to play with the assistant, not how the code works.

## Voice

Write to the player as "you". Use a friendly guide voice: calm, useful, and a little adventurous when the subject earns it.

Do write like this:

- "Keep one Meal in reserve unless Hunting is carrying that part of the journey."
- "If the app offers a loot button, use it. Inventory pressure is part of Book 1."
- "This is a good replay branch, not something you need to force into your first clear."

Do not write like this:

- "The test harness validates this route."
- "The route audit shows a branch condition."
- "This code path triggers automation."

## Banned Player-Facing Phrases

Keep these out of ordinary wiki pages:

- `test harness`
- `regression test`
- `route audit`
- `code path`
- `mechanical reason`
- `narrative reason`
- `completionist scaffolding`
- `playtest`
- `integrity check`

Internal pages may mention these terms only when describing the authoring rules themselves.

## Spoiler Scope

Spoiler scope is per page.

|Page|Spoilers allowed|Spoilers not allowed|
|----|----------------|--------------------|
|Book 1 Strategy Guide|Book 1 events|Books 2 and later|
|Book 2 Strategy Guide|Books 1 and 2 events|Books 3 and later|
|Achievement 100 Percent Guide|Only implemented books unless clearly labeled future|Unimplemented book details|
|Full Campaign Story Run|Route-light and spoiler-light|Detailed story endings|

Each strategy guide should include a heads-up paragraph near the top.

## Quotes

When a strategy guide needs book flavor, use short quotes from the local Project Aon files in:

```text
books\lw\<bookcode>\sect<N>.htm
```

Keep any quote short, around 25 words or fewer. Use it to support strategy, not to reproduce the book.

Attribution format:

```markdown
> *"Short quote."*
>
> - Section 1
```

Avoid adjacent blockquotes with blank lines between them. Markdown lint can dislike that shape.

## Page Set

The Lone Wolf wiki should mirror the Grey Star wiki shape as the app grows:

- Home
- Getting Started
- Installing Project Aon Books
- Command Reference
- Game Modes
- Combat Guide
- Inventory and Item Rules
- Stats and Achievements
- Campaign and Saves
- Public Release Guide
- Book Support Matrix
- Strategy Guide
- Full Campaign Story Run
- Achievement 100 Percent Guide
- FAQ
- one strategy guide per supported book

If a page describes unsupported books, be honest. Say "not started" or "future pipeline target".

## Cross-Linking

Link to wiki pages by slug, without `.md`:

```markdown
See the [Book 1 Strategy Guide](Book-1-Strategy-Guide).
```

## File Mirror Rule

At the moment, Lone Wolf has a project docs mirror at:

```text
docs\wiki
```

If a live GitHub wiki checkout is added later at:

```text
wiki
```

then every wiki edit must keep both folders in sync.

## Release Honesty

Do not call a package release-ready until the packaging checks are complete. Book 1 is now the playable release candidate. Book 2 is playable in the helper build, but needs more real-route time before release-candidate wording.
