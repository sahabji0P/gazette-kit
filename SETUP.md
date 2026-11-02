# Setup: point your agent at it and put it on a schedule

Every agent runs the same loop from `AGENTS.md`. Only the way you start it differs. The prompt is always the same:

> **Run one edition of the paper in this folder. Read AGENTS.md first and follow it exactly. Start with `python3 scripts/fetch.py`.**

You need **Python 3.9+** (standard library only, nothing to install) and an agent that can read and write files, run shell commands and fetch web pages.

## 1. First run (any agent)

1. Fork or copy this repo.
2. Open your agent in the folder and say: **"Set up my paper."** It follows `skills/gazette-setup`: it interviews you, fills `gazette.config.json`, clears the sample data and runs a fetch smoke test. (You can also edit `gazette.config.json` by hand.)
3. Say: **"Run one edition."** Then open `out/index.html` in your browser.

When that works, schedule it with one of the recipes below.

## 2. Where state lives (read before choosing a scheduler)

Everything the paper remembers is in files: `data/` (stories, seen-store, run log), `notes/` and `hunts/`.
- **Runs on your own machine** (desktop app, cron, launchd): state stays in the folder. Nothing else needed. Runs scheduled while the machine sleeps are skipped or run late. `fetch.py` notices a late run and covers the whole window.
- **Runs in the cloud** (cloud routines, CI): each run starts from a **fresh clone**. The paper must live in a (private) git repo, and every run must **commit and push** `data/`, `notes/` and `hunts/` at the end (`skills/gazette-publish` §7 already says so), or the next run forgets everything. `out/` is rebuilt every time and isn't committed. To read the paper, pull and run `python3 scripts/build.py`.

Keep the repo **private** if you use the project section. Public repos expose `data/stories.json`, including private ideas.

## 3. Claude Code

Install the extras once (see `extras/claude-code/README.md`):
```bash
cp extras/claude-code/CLAUDE.md ./CLAUDE.md
mkdir -p .claude && cp extras/claude-code/settings.json .claude/settings.json
ln -s ../skills .claude/skills
```
`CLAUDE.md` imports `AGENTS.md`, `.claude/skills` makes the five skills available, and `settings.json` allows the kit's own scripts and web fetching so scheduled runs don't stop at permission prompts. Review it and tighten it as you like.

- **Desktop app:** create a scheduled task in this folder with the prompt above, at your three run times.
- **Cloud routine:** use `/schedule` (or the routines page) with the prompt above, plus: *"When done, commit and push data/, notes/ and hunts/."* See §2.
- **Headless with cron or launchd** (machine must be awake):
  ```bash
  cd /path/to/your-gazette && claude -p "Run one edition of the paper in this folder. Read AGENTS.md first and follow it exactly. Start with python3 scripts/fetch.py."
  ```

## 4. Codex

Codex reads `AGENTS.md` natively. The skills are plain markdown that `AGENTS.md` points to, so they work without any skill support.
```bash
cd /path/to/your-gazette && codex exec "Run one edition of the paper in this folder. Read AGENTS.md first and follow it exactly. Start with python3 scripts/fetch.py."
```
Schedule that line with cron or launchd (§6). Give Codex permission to write files in the folder, run `python3` and use the network. Check your Codex sandbox settings.

## 5. Grok Bot and other chat agents with routines

Create a routine with the prompt above at your run times, attached to wherever the paper lives (a box workspace or a connected machine). If the agent builds on a remote box and you read on another machine, add a sync step at the end of the routine. Report a sync only if it really happened (`AGENTS.md` rule 10).

## 6. Plain cron or launchd

**cron** (uses the machine's local time; set the times in *your* timezone):
```cron
# 09:00, 14:00, 19:00 every day
0 9,14,19 * * *  cd /path/to/your-gazette && claude -p "Run one edition of the paper in this folder. Read AGENTS.md first and follow it exactly. Start with python3 scripts/fetch.py." >> hunts/cron.log 2>&1
```
Swap `claude -p` for `codex exec`, or any agent CLI that takes a prompt.

**launchd** (macOS; runs late if the Mac was asleep, unlike cron): create `~/Library/LaunchAgents/com.you.gazette.plist` with `ProgramArguments` = `/bin/zsh -lc "cd /path/to/your-gazette && claude -p '…'"` and a `StartCalendarInterval` array of `{Hour: 9, Minute: 0}`, `{Hour: 14, Minute: 0}`, `{Hour: 19, Minute: 0}`. Then run `launchctl load` on it.

## 7. Fetch.ai uAgents

uAgents gives you a long-running Python agent with timers. A small uAgent can act as the scheduler and hand each run to an agent CLI. This is a sketch; adapt it to your uAgents version:

```python
# scheduler_agent.py  (pip install uagents)
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
from uagents import Agent, Context

PAPER = "/path/to/your-gazette"
TZ = ZoneInfo("Asia/Kolkata")          # same as gazette.config.json
RUN_AT = {(9, 0), (14, 0), (19, 0)}
PROMPT = ("Run one edition of the paper in this folder. Read AGENTS.md first "
          "and follow it exactly. Start with python3 scripts/fetch.py.")

agent = Agent(name="gazette-scheduler")
last = {"key": None}

@agent.on_interval(period=60.0)
async def tick(ctx: Context):
    now = datetime.now(TZ)
    key = (now.date(), now.hour, now.minute)
    if (now.hour, now.minute) in RUN_AT and last["key"] != key:
        last["key"] = key
        ctx.logger.info("starting edition run")
        subprocess.Popen(["claude", "-p", PROMPT], cwd=PAPER)   # or ["codex", "exec", PROMPT]

if __name__ == "__main__":
    agent.run()
```
To have a uAgent *be* the newsroom instead of a scheduler, give it an LLM and tools that can read and write the folder and run the four scripts, and give it `AGENTS.md` as its instructions.

## 8. Notifications

`AGENTS.md` tells the editor to ping the owner with 2–3 sentences after a shipped edition. How the ping arrives depends on your agent: the chat itself, a desktop notification, email, Telegram and so on. Configure that in your agent, and describe it in `gazette.config.json` → `agent.ping`.

## 9. Keeping a public copy (optional)

There is no hosting in this kit. If you ever want to share a copy, run:
```bash
python3 scripts/build.py --public && python3 scripts/check.py --public
```
and share `out-public/` however you like. It contains no project stories, no private boxes and no private wire lines, and the check fails if any private marker slips through.
