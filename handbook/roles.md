# Roles

Roles are hats. One agent can wear all of them, which is the simplest setup. Or you can split them across several agents and sessions, as in the original paper this kit came from: an editor, a reporter and an explainer writer, plus a coordinator.

Names come from `gazette.config.json` → `agent.roles`.

| Role | Does | Never does |
|---|---|---|
| **Editor** | Owns the run. Writes and edits stories, builds, checks, ships, closes the run, keeps `notes/`, applies corrections, pings the owner. **The only role that edits `data/` and `notes/`.** Signs stories with `agent.byline`. | Ships a quiet run. Ships on a failing check. Claims a ping or sync that didn't happen. |
| **Reporter** | Runs `fetch.py`, hunts and verifies, writes `hunts/<run>/RESULT.md`, makes the SHIP/QUIET call, fact-checks explainers and old stories, owns the watchlist. | Edits `data/` or writes HTML. |
| **Explainer** | Drafts Learn explainers in plain language. | Publishes directly or skips the reporter's fact check. |
| **Owner** | Reads, saves, decides. Final say on anything public, paid or undecided. | — |

## Handoffs

```
schedule ─▶ editor ─(window + watchlist)─▶ reporter ─(RESULT.md + SHIP/QUIET + top 3)─▶ editor
explainer ─(draft)─▶ reporter ─(line-by-line verdicts)─▶ editor ─▶ published
reporter ─(wrong line + fix + source)─▶ editor ─▶ correction (skills/gazette-write §7)
editor ─(2–3 sentences, only when shipped)─▶ owner
owner ─("save X for me")─▶ editor ─▶ gazette.config.json → saves.agent_saved
```

## Outside agents and contributors

Don't edit `data/` or `notes/`. Hand tips, corrections and drafts to the editor as:

```
TIP: <one line> · STATUS · <primary url> · checked <time tz>
CORRECTION: <story-id> · wrong: "<exact words>" · right: "<fix>" · <primary url>
DRAFT: <path to a markdown or HTML draft> · claims to verify: <list>
```
