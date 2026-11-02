---
name: gazette-setup
description: First-time setup for a gazette-kit paper. Interviews the owner and fills gazette.config.json (paper name, beats, sources, schedule, private project), clears the sample data, and runs a first build. Use when the config still holds the sample values, or when the owner says "set up my paper" or "change my beats/sources".
---

# Set up the paper

The goal is a `gazette.config.json` that describes *this* owner's paper, and a clean `data/` so the first real edition doesn't carry the sample stories.

Ask one short question at a time. Offer a sensible default with each question so the owner can just say "yes". Never invent the owner's details.

## 1. Interview

Ask, in this order:

1. **Paper**: name (shown in the masthead), a one-line tagline, the owner's name for the folio, and a short slug for browser storage (lowercase, dashes).
2. **Agent**: what the editor signs as (byline, e.g. "By Informer"), and the label for its opinion box ("Informer's take").
3. **Time**: timezone (IANA name like `Europe/Berlin`), a short label (`CET`), run times and slot names (default 09:00 morning · 14:00 afternoon · 19:00 evening), and whether weekends run.
4. **Beats**: what the paper covers. Turn the answer into:
   - `sections`: 4–7 front-page sections. Each story has **exactly one**. Each needs `key`, `label`, `short`, `blurb`. Use `"front": "strip"` for a thin one-line section (like People), and `"hidden"` to keep a section off the front.
   - `threads`: 0–5 cross-cutting topics a story can also carry (e.g. Voice, Memory, Safety, Pricing).
   - `tags`: extra chips (e.g. "Open weights", "Agents").
   - `standing_beats`: topics that must stay on or near the front even when quiet (optional).
   Keep a section with key `build` if the owner wants the idea engine.
5. **Sources**: the trust order (keep the default unless they disagree) and feeds. For each feed: `id`, `name`, `url`, `tier` (1 = primary). Pages with no feed get `"type": "page"` and are checked by hand each run. Prefer official blogs, changelogs, GitHub `releases.atom`, arXiv listings and registries over aggregators.
6. **Policy**: strike threshold to ship (default 7), cards per front section (5).
7. **Project** (optional): "Is there a project you want same-day ideas for?" If yes, collect `name`, a 3–5 sentence `about` (what it does, its users, its stack), `label` ("Build for X"), `id_prefix` (`build-x-`), and extra `private_markers` (codenames, client names). It stays `"private": true` unless the owner explicitly says the ideas may be public.

## 2. Write the config

Edit `gazette.config.json` in place and keep the same shape. Remove `theme.banner` (it marks the sample). Show the owner the diff, or a short summary of it.

## 3. Clear the sample

Only after the owner confirms:

- `data/stories.json` becomes `{"edition": {"number": 0, "published": null, "slot": null}, "lead": null, "flash": "", "tape": [], "thin_ticks": [], "watchlist": [], "chains": [], "stories": []}`
- delete the files in `data/bodies/`
- `data/editions.json` becomes `{"editions": []}`, `data/corrections.json` becomes `{"do_not_reintroduce": []}`, `data/glossary.json` becomes `{"terms": []}`
- `data/runs.json` and `data/seen.json` stay as they are (empty)
- reset `notes/MEMORY.md` and `notes/EDITIONS.md` to their headers only

## 4. Smoke test

```bash
python3 scripts/fetch.py --hours 24
```
Report which feeds failed and fix their URLs with the owner. Then close the test run:
```bash
python3 scripts/runlog.py close --status quiet --top-strike 0 --note "setup test"
```
(If most feeds failed, use `--status failed`.)

## 5. Schedule

Point the owner to `SETUP.md` for their agent (Claude Code, Codex, Grok Bot, uAgents, or plain cron). The scheduled prompt is the same everywhere:

> Run one edition of the paper in this folder. Read AGENTS.md first and follow it exactly.
