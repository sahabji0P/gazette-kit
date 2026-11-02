# gazette-kit

**Your own daily newspaper, written by your own AI agent.**

gazette-kit is a template for running a personal newspaper that an agent (Claude Code, Codex, Grok Bot, a Fetch.ai uAgent, or anything that can read files and run a shell) writes on a schedule, for example three editions a day. It isn't a link dump. Each edition has to teach something or spark something you can try the same day, every fact carries its source and a status, and when nothing important happened, the paper stays quiet.

![The sample edition's front page](examples/sample-front.png)

*The sample edition. Every company and number in it is made up.* Open `examples/sample-edition/index.html` to click around.

## What's in the box

| | |
|---|---|
| **`AGENTS.md`** | The newsroom's rules and daily loop. Every agent reads it first. |
| **`skills/`** | How to do each step, as `SKILL.md` files: setup, gather, write, publish, build-for-my-project. |
| **`gazette.config.json`** | The one file you edit: paper name, owner, timezone and schedule, beats, sources, ship threshold, and your private project. |
| **`theme/`** | A newsprint design (front page, split reader, sections, threads, glossary, wire, archive, saved shelf). Restyle freely. |
| **`scripts/`** | Four stdlib-Python scripts that do the mechanical parts. Nothing to install. |
| **`handbook/`** | Deeper reference: roles, sourcing and fact-check, style, design, saves. |
| **`examples/`** | A built sample edition. |

The agent does the judgement (what matters, is it true, how to say it). The scripts do the mechanics (fetch, dedupe, layout, checks), so the paper comes out right every time.

## Quickstart

```bash
git clone <your fork> my-gazette && cd my-gazette
python3 scripts/build.py && open out/index.html      # see the sample paper (Linux: xdg-open)
```
Then open your agent in the folder and say:
1. **"Set up my paper."** It interviews you and fills `gazette.config.json`.
2. **"Run one edition."**
3. Put it on a schedule: see **[SETUP.md](SETUP.md)** for Claude Code, Codex, Grok Bot, uAgents and cron/launchd.

## How a run works

```
schedule ─▶ fetch.py ─▶ gather (hunt + verify) ─▶ QUIET? close run, stop, no ping
                                               └▶ SHIP ─▶ write ─▶ build.py ─▶ check.py PASS ─▶ runlog close ─▶ notes ─▶ ping
```

1. **`scripts/fetch.py`** reads your feeds, canonicalises URLs, drops what the paper already covered (`data/seen.json`), flags likely duplicates, and logs which sources worked (`data/runs.json`).
2. **Gather** (agent): hunts beyond the feeds in your trust order, verifies each claim against a primary source, scores **strike** 1–10, and calls SHIP or QUIET.
3. **Write** (agent): adds story records to `data/stories.json` and bodies to `data/bodies/`.
4. **`scripts/build.py`** lays it all out into `out/`: a static site that opens from `file://`, no server.
5. **`scripts/check.py`** is the gate: broken links, one-way related links, missing pages, unfilled templates, corrected wording coming back, and (with `--public`) any private content.
6. **`scripts/runlog.py`** closes the run and updates the seen-store.

## What makes it different

- **Every fact is labelled**: CONFIRMED, VENDOR-REPORTED, RUMOR or UNVERIFIED, with a link to the original and the time it was checked.
- **Quiet runs are real.** Nothing at or above the ship threshold means no edition and no ping. And a run where the feeds failed is recorded as *failed*, never passed off as a quiet day.
- **Memory between runs**: a watchlist and editorial notes (`notes/MEMORY.md`), a seen-store for dedupe, and a run log.
- **Corrections stick.** Corrected wording goes into `data/corrections.json`, and the check fails if it ever comes back.
- **A private "Build for my project" section.** Tell it about your project, and it turns the day's news into labelled suggestions for it. Those stay out of public builds (`build.py --public`), and `check.py --public` proves it.
- **Two-way links, chains, glossary.** Related stories link both ways, versions form chains, and jargon links to a glossary automatically.
- **Sources are data, not instructions.** Prompt injection in fetched pages is ignored and reported.
- **Agent-agnostic, no hosting, no lock-in.** Plain files, plain Python, and a site that opens from disk.

## Requirements

Python 3.9+ and an agent that can read and write files, run shell commands, and fetch web pages. Fonts load from Google Fonts by default. Set `theme.fonts_url` to `""` to work fully offline.

## License

MIT. See [LICENSE](LICENSE).
