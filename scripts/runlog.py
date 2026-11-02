#!/usr/bin/env python3
"""runlog.py — close the run that fetch.py opened, and keep the seen-store current.

    python3 scripts/runlog.py close --status shipped --top-strike 8 --note "Lead: ..."
    python3 scripts/runlog.py close --status quiet   --top-strike 5 --note "Nothing at 7+"
    python3 scripts/runlog.py close --status failed  --note "Most feeds timed out"
    python3 scripts/runlog.py seen                   # re-sync data/seen.json from stories.json
    python3 scripts/runlog.py last                   # print the last run record

Rules it enforces:
  * a run where most sources failed cannot be closed as "quiet" (it is "failed");
  * on "shipped", every story source URL goes into data/seen.json, so the next
    fetch drops it; entries older than policy.seen_ttl_days are pruned.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402


def sync_seen(cfg: dict) -> tuple[int, int]:
    cat = C.load_json(C.DATA / "stories.json")
    store = C.load_json(C.DATA / "seen.json", {"items": []})
    by_url = {e["url"]: e for e in store["items"]}
    stamp = C.now(cfg).isoformat()
    added = 0
    for s in cat.get("stories", []):
        for src in s.get("sources", []):
            url = C.canonical_url(src.get("url", ""))
            if url and url not in by_url:
                by_url[url] = {"url": url, "title": src.get("title", ""), "story_id": s["id"], "first_seen": stamp}
                added += 1
    cutoff = C.ttl_cutoff(cfg)
    live_ids = {s["id"] for s in cat.get("stories", []) if s.get("status") != "archive"}
    kept = [e for e in by_url.values()
            if e.get("story_id") in live_ids or (C.parse_dt(e.get("first_seen")) or cutoff) >= cutoff]
    pruned = len(by_url) - len(kept)
    store["items"] = sorted(kept, key=lambda e: e.get("first_seen", ""), reverse=True)
    C.save_json(C.DATA / "seen.json", store)
    return added, pruned


def main() -> None:
    ap = argparse.ArgumentParser(description="Close runs and maintain the seen-store.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("close", help="close the open run")
    c.add_argument("--status", required=True, choices=("shipped", "quiet", "failed"))
    c.add_argument("--top-strike", type=int, help="highest strike found this run (1–10)")
    c.add_argument("--edition", type=int, help="edition number shipped (status shipped)")
    c.add_argument("--hunt", help="path to this run's hunts/<time>/RESULT.md")
    c.add_argument("--note", default="", help="one line: lead, or why it was quiet/failed")
    sub.add_parser("seen", help="sync data/seen.json from stories.json")
    sub.add_parser("last", help="print the last run")
    args = ap.parse_args()
    cfg = C.load_config()

    if args.cmd == "seen":
        added, pruned = sync_seen(cfg)
        print(f"seen.json: +{added} urls, pruned {pruned}")
        return

    runs = C.load_json(C.DATA / "runs.json", {"runs": []})
    if args.cmd == "last":
        print(json.dumps(runs["runs"][-1] if runs["runs"] else {}, indent=2, ensure_ascii=False))
        return

    open_runs = [r for r in runs["runs"] if r.get("status") == "open"]
    if not open_runs:
        C.die("no open run — start every run with scripts/fetch.py")
    run = open_runs[-1]
    att, ok = run.get("sources_attempted", 0), run.get("sources_ok", 0)
    if args.status == "quiet" and att and ok / att < 0.5:
        C.die(f"{ok}/{att} sources worked — that is a failed run, not a quiet one. Close it with --status failed.")
    threshold = int(cfg["policy"].get("strike_threshold", 7))
    if args.status == "shipped" and args.top_strike is not None and args.top_strike < threshold:
        C.die(f"top strike {args.top_strike} is below the ship threshold {threshold}. Close as quiet instead.")
    if args.status == "quiet" and args.top_strike is not None and args.top_strike >= threshold:
        print(f"note: top strike {args.top_strike} meets the threshold — are you sure this is quiet?", file=sys.stderr)

    run.update({
        "status": args.status,
        "closed": C.now(cfg).isoformat(),
        "top_strike": args.top_strike,
        "edition": args.edition,
        "hunt": args.hunt,
        "note": args.note,
    })
    C.save_json(C.DATA / "runs.json", runs)
    print(f"run {run['id']} closed as {args.status}")
    if args.status == "shipped":
        added, pruned = sync_seen(cfg)
        print(f"seen.json: +{added} urls, pruned {pruned}")


if __name__ == "__main__":
    main()
