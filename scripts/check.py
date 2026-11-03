#!/usr/bin/env python3
"""check.py — the gate every edition must pass before it ships.

    python3 scripts/check.py                 # checks data/ and out/
    python3 scripts/check.py --public        # checks data/ and out-public/, plus the privacy scan
    python3 scripts/check.py --site DIR      # check a specific built folder

Exit code 0 = ship. Anything else = fix and rerun. Never ship on a failure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402


CORRECTION_NOTE = re.compile(r'<p class="correction">.*?</p>', re.S)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append(a[key])


class Report:
    def __init__(self):
        self.rows: list[tuple[str, int, list[str]]] = []

    def add(self, name: str, problems: list[str]):
        self.rows.append((name, len(problems), problems))

    def ok(self) -> bool:
        return all(n == 0 for _, n, _ in self.rows)

    def print(self):
        for name, n, problems in self.rows:
            mark = "ok  " if n == 0 else "FAIL"
            print(f"[{mark}] {name}: {n}")
            for p in problems[:15]:
                print(f"         - {p}")
            if len(problems) > 15:
                print(f"         … and {len(problems) - 15} more")


def check_data(cfg: dict, cat: dict, rep: Report) -> None:
    stories = cat.get("stories", [])
    by_id = {s["id"]: s for s in stories}
    sections = {s["key"] for s in cfg["beats"]["sections"]}
    threads = {t["key"] for t in cfg["beats"].get("threads", [])}

    problems = []
    for s in stories:
        sid = s.get("id", "?")
        for field in ("id", "headline", "section", "status", "date"):
            if not s.get(field):
                problems.append(f"{sid}: missing {field}")
        if s.get("section") not in sections:
            problems.append(f"{sid}: unknown section {s.get('section')!r}")
        for t in s.get("threads", []):
            if t not in threads:
                problems.append(f"{sid}: unknown thread {t!r}")
        if s.get("status") not in C.ALL_STATUSES:
            problems.append(f"{sid}: bad status {s.get('status')!r}")
        if s.get("status") != "archive" and s.get("what_happened") and len(s["what_happened"]) != 2:
            problems.append(f"{sid}: what_happened should be exactly 2 lines")
        if s.get("what_happened") and not s.get("why_it_matters"):
            problems.append(f"{sid}: has a page but no why_it_matters")
        if s.get("status") != "archive" and not s.get("sources"):
            problems.append(f"{sid}: live story with no sources")
        for src in s.get("sources", []):
            st = (src.get("status") or "").upper()
            if st and st not in C.FACT_STATUSES:
                problems.append(f"{sid}: source status {st!r} is not one of {', '.join(C.FACT_STATUSES)}")
            if not src.get("url"):
                problems.append(f"{sid}: source without url")
        strike = s.get("strike")
        if strike is not None and not (1 <= strike <= 10):
            problems.append(f"{sid}: strike must be 1–10")
    leads = [s["id"] for s in stories if s.get("status") == "lead"]
    expected = [cat["lead"]] if cat.get("lead") else []
    if leads != expected:
        problems.append(f"stories.json → lead is {cat.get('lead')!r} but stories with status \"lead\" are {leads} "
                        "(there must be exactly one, and they must match)")
    live = [s for s in stories if s.get("status") != "archive"]
    if live and not cat.get("lead"):
        problems.append("stories.json → lead is empty but there are live stories; pick a lead")
    rep.add("story records", problems)

    one_way, missing = [], []
    for s in stories:
        for r in s.get("related", []):
            if r not in by_id:
                missing.append(f"{s['id']} -> {r} (no such story)")
            elif s["id"] not in by_id[r].get("related", []):
                one_way.append(f"{s['id']} -> {r}")
    rep.add("related links pointing at missing stories", missing)
    rep.add("one-way related links", one_way)

    chains = []
    for ch in cat.get("chains", []):
        for i in ch.get("ids", []):
            if i not in by_id:
                chains.append(f"chain {ch.get('name')!r}: {i} is not a story")
    rep.add("chain entries", chains)

    pages = [s["id"] for s in stories if s.get("status") != "archive" and not s.get("what_happened")
             and s.get("status") in ("lead", "confirmed")]
    rep.add("live lead/confirmed stories without a page (add what_happened)", pages)

    bodies = C.DATA / "bodies"
    tags = []
    for p in sorted(bodies.glob("*.html")) if bodies.exists() else []:
        tags += [f"{p.name}: {x}" for x in C.private_tag_problems(p.read_text(encoding="utf-8"))]
    rep.add("unbalanced <!-- private --> blocks in bodies", tags)

    orphans = [p.name for p in bodies.glob("*.html") if p.stem not in by_id] if bodies.exists() else []
    rep.add("body files with no story record", orphans)


def check_site(site: Path, rep: Report) -> None:
    html_files = sorted(site.rglob("*.html"))
    if not html_files:
        rep.add(f"built pages in {site}", [f"nothing built in {site} — run scripts/build.py first"])
        return
    ids_by_file: dict[Path, set] = {}
    refs_by_file: dict[Path, list] = {}
    for f in html_files:
        p = Links()
        p.feed(f.read_text(encoding="utf-8"))
        ids_by_file[f.resolve()] = p.ids
        refs_by_file[f] = p.refs
    broken, anchors, absolute = [], [], []
    total = 0
    for f, refs in refs_by_file.items():
        for ref in refs:
            parts = urlsplit(ref)
            if parts.scheme in ("http", "https", "mailto", "data", "javascript"):
                continue
            if parts.scheme or ref.startswith("//"):
                continue
            total += 1
            if ref.startswith("/"):
                absolute.append(f"{f.relative_to(site)}: {ref} (use relative links so file:// works)")
                continue
            target = (f.parent / unquote(parts.path)).resolve() if parts.path else f.resolve()
            if not target.exists():
                broken.append(f"{f.relative_to(site)}: {ref}")
                continue
            if parts.fragment and target.suffix == ".html":
                ids = ids_by_file.get(target)
                if ids is not None and parts.fragment not in ids:
                    anchors.append(f"{f.relative_to(site)}: {ref}")
    rep.add(f"broken local links (of {total} checked, {len(html_files)} pages)", broken)
    rep.add("missing #anchors", anchors)
    rep.add("absolute local links", absolute)

    gaps = []
    for f in html_files:
        m = re.search(r"\{\{\w+\}\}", f.read_text(encoding="utf-8"))
        if m:
            gaps.append(f"{f.relative_to(site)}: {m.group(0)}")
    rep.add("unfilled template placeholders", gaps)

    js = site / "assets" / "catalog.js"
    data = site / "data" / "stories.json"
    mismatch = []
    if js.exists() and data.exists():
        body = js.read_text(encoding="utf-8").strip()
        body = body[body.index("=") + 1:].rstrip(";").strip()
        if json.loads(body) != json.loads(data.read_text(encoding="utf-8")):
            mismatch.append("assets/catalog.js != data/stories.json")
    else:
        mismatch.append("catalog.js or data/stories.json missing")
    rep.add("catalog mirror", mismatch)


def check_corrections(site: Path, rep: Report) -> None:
    corr = C.load_json(C.DATA / "corrections.json", {"do_not_reintroduce": []}).get("do_not_reintroduce", [])
    hits = []
    for item in corr:
        phrase = item["wrong"] if isinstance(item, dict) else item
        for f in site.rglob("*.html"):
            # the correction notice itself may quote the old wording; everything else may not
            text = CORRECTION_NOTE.sub("", f.read_text(encoding="utf-8"))
            if phrase.lower() in text.lower():
                hits.append(f"{f.relative_to(site)}: corrected wording came back: {phrase!r}")
    rep.add("corrected wording reintroduced", hits)


def check_privacy(cfg: dict, site: Path, rep: Report) -> None:
    markers = C.private_markers(cfg)
    hits = []
    for f in sorted(site.rglob("*")):
        if not f.is_file() or f.suffix not in (".html", ".js", ".json"):  # styles.css legitimately names .for-you
            continue
        text = f.read_text(encoding="utf-8").lower()
        for m in markers:
            if m.lower() in text:
                hits.append(f"{f.relative_to(site)}: contains {m!r}")
        if C.PRIVATE_TAG.search(text):
            hits.append(f"{f.relative_to(site)}: contains a private-block tag (something private was not stripped)")
    rep.add(f"private markers in public output ({', '.join(markers)})", hits)


def check_runs(rep: Report) -> None:
    runs = C.load_json(C.DATA / "runs.json", {"runs": []}).get("runs", [])
    problems = []
    for r in runs:
        if r.get("status") == "quiet" and r.get("sources_attempted"):
            if r.get("sources_ok", 0) / r["sources_attempted"] < 0.5:
                problems.append(f"run {r.get('id')}: marked quiet but most sources failed — it was a failed run")
    cfg = C.load_config()
    stale = C.now(cfg) - timedelta(hours=12)
    for r in runs:
        started = C.parse_dt(r.get("started"))
        if r.get("status") == "open" and started and started < stale:
            problems.append(f"run {r.get('id')} has been open for over 12 h; close it or "
                            f"mark it: python3 scripts/runlog.py abandon --run {r.get('id')}")
    rep.add("run log", problems)


def main() -> None:
    ap = argparse.ArgumentParser(description="Check data and the built site before shipping.")
    ap.add_argument("--public", action="store_true", help="also scan for private project content")
    ap.add_argument("--site", help="built folder to check (default out/ or out-public/)")
    args = ap.parse_args()
    cfg = C.load_config()
    cat = C.load_json(C.DATA / "stories.json")
    site = Path(args.site) if args.site else C.ROOT / ("out-public" if args.public else "out")

    rep = Report()
    check_data(cfg, cat, rep)
    check_site(site, rep)
    check_corrections(site, rep)
    check_runs(rep)
    if args.public:
        check_privacy(cfg, site, rep)
    rep.print()
    if rep.ok():
        print("\nPASS — safe to ship.")
        sys.exit(0)
    print("\nFAIL — do not ship. Fix the items above, rebuild, and rerun the check.")
    sys.exit(1)


if __name__ == "__main__":
    main()
