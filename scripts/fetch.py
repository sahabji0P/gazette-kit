#!/usr/bin/env python3
"""fetch.py — step one of every run: collect the feeds before the agent reads anything.

    python3 scripts/fetch.py                    # since the last run (or the last 24 h)
    python3 scripts/fetch.py --hours 36         # explicit window
    python3 scripts/fetch.py --since 2026-11-02T09:00:00+05:30

It reads sources.feeds from gazette.config.json, fetches every RSS/Atom feed,
canonicalises URLs, drops items already covered (data/seen.json), flags likely
duplicates by title, and writes data/snapshots/<run-id>.json. It also opens a
run record in data/runs.json with per-source health, so a run where the feeds
failed can never be mistaken for a quiet news day.

Feeds with "type": "page" are not fetched; they are listed under "manual" for the
agent to visit by hand (pages without a feed, X accounts, changelogs).
"""
from __future__ import annotations

import argparse
import gzip
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

ATOM = "{http://www.w3.org/2005/Atom}"
UA = "gazette-kit/1.0 (+https://github.com/) feed reader"


def text(el, tag):
    found = el.find(tag)
    return (found.text or "").strip() if found is not None and found.text else ""


def parse_date(value: str):
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return C.parse_dt(value)


def parse_feed(raw: bytes) -> list[dict]:
    root = ET.fromstring(raw)
    items = []
    if root.tag == f"{ATOM}feed":
        for e in root.findall(f"{ATOM}entry"):
            link = ""
            for l in e.findall(f"{ATOM}link"):
                if l.get("rel", "alternate") == "alternate":
                    link = l.get("href", "")
                    break
            items.append({
                "title": text(e, f"{ATOM}title"),
                "url": link,
                "published": text(e, f"{ATOM}published") or text(e, f"{ATOM}updated"),
                "summary": text(e, f"{ATOM}summary")[:400],
            })
    else:  # RSS 2.0 / RDF
        for it in root.iter():
            if it.tag.split("}")[-1] != "item":
                continue
            def get(name, it=it):
                for c in it:
                    if c.tag.split("}")[-1] == name and c.text:
                        return c.text.strip()
                return ""
            items.append({
                "title": get("title"),
                "url": get("link"),
                "published": get("pubDate") or get("date"),
                "summary": get("description")[:400],
            })
    return items


