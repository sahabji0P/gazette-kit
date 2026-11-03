# gazette-kit

**Your own daily newspaper, written by your own AI agent.**

gazette-kit is a template for running a personal newspaper that an agent writes on a schedule, for example three editions a day. Any agent that can read and write files, run shell commands and fetch web pages can run it: Claude Code, Codex, Grok Bot, or another agent CLI. Schedule it with the agent's own routines, cron, launchd, or a Fetch.ai uAgent acting as the timer. It isn't a link dump. Each edition has to teach something or spark something you can try the same day, every fact carries its source and a status, and when nothing important happened, the paper stays quiet.

![The sample edition's front page](examples/sample-front.png)

*The sample edition. Every company and number in it is made up.* After cloning, open `examples/sample-edition/index.html` to click around.

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

The agent does the judgement (what matters, is it true, how to say it). The scripts do the mechanics (fetch, dedupe, layout, checks), so the layout, links and bookkeeping are the same every edition.

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
- **A private "Build for my project" section.** Tell it about your project, and it turns the day's news into labelled suggestions for it. Public builds (`build.py --public`) drop project stories and private blocks at build time, and `check.py --public` fails if any configured private marker word or private-block tag survives. It can't recognise a paraphrase, so the skills tell the agent to keep project details out of public fields.
- **Two-way links, chains, glossary.** Related stories link both ways, versions form chains, and jargon links to a glossary automatically.
- **Sources are data, not instructions.** The agent is told to ignore instructions found in fetched pages and to report them. That's a rule in `AGENTS.md`, not a sandbox.
- **Agent-agnostic, no hosting, no lock-in.** Plain files, plain Python, and a site that opens from disk.

## Status

This is new. The scripts are covered by tests (`python3 -m unittest discover -s tests`), and CI runs them plus both build gates on every push. The sample edition was produced by hand, not by an agent run. The skills come from a real paper that has shipped 100+ editions, but this generic kit hasn't completed a full scheduled agent run yet. Issues and reports from your first runs are very welcome.

## How it compares

- **[GPT Newspaper](https://github.com/rotemweiss57/gpt-newspaper)** is a LangGraph app that writes a paper per request. gazette-kit is agent-agnostic files plus scripts, with memory between runs and quiet days.
- **[daily-brief](https://github.com/junjzhang/daily-brief)** and **[weekly-ai-news-digest](https://github.com/elbruno/weekly-ai-news-digest)** are digest pipelines published to GitHub Pages. gazette-kit adds per-fact status labels, a ship threshold, corrections that stick, and a private project section, and needs no hosting.

## Requirements

Python 3.9+ and an agent that can read and write files, run shell commands, and fetch web pages. Fonts load from Google Fonts by default. Set `theme.fonts_url` to `""` to work fully offline.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
