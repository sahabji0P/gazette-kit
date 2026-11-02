---
name: gazette-publish
description: Step 3 of a gazette run. Assembles and ships the edition — bumps the edition number and folio, sets the lead, demotes and cools old stories, runs scripts/build.py and scripts/check.py, closes the run, updates notes, and pings the owner. Use after gazette-write, or when asked to rebuild, ship or publish the paper.
---

# Publish: assemble, check, ship

You are the **editor**. Nothing ships unless `check.py` prints PASS.

## 1. Edition header (`data/stories.json`)

- `edition.number`: previous + 1. Quiet runs never bump it.
- `edition.published`: now, ISO with the owner's offset (e.g. `2026-11-02T14:10:00+05:30`).
- `edition.slot`: the slot name from `schedule.runs` that this run belongs to (morning / afternoon / evening). If the run is late, it's still that slot. Don't backdate.
- `flash`: one or two sentences in the paper's voice: "Mon afternoon: <lead in plain words>. Also: <second item>."

## 2. Lead and front

- **New lead**: set its `status` to `lead` and `catalog.lead` to its id. Add a `status_chip` if one fits.
- **Old lead**: set it to `confirmed`, remove its `status_chip`, and usually lower its strike by one (9 → 8).
- There is exactly one `lead`. `check.py` enforces it.
- **Cool** stories that are stale or pushed off by newer ones: set `status: "archive"` and `cooled_in: <this edition number>`. Never delete. The front ranks live stories by strike, then date, `policy.front_per_section` per section. The rest go to the one-line ticker.
- `"front": false` keeps a live story off the front without archiving it.
- Standing beats (`beats.standing_beats`): keep at least one live story on each near the front.

## 3. Wire entry (`data/editions.json`)

Insert at the **top** of `editions`:
```json
{ "number": N, "folio": "Monday · 2 November 2026 · afternoon",
  "wire": ["<Lead> LEAD: one line · strike N", "New: …", "Cooled: id, id",
           { "text": "Build: <project idea>", "private": true }] }
```
Mark project lines `"private": true`.

## 4. Build and check

```bash
python3 scripts/build.py
python3 scripts/check.py
```
Fix every FAIL and rerun until it prints **PASS**. Common fixes:
- one-way related → add the missing id on the other story
- story without a page → add `what_happened` and `why_it_matters`
- corrected wording came back → rewrite the sentence
- broken link → wrong id in `related` or in a body link

**Never ship on FAIL.** If you can't fix it this run, don't ship. Close the run as `failed` with the reason.

If the owner publishes a public copy anywhere (only with their explicit yes):
```bash
python3 scripts/build.py --public && python3 scripts/check.py --public
```
The privacy check must show 0 private markers.

## 5. Close the run

```bash
python3 scripts/runlog.py close --status shipped --top-strike N --edition N \
  --hunt hunts/<run>/RESULT.md --note "Lead: <id>"
```
This also adds every story source to `data/seen.json`, so the next fetch skips them.

## 6. Notes

- `notes/MEMORY.md`: add a new entry at the **top**: edition, lead, new stories, cooled, corrections, watchlist changes, open questions, anything the next run must know.
- `notes/EDITIONS.md`: one paragraph at the top: what shipped, why the lead was the lead, anything unusual about the build.

## 7. Open and ping

Open `out/index.html` if you can (e.g. `open out/index.html` on macOS). Then send the owner the ping described in `agent.ping` in the config: by default **2–3 sentences, no article paste**: the lead in plain words and the one thing worth trying. Only say you opened, synced or sent something if you actually did.

If the paper lives in git (needed for cloud-scheduled runs), commit `data/`, `notes/` and `hunts/` with a message like `edition N: <lead id>`. `out/` is rebuilt, so it isn't committed.