def fetch(url: str, timeout: int) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (urls come from the owner's config)
        raw = r.read(5_000_000)
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.lstrip(b"\xef\xbb\xbf \t\r\n")


def fetch_entries(url: str, timeout: int) -> list[dict]:
    """Fetch and parse, retrying once: feeds fail transiently more often than you'd think."""
    try:
        return parse_feed(fetch(url, timeout))
    except Exception:
        time.sleep(2)
        return parse_feed(fetch(url, timeout))


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect feeds into a dated snapshot and open a run record.")
    ap.add_argument("--since", help="ISO time; default = start of the last closed run, else --hours ago")
    ap.add_argument("--hours", type=float, default=24.0, help="window when there is no previous run (default 24)")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--max-per-source", type=int, help="cap new items kept per feed (default policy.max_items_per_source, else 40)")
    args = ap.parse_args()

    cfg = C.load_config()
    started = C.now(cfg)
    runs = C.load_json(C.DATA / "runs.json", {"runs": []})
    closed = [r for r in runs["runs"] if r.get("status") in ("shipped", "quiet")]
    if args.since:
        since = C.parse_dt(args.since)
        if not since:
            C.die(f"--since is not an ISO time: {args.since}")
    elif closed and not any(a.startswith("--hours") for a in sys.argv[1:]):
        since = C.parse_dt(closed[-1]["started"])
    else:
        since = started - timedelta(hours=args.hours)

    seen = C.load_json(C.DATA / "seen.json", {"items": []})["items"]
    seen_urls = {e["url"]: e for e in seen}
    seen_titles = [(C.title_tokens(e.get("title", "")), e) for e in seen if e.get("title")]
    threshold = float(cfg["policy"].get("title_dupe_threshold", 0.6))

    cap = args.max_per_source or int(cfg["policy"].get("max_items_per_source", 40))
    sources, manual, items, by_url = [], [], [], {}
    for feed in cfg["sources"].get("feeds", []):
        if feed.get("type") == "page":
            manual.append({k: feed.get(k) for k in ("id", "name", "url", "tier", "note") if feed.get(k)})
            continue
        rec = {"id": feed["id"], "name": feed.get("name", feed["id"]), "url": feed["url"], "tier": feed.get("tier", 2)}
        try:
            entries = fetch_entries(feed["url"], args.timeout)
            rec.update(ok=True, items_total=len(entries))
        except Exception as e:  # network, HTTP, XML — record it, never hide it
            rec.update(ok=False, error=f"{type(e).__name__}: {e}"[:200], items_total=0)
            sources.append(rec)
            continue
        fresh = dropped = 0
        entries.sort(key=lambda e: -(parse_date(e["published"]).timestamp() if parse_date(e["published"]) else 0))
        for en in entries:
            url = C.canonical_url(en["url"])
            if not url:
                continue
            dt = parse_date(en["published"])
            if dt and dt < since:
                continue
            if url in by_url:
                by_url[url]["also_in"].append(feed["id"])
                continue
            if fresh >= cap:  # newest first, so the cap drops the oldest
                dropped += 1
                continue
            item = {
                "source": feed["id"], "tier": rec["tier"], "title": en["title"], "url": url,
                "published": dt.astimezone(C.tz(cfg)).isoformat() if dt else None,
                "summary": en["summary"], "also_in": [],
            }
            if url in seen_urls:
                item["seen"] = seen_urls[url].get("story_id") or True
            else:
                toks = C.title_tokens(en["title"])
                best = max(((C.jaccard(toks, t), e) for t, e in seen_titles), default=(0.0, None), key=lambda x: x[0])
                if best[0] >= threshold:
                    item["possible_dupe_of"] = best[1].get("story_id") or best[1]["url"]
            by_url[url] = item
            items.append(item)
            fresh += 1
        rec["items_in_window"] = fresh
        rec["items_over_cap"] = dropped
        sources.append(rec)

    items.sort(key=lambda i: (i.get("tier", 2), -(C.parse_dt(i["published"]).timestamp() if i.get("published") else 0)))
    run_id = started.strftime("%Y-%m-%d-%H%M")
    taken = {r.get("id") for r in runs["runs"]}
    n = 2
    while run_id in taken:  # never overwrite an earlier run record
        run_id = f"{started.strftime('%Y-%m-%d-%H%M')}-{n}"
        n += 1
    snapshot = {
        "run_id": run_id,
        "started": started.isoformat(),
        "since": since.astimezone(C.tz(cfg)).isoformat(),
        "sources": sources,
        "manual": manual,
        "items": items,
    }
    snap_path = C.DATA / "snapshots" / f"{run_id}.json"
    C.save_json(snap_path, snapshot)

    attempted = len(sources)
    ok = sum(1 for s in sources if s["ok"])
    new = sum(1 for i in items if not i.get("seen"))
    late = None
    for slot in cfg["schedule"].get("runs", []):
        hh, mm = map(int, slot["time"].split(":"))
        sched = started.replace(hour=hh, minute=mm, second=0)
        delta = (started - sched).total_seconds() / 60
        if 0 <= delta < 24 * 60 and (late is None or delta < late[1]):
            late = (slot.get("slot"), delta)
    still_open = [r["id"] for r in runs["runs"] if r.get("status") == "open"]
    runs["runs"].append({
        "id": run_id,
        "started": started.isoformat(),
        "since": snapshot["since"],
        "slot": late[0] if late else None,
        "minutes_late": round(late[1]) if late else None,
        "snapshot": str(snap_path.relative_to(C.ROOT)),
        "sources_attempted": attempted,
        "sources_ok": ok,
        "items_new": new,
        "status": "open",
    })
    C.save_json(C.DATA / "runs.json", runs)

    print(f"run id: {run_id}   (close it with: python3 scripts/runlog.py close --run {run_id} …)")
    print(f"window since {snapshot['since']}")
    if still_open:
        print(f"NOTE: other runs are still open: {', '.join(still_open)}. If one is still working, leave it alone; "
              f"if it died, mark it with: python3 scripts/runlog.py abandon --run <id>")
    print(f"sources ok {ok}/{attempted} · items in window {len(items)} · new {new} · manual checks {len(manual)}")
    for s in sources:
        if s["ok"]:
            extra = f" (+{s['items_over_cap']} older over the cap)" if s.get("items_over_cap") else ""
            print(f"  tier {s['tier']} {s['id']}: {s['items_in_window']} in window{extra}")
        else:
            print(f"  tier {s['tier']} {s['id']}: FAILED {s['error']}")
    if attempted and ok / attempted < 0.5:
        print("WARNING: most sources failed. If you stop here, close the run as 'failed', not 'quiet'.")
    limit = int(cfg["schedule"].get("late_after_minutes", 90))
    if late and late[1] > limit:
        print(f"NOTE: this run started {round(late[1])} min after the {late[0]} slot. Cover the whole window; do not backdate.")
    print(f"snapshot: {snap_path.relative_to(C.ROOT)}")


if __name__ == "__main__":
    main()
