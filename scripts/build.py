#!/usr/bin/env python3
"""build.py — lay out the paper.

Reads gazette.config.json + data/ (stories.json, glossary.json, editions.json, bodies/)
and writes a complete static site that opens from file:// with no server.

    python3 scripts/build.py                    # private build  -> out/
    python3 scripts/build.py --public           # public build   -> out-public/ (private stories removed)
    python3 scripts/build.py --out some/dir     # choose the output folder

The build never edits data/. Same input, same output.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
from common import esc  # noqa: E402

STAMP = ".gazette-build"  # marks a folder build.py made, so it is safe to replace
PRIVATE_BLOCK = re.compile(r"<!--\s*private\s*-->.*?<!--\s*/private\s*-->", re.S | re.I)


# ---------------------------------------------------------------------------
# templates

def template(name: str) -> str:
    return (C.THEME / "templates" / name).read_text(encoding="utf-8")


def fill(tpl: str, **values) -> str:
    def sub(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f"template placeholder {{{{{key}}}}} has no value")
        return str(values[key])
    return re.sub(r"\{\{(\w+)\}\}", sub, tpl)


# ---------------------------------------------------------------------------
# loading + preparing the catalog

class Paper:
    def __init__(self, public: bool):
        self.public = public
        self.cfg = C.load_config()
        self.catalog = C.load_json(C.DATA / "stories.json")
        self.glossary = C.load_json(C.DATA / "glossary.json", {"terms": []}).get("terms", [])
        self.editions = C.load_json(C.DATA / "editions.json", {"editions": []}).get("editions", [])
        self.sections = self.cfg["beats"]["sections"]
        self.threads = self.cfg["beats"].get("threads", [])
        self.tags = self.cfg["beats"].get("tags", [])
        self.sec_by_key = {s["key"]: s for s in self.sections}
        self.thread_by_key = {t["key"]: t for t in self.threads}
        self.name = self.cfg["paper"]["name"]
        self.edition_label = C.edition_label(self.cfg, self.catalog)
        self.folio = C.folio(self.cfg, self.catalog)
        self.project = C.project(self.cfg)
        self.problems: list[str] = []
        self._prepare()

    # -- data shaping --
    def _prepare(self):
        stories = self.catalog.get("stories", [])
        ids = [s.get("id") for s in stories]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            C.die(f"duplicate story ids in stories.json: {', '.join(sorted(dupes))}")
        if self.public:
            hidden = {s["id"] for s in stories if C.is_private_story(s, self.cfg)}
            stories = [s for s in stories if s["id"] not in hidden]
            for s in stories:
                s["related"] = [r for r in s.get("related", []) if r not in hidden]
                s.pop("for_you", None)
            self.catalog["chains"] = [
                {**ch, "ids": [i for i in ch.get("ids", []) if i not in hidden]} for ch in self.catalog.get("chains", [])
            ]
            self.catalog["thin_ticks"] = [t for t in self.catalog.get("thin_ticks", []) if not t.get("private")]
            self.catalog["watchlist"] = [w for w in self.catalog.get("watchlist", []) if w.get("id") not in hidden and not w.get("private")]
            if self.catalog.get("lead") in hidden:
                C.die("the lead story is private; a public build needs a public lead")
            self.hidden = hidden
        else:
            self.hidden = set()

        for s in stories:
            sec = self.sec_by_key.get(s.get("section"))
            if not sec:
                C.die(f"story {s.get('id')}: unknown section {s.get('section')!r} (see beats.sections in gazette.config.json)")
            if s.get("status") not in C.ALL_STATUSES:
                C.die(f"story {s['id']}: status must be one of {', '.join(C.ALL_STATUSES)}")
            s["section_label"] = sec["label"]
            chips = [sec.get("short", sec["label"])]
            for t in s.get("threads", []):
                th = self.thread_by_key.get(t)
                if not th:
                    C.die(f"story {s['id']}: unknown thread {t!r}")
                chips.append(th.get("chip", th["label"]))
            chips += [t for t in s.get("tags", []) if t in self.tags]
            s["categories"] = chips
            s["body_path"] = f"stories/{s['id']}.html" if s.get("what_happened") else None
        self.stories = stories
        self.by_id = {s["id"]: s for s in stories}
        lead = self.catalog.get("lead")
        if lead and lead not in self.by_id:
            C.die(f"lead {lead!r} is not a story in stories.json")

        # chains: name -> ordered ids
        self.chain_of: dict[str, list[tuple[str, list[str]]]] = {}
        for ch in self.catalog.get("chains", []):
            for i in ch.get("ids", []):
                self.chain_of.setdefault(i, []).append((ch["name"], ch["ids"]))

    def live(self):
        return [s for s in self.stories if s["status"] != "archive"]

    def taxonomy(self):
        return [s.get("short", s["label"]) for s in self.sections] + [t.get("chip", t["label"]) for t in self.threads] + self.tags

    @staticmethod
    def rank_key(s):
        return (-(s.get("strike") or 0), "".join(chr(255 - ord(c)) for c in (s.get("date") or "")))

    # -- shared fragments --
    def nav(self, root: str) -> str:
        """root is '' for top-level pages and '../' for pages inside stories/."""
        sp = "" if root else "stories/"  # path to stories/ from this page
        links = [(f"{root}index.html", "index.html", "Front")]
        for s in self.sections:
            links.append((f"{sp}section-{s['key']}.html", f"section-{s['key']}.html", s.get("short", s["label"])))
        links += [
            (f"{root}wire.html", "wire.html", "Wire"),
            (f"{sp}glossary.html", "glossary.html", "Glossary"),
            (f"{root}saved.html", "saved.html", "Saved"),
            (f"{root}archive.html", "archive.html", "Archive"),
        ]
        items = "\n".join(f'  <a href="{h}" data-nav="{d}">{esc(t)}</a>' for h, d, t in links)
        return f'<nav class="nav-bar" aria-label="Sections">\n{items}\n</nav>'

    def chips(self, s: dict, sp: str) -> str:
        """sp = path prefix to the stories/ folder from the current page."""
        sec = self.sec_by_key[s["section"]]
        out = [f'<a class="cat-chip sec-chip" href="{sp}section-{sec["key"]}.html">{esc(sec.get("short", sec["label"]))}</a>']
        for t in s.get("threads", []):
            th = self.thread_by_key[t]
            out.append(f'<a class="cat-chip thread-chip" href="{sp}thread-{th["key"]}.html">{esc(th.get("chip", th["label"]))}</a>')
        out += [f'<span class="cat-chip">{esc(t)}</span>' for t in s.get("tags", []) if t in self.tags]
        return "".join(out)

    def page(self, *, title: str, content: str, root: str = "", scripts=("nav.js", "save.js"), body_attrs: str = "") -> str:
        theme = self.cfg.get("theme", {})
        fonts = theme.get("fonts_url")
        fonts_html = (
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link href="{esc(fonts)}" rel="stylesheet">'
        ) if fonts else ""
        banner = f'<div class="sample-banner">{esc(theme["banner"])}</div>' if theme.get("banner") else ""
        tags = "\n".join(f'<script src="{root}assets/{s}"></script>' for s in scripts)
        return fill(
            template("page.html"),
            lang=esc(self.cfg["paper"].get("language", "en")),
            title=esc(title), fonts=fonts_html, root=root, body_attrs=body_attrs,
            banner=banner, content=content, scripts=tags,
        )

    def masthead(self, left: str, mid: str, tagline: str | None = None) -> str:
        p = self.cfg["paper"]
        right = " · ".join(x for x in (p.get("owner"), self.cfg["schedule"].get("timezone_label")) if x)
        return fill(
            template("masthead.html"),
            folio_left=esc(left), folio_mid=esc(mid), folio_right=esc(right),
            paper_name=esc(self.name), tagline=esc(tagline if tagline is not None else p.get("tagline", "")),
        )

    def footer(self) -> str:
        live = len(self.live())
        archived = len(self.stories) - live
        return (f'  <footer class="footer">\n    <span>{esc(self.name)} · {esc(self.edition_label)} · {live} live · {archived} archived</span>\n'
                f'    <a href="archive.html">Archive</a>\n  </footer>')

    # -- glossary auto-linking --
    def autolink(self, html_text: str, used: set, href_prefix: str) -> str:
        terms = sorted(self.glossary, key=lambda t: -len(t.get("match", t["term"])))
        if not terms:
            return html_text
        parts = re.split(r"(<[^>]+>)", html_text)
        depth = 0  # inside <a>, <code>, <pre>, <h1-3>
        blockers = re.compile(r"^<(/?)(a|code|pre|h1|h2|h3)\b", re.I)
        out = []
        for part in parts:
            if part.startswith("<"):
                m = blockers.match(part)
                if m:
                    depth += -1 if m.group(1) else 1
                    depth = max(depth, 0)
                out.append(part)
                continue
            if depth or not part.strip():
                out.append(part)
                continue
            # segments: (text, linkable). New links are not linkable, so terms never nest.
            segs = [(part, True)]
            for t in terms:
                if t["id"] in used:
                    continue
                words = [t.get("match", t["term"])] + t.get("aliases", [])
                pat = re.compile(r"(?<![\w-])(" + "|".join(re.escape(w) for w in words) + r")(?![\w-])", re.I)
                for i, (text, ok) in enumerate(segs):
                    m = pat.search(text) if ok else None
                    if not m:
                        continue
                    link = f'<a class="gl" href="{href_prefix}glossary.html#{esc(t["id"])}" title="Glossary: {esc(t["term"])}">{m.group(1)}</a>'
                    segs[i:i + 1] = [(text[: m.start()], True), (link, False), (text[m.end():], True)]
                    used.add(t["id"])
                    break
            out.append("".join(text for text, _ in segs))
        return "".join(out)

    # -----------------------------------------------------------------------
    # pages

    def front(self) -> str:
        cat = self.catalog
        lead = self.by_id.get(cat.get("lead"))
        live = [s for s in self.live() if s.get("front", True)]
        shown = set()
        blocks = []

        tape = cat.get("tape") or []
        if tape:
            label = self.cfg.get("theme", {}).get("tape_label", "Tape")
            chips = "".join(f'<span class="mkt-chip" role="listitem"><span class="n">{esc(t["name"])}</span> <span class="p">{esc(t["value"])}</span></span>' for t in tape)
            blocks.append(f'  <div class="markets markets-tape quiet-tape" role="list" aria-label="Tape">\n    <span class="tape-label">{esc(label)}</span>{chips}\n  </div>')

        grid = ['  <div class="front-grid front-grid-v3">']
        if lead:
            shown.add(lead["id"])
            wh = " ".join(lead.get("what_happened", []))
            chip = f" · {esc(lead['status_chip'])}" if lead.get("status_chip") else ""
            grid.append(f'''    <article data-story-id="{esc(lead['id'])}" class="lead-story">
      <p class="kicker">Lead{chip} · {esc(lead['section_label'])} · {esc(C.short_date(lead.get('date')))}</p>
      <h2 class="hed"><a href="reader.html?id={esc(lead['id'])}">{esc(lead['headline'])}</a></h2>
      <dl class="lead-summary">
        <dt>What happened</dt><dd>{esc(wh)}</dd>
        <dt>Why it matters</dt><dd>{esc(lead.get('why_it_matters', ''))}</dd>
      </dl>
      <div class="card-foot"><div class="cat-row">{self.chips(lead, 'stories/')}</div><div class="story-actions"><a class="jump" href="reader.html?id={esc(lead['id'])}">Read the story →</a></div></div>
    </article>''')

        per = int(self.cfg["policy"].get("front_per_section", 5))
        grid.append('    <div class="sections-grid">')
        strips = []
        for sec in self.sections:
            layout = sec.get("front", "grid")
            items = sorted([s for s in live if s["section"] == sec["key"] and s["id"] not in shown and s["status"] != "rumor"], key=self.rank_key)
            if layout == "hidden" or not items:
                continue
            total = sum(1 for s in self.stories if s["section"] == sec["key"])
            if layout == "strip":
                links = " · ".join(f'<a href="reader.html?id={esc(s["id"])}">{esc(s["headline"])}</a>' for s in items[:per])
                shown.update(s["id"] for s in items[:per])
                strips.append(f'  <section class="people-strip" id="sec-{esc(sec["key"])}" aria-label="{esc(sec["label"])}">\n'
                              f'    <span class="strip-label"><a href="stories/section-{esc(sec["key"])}.html">{esc(sec.get("short", sec["label"]))}</a></span> {links}\n  </section>')
                continue
            cards = []
            for s in items[:per]:
                shown.add(s["id"])
                href = f"reader.html?id={esc(s['id'])}" if s["body_path"] else f"stories/section-{esc(sec['key'])}.html"
                punch = (s.get("what_happened") or [s.get("dek", "")])[0]
                cards.append(f'''      <article class="front-card" data-story-id="{esc(s['id'])}">
        <h3 class="hed"><a href="{href}">{esc(s['headline'])}</a></h3>
        <p class="punch">{esc(punch)}</p>
        <div class="card-foot"><div class="cat-row">{self.chips(s, 'stories/')}</div><div class="story-actions"></div></div>
      </article>''')
            grid.append(f'''    <section class="front-section" id="sec-{esc(sec['key'])}">
      <header class="sec-head"><h2><a href="stories/section-{esc(sec['key'])}.html">{esc(sec['label'])}</a></h2><span class="sec-blurb">{esc(sec.get('blurb', ''))}</span></header>
{chr(10).join(cards)}
      <a class="sec-more" href="stories/section-{esc(sec['key'])}.html">All {total} in {esc(sec['label'])} →</a>
    </section>''')
        grid.append("    </div>\n  </div>")
        blocks.append("\n".join(grid))
        blocks += strips

        if self.threads:
            tl = " · ".join(f'<a href="stories/thread-{esc(t["key"])}.html">{esc(t["label"])}</a>' for t in self.threads)
            blocks.append(f'  <p class="section-label">Threads · <span class="thread-links">{tl} · <a href="stories/glossary.html">Glossary</a></span></p>')

        ticks = []
        for t in cat.get("thin_ticks", []):
            ticks.append(f'<div class="tick thin-tick"><span class="tick-tag">{esc(t.get("tag", "Wire"))}</span><a href="{esc(t.get("href", "wire.html"))}">{esc(t["text"])}</a></div>')
        for s in sorted([s for s in live if s["id"] not in shown], key=self.rank_key):
            href = f"reader.html?id={esc(s['id'])}" if s["body_path"] else f"stories/section-{esc(s['section'])}.html"
            ticks.append(f'<div class="tick"><span class="tick-tag">{esc(self.sec_by_key[s["section"]].get("short"))}</span><a href="{href}">{esc(s["headline"])}</a></div>')
        if ticks:
            blocks.append('  <p class="section-label">More live stories · one line each</p>\n'
                          f'  <div class="ticker-rail" tabindex="0" aria-label="More live stories"><div class="ticker-track">{"".join(ticks)}</div></div>')

        flash = cat.get("flash")
        flash_html = f'  <p class="flash">{esc(flash)}</p>\n' if flash else ""
        content = ('<div class="wrap front-page front-v3">\n'
                   + self.masthead(self.edition_label, self.folio) + "\n"
                   + self.nav("") + "\n" + flash_html
                   + "\n\n".join(blocks) + "\n" + self.footer() + "\n</div>")
        title = f"{self.folio or self.edition_label} — {self.name}"
        return self.page(title=title, content=content, scripts=("nav.js", "save.js"))

    def story_page(self, s: dict) -> str:
        used: set = set()
        sec = self.sec_by_key[s["section"]]
        status = C.STATUS_LABEL[s["status"]]
        if s.get("status_chip"):
            status += f" · {s['status_chip']}"
        kicker = " · ".join(x for x in (sec["label"], status, C.short_date(s.get("date"))) if x)
        if s.get("fold_date") and s.get("fold_date") != s.get("date"):
            kicker += " · Catch-up"

        wh = "\n".join(f'<p class="wh-line">{self.autolink(esc(line), used, "")}</p>' for line in s.get("what_happened", []))
        why = f'<p>{self.autolink(esc(s.get("why_it_matters", "")), used, "")}</p>'

        body_file = C.DATA / "bodies" / f"{s['id']}.html"
        body = ""
        if body_file.exists():
            raw = body_file.read_text(encoding="utf-8")
            bad = C.private_tag_problems(raw)
            if bad:
                C.die(f"data/bodies/{s['id']}.html: " + "; ".join(bad) + " (an unclosed private block would leak into a public build)")
            if self.public:
                raw = PRIVATE_BLOCK.sub("", raw)
            body = '<h2 class="tpl-h">Details</h2>\n<div class="story-body">\n' + self.autolink(raw.strip(), used, "") + "\n</div>"

        take = ""
        if s.get("take"):
            take = f'<div class="why-box take-box"><h2>{esc(self.cfg["agent"].get("take_label", "Our take"))}</h2>\n<p>{esc(s["take"])}</p>\n</div>'
        try_box = ""
        if s.get("try"):
            items = "".join(f"<li>{esc(x)}</li>" for x in s["try"])
            try_box = f'<div class="learn-box"><h2>What to learn / try</h2>\n<ul>{items}</ul>\n</div>'
        for_you = ""
        if s.get("for_you") and not self.public:
            label = f"For you ({self.project.get('name')})" if self.project.get("name") else "For you"
            items = "".join(f"<li>{esc(x)}</li>" for x in s["for_you"])
            for_you = f'<div class="learn-box for-you"><h2>{esc(label)}</h2>\n<ul>{items}</ul>\n</div>'

        receipts = self.receipts(s)
        correction = "".join(
            f'<p class="correction"><strong>Corrected {esc(c.get("date", ""))}:</strong> {esc(c.get("text", ""))}</p>'
            for c in s.get("corrections", [])
        )
        content = fill(
            template("story.html"),
            section_key=esc(sec["key"]), section_label=esc(sec["label"]), id=esc(s["id"]),
            nav=self.nav("../"), kicker=esc(kicker), headline=esc(s["headline"]), dek=esc(s.get("dek", "")),
            byline=esc(self.cfg["agent"].get("byline", "")), edition_label=esc(self.edition_label),
            chips=self.chips(s, ""),
            save_button=f'<button type="button" class="save-btn" data-save-id="{esc(s["id"])}" aria-pressed="false">Save</button>',
            correction=correction, what_happened=wh, why_it_matters=why, body=body, take=take,
            try_box=try_box, for_you=for_you, receipts=receipts, related=self.related(s), paper_name=esc(self.name),
        )
        return self.page(title=f"{s['headline']} — {self.name}", content=content, root="../")

    def receipts(self, s: dict) -> str:
        srcs = s.get("sources", [])
        if not srcs:
            return '<p class="muted">No sources listed.</p>'
        rows = []
        for src in srcs:
            status = (src.get("status") or "").upper()
            pill = f'<span class="fact-status {esc(status.lower())}">{esc(status)}</span>' if status else ""
            checked = f' <span class="muted">· checked {esc(src["checked"])}</span>' if src.get("checked") else ""
            rows.append(f'<li><a href="{esc(src["url"])}">{esc(src.get("title") or src["url"])}</a>{pill}{checked}</li>')
        return "<ul>\n" + "\n".join(rows) + "\n</ul>"

    def link_to(self, sid: str) -> str:
        t = self.by_id[sid]
        if t["body_path"]:
            return f'<a href="{esc(sid)}.html">{esc(t["headline"])}</a>'
        return f'<span>{esc(t["headline"])}</span> <span class="headline-only">headline only</span>'

    def related(self, s: dict) -> str:
        out = []
        for name, ids in self.chain_of.get(s["id"], []):
            i = ids.index(s["id"])
            prev_id = ids[i - 1] if i > 0 else None
            next_id = ids[i + 1] if i + 1 < len(ids) else None
            nav = []
            if prev_id and prev_id in self.by_id:
                nav.append(f'<a class="chain-prev" href="{esc(prev_id)}.html">← {esc(self.by_id[prev_id]["headline"])}</a>')
            if next_id and next_id in self.by_id:
                nav.append(f'<a class="chain-next" href="{esc(next_id)}.html">{esc(self.by_id[next_id]["headline"])} →</a>')
            out.append(f'<div class="chain" data-chain="{esc(name)}"><p class="chain-name">{esc(name)} · {i + 1} of {len(ids)}</p><div class="chain-nav">{"".join(nav)}</div></div>')
        rel = [r for r in s.get("related", []) if r in self.by_id]
        expl = [r for r in rel if self.by_id[r]["section"] in ("learn", "build")]
        news = [r for r in rel if r not in expl]
        if expl:
            out.append('<h3 class="rel-h">Explainers &amp; Build</h3><ul class="rel-expl">' + "".join(f"<li>{self.link_to(r)}</li>" for r in expl) + "</ul>")
        if news:
            out.append('<h3 class="rel-h">Related news</h3><ul class="rel-news">' + "".join(f"<li>{self.link_to(r)}</li>" for r in news) + "</ul>")
        extra = [f'<a href="section-{esc(s["section"])}.html">All {esc(self.sec_by_key[s["section"]]["label"])}</a>']
        extra += [f'<a href="thread-{esc(t)}.html">{esc(self.thread_by_key[t]["label"])}</a>' for t in s.get("threads", [])]
        extra.append('<a href="glossary.html">Glossary</a>')
        out.append(f'<p class="rel-threads">{" · ".join(extra)}</p>')
        return "\n".join(out)

    def list_items(self, stories: list) -> str:
        rows = []
        for s in stories:
            punch = (s.get("what_happened") or [s.get("dek", "")])[0]
            meta = f'{esc(C.short_date(s.get("date")))} · {esc(C.STATUS_LABEL[s["status"]])}'
            if s["body_path"]:
                hed = f'<a class="li-hed" href="{esc(s["id"])}.html">{esc(s["headline"])}</a>'
                meta += f' · <a class="reader-link" href="../reader.html?id={esc(s["id"])}">split reader</a>'
            else:
                hed = f'<span class="li-hed">{esc(s["headline"])}</span>'
                meta += ' · <span class="headline-only">headline only</span>'
            rows.append(f'<li class="list-item" data-story-id="{esc(s["id"])}">{hed}<p class="li-punch">{esc(punch)}</p><span class="li-meta">{meta}</span></li>')
        return '<ul class="story-list">' + "".join(rows) + "</ul>"

    def list_page(self, *, page_id: str, title: str, dek: str, stories: list, others: str) -> str:
        live = sorted([s for s in stories if s["status"] != "archive"], key=self.rank_key)
        arch = sorted([s for s in stories if s["status"] == "archive"], key=lambda s: s.get("date") or "", reverse=True)
        parts = [
            f'<div class="story-page list-page" id="{esc(page_id)}">',
            '  <nav class="crumbs" aria-label="Breadcrumb"><a class="crumb-front" href="../index.html">← Front page</a><span class="sep">·</span><a href="glossary.html">Glossary</a></nav>',
            self.nav("../"),
            f'  <p class="kicker">{esc(self.name)} · {esc(self.edition_label)}</p>',
            f'  <h1 class="hed">{esc(title)}</h1>',
            f'  <p class="dek">{esc(dek)}</p>',
            f'  <p class="sec-others">{others}</p>',
            f'  <h2 class="list-h">Live now <span class="count">{len(live)}</span></h2>{self.list_items(live) if live else "<p class=muted>Nothing live right now.</p>"}',
        ]
        if arch:
            parts.append(f'  <h2 class="list-h">Archived <span class="count">{len(arch)}</span></h2>{self.list_items(arch)}')
        parts.append(f'  <footer class="footer story-foot"><span><a href="../index.html">← Front page</a> · <a href="glossary.html">Glossary</a></span><span>{esc(self.name)} · {esc(self.edition_label)}</span></footer>')
        parts.append("</div>")
        return self.page(title=f"{title} — {self.name}", content="\n".join(parts), root="../", scripts=("nav.js",))

    def section_pages(self) -> dict:
        pages = {}
        for sec in self.sections:
            others = "Other sections: " + " · ".join(
                f'<a href="section-{esc(o["key"])}.html">{esc(o["label"])}</a>' for o in self.sections if o["key"] != sec["key"])
            pages[f"stories/section-{sec['key']}.html"] = self.list_page(
                page_id=f"section-{sec['key']}", title=sec["label"], dek=sec.get("blurb", ""),
                stories=[s for s in self.stories if s["section"] == sec["key"]], others=others)
        for th in self.threads:
            others = "Other threads: " + " · ".join(
                f'<a href="thread-{esc(o["key"])}.html">{esc(o["label"])}</a>' for o in self.threads if o["key"] != th["key"])
            pages[f"stories/thread-{th['key']}.html"] = self.list_page(
                page_id=f"thread-{th['key']}", title=th["label"], dek=th.get("blurb", "A thread across sections."),
                stories=[s for s in self.stories if th["key"] in s.get("threads", [])], others=others)
        return pages

    def glossary_page(self) -> str:
        entries = []
        for t in sorted(self.glossary, key=lambda t: t["term"].lower()):
            src = f'<span class="gl-src">{esc(t["source"])}</span>' if t.get("source") else ""
            entries.append(f'<div class="gl-entry" id="{esc(t["id"])}"><dt>{esc(t["term"])}</dt><dd>{esc(t["definition"])}{src}</dd></div>')
        content = "\n".join([
            '<div class="story-page list-page" id="glossary">',
            '  <nav class="crumbs" aria-label="Breadcrumb"><a class="crumb-front" href="../index.html">← Front page</a></nav>',
            self.nav("../"),
            f'  <p class="kicker">{esc(self.name)} · Glossary</p>',
            '  <h1 class="hed">Glossary</h1>',
            '  <p class="dek">Plain-language definitions. Story pages link the first mention of each term here.</p>',
            '  <dl class="gloss gl-list">' + "".join(entries) + "</dl>",
            f'  <footer class="footer story-foot"><span><a href="../index.html">← Front page</a></span><span>{esc(self.name)} · {esc(self.edition_label)}</span></footer>',
            "</div>",
        ])
        return self.page(title=f"Glossary — {self.name}", content=content, root="../", scripts=("nav.js",))

    def desk(self, *, title: str, mid: str, tagline: str, body: str, scripts=("nav.js", "save.js")) -> str:
        content = ('<div class="wrap front-page">\n' + self.masthead(title, mid, tagline) + "\n" + self.nav("")
                   + "\n" + body + "\n" + self.footer() + "\n</div>")
        return self.page(title=f"{title} — {self.name}", content=content, scripts=scripts)

    def wire_page(self) -> str:
        bands = []
        cat = self.catalog
        rumors = [s for s in self.live() if s["status"] == "rumor"]
        ticks = cat.get("thin_ticks", [])
        if ticks or rumors:
            lis = [f'<li><strong>{esc(t.get("tag", "Wire"))}</strong> {esc(t["text"])}</li>' for t in ticks]
            lis += [f'<li><strong>RUMOR</strong> <a href="reader.html?id={esc(s["id"])}">{esc(s["headline"])}</a></li>' if s["body_path"]
                    else f'<li><strong>RUMOR</strong> {esc(s["headline"])}</li>' for s in rumors]
            bands.append(f'<section class="desk-band">\n  <p class="section-label">Thin ticks &amp; rumor mill</p>\n  <ul class="desk-list">{"".join(lis)}</ul>\n</section>')
        watch = cat.get("watchlist", [])
        if watch:
            lis = "".join(f'<li><strong>{esc(w.get("label") or w.get("id"))}</strong> {esc(w.get("note", ""))}</li>' for w in watch)
            bands.append(f'<section class="desk-band">\n  <p class="section-label">Watchlist</p>\n  <ul class="desk-list">{lis}</ul>\n</section>')
        for ed in self.editions:
            lines = []
            for line in ed.get("wire", []):
                if isinstance(line, dict):
                    if self.public and line.get("private"):
                        continue
                    line = line.get("text", "")
                lines.append(f"<li>{esc(line)}</li>")
            label = f'Wire · {ed.get("folio", "")} · Vol. {self.cfg["edition"].get("volume", 1)} No. {ed.get("number", "?")}'
            bands.append(f'<section class="desk-band">\n  <p class="section-label">{esc(label)}</p>\n  <ul class="desk-list">{"".join(lines)}</ul>\n</section>')
        if not bands:
            bands.append('<p class="muted">The wire is empty.</p>')
        return self.desk(title="Wire", mid=self.edition_label, tagline="Thin ticks, rumors, the watchlist and every edition's log", body="\n".join(bands))

    def build_desk(self) -> str:
        build_sec = self.sec_by_key.get("build")
        ideas = sorted([s for s in self.stories if s["section"] == "build" and s["status"] != "archive"], key=self.rank_key) if build_sec else []
        cards = []
        for s in ideas:
            badge = "Suggestion" + (f" · {self.project.get('name')}" if C.is_private_story(s, self.cfg) and self.project.get("name") else "")
            href = f"reader.html?id={esc(s['id'])}" if s["body_path"] else f"stories/section-build.html"
            punch = (s.get("what_happened") or [s.get("dek", "")])[0]
            cards.append(f'<article class="idea-card" data-story-id="{esc(s["id"])}"><span class="badge">{esc(badge)}</span>'
                         f'<h3><a href="{href}">{esc(s["headline"])}</a></h3><p>{esc(punch)}</p>'
                         f'<div class="card-foot"><div class="cat-row">{self.chips(s, "stories/")}</div><div class="story-actions"></div></div></article>')
        body = "\n".join(cards) or '<p class="muted">No build ideas yet.</p>'
        label = self.project.get("label") if (self.project.get("enabled") and not self.public) else "Build"
        return self.desk(title=label or "Build", mid=self.edition_label, tagline="Ideas to try the same day — suggestions, not news", body=body)

    def archive_page(self) -> str:
        arch = sorted([s for s in self.stories if s["status"] == "archive"],
                      key=lambda s: (s.get("cooled_in") or 0, s.get("date") or ""), reverse=True)
        cards = []
        for s in arch:
            sec = self.sec_by_key[s["section"]]
            href = f"reader.html?id={esc(s['id'])}" if s["body_path"] else f"stories/section-{esc(sec['key'])}.html"
            note = f"Cooled to archive in No.{s['cooled_in']}. " if s.get("cooled_in") else ""
            cards.append(f'    <article class="archive-card">\n      <p class="kicker">{esc(sec.get("short", sec["label"]))} · cooled</p>\n'
                         f'      <h3 class="hed"><a href="{href}">{esc(s["headline"])}</a></h3>\n'
                         f'      <p class="dek">{esc(note)}Story kept; still on its section page.</p>\n    </article>')
        body = '<div class="archive-list">\n' + ("\n".join(cards) or '<p class="muted">Nothing archived yet.</p>') + "\n</div>"
        return self.desk(title="Archive", mid=f"{len(arch)} stories", tagline="Older stories, newest cooled first — never deleted", body=body, scripts=("nav.js",))

    def saved_page(self) -> str:
        body = ('  <p class="section-label">Saved · <span id="saved-count">0</span></p>\n'
                '  <div id="saved-filter" class="cat-row" aria-label="Filter by category"></div>\n'
                '  <div id="saved-grid" class="saved-grid"></div>\n'
                '  <p id="saved-empty" class="saved-empty hidden">Nothing saved yet. Open a story and hit Save.</p>')
        return self.desk(title="Saved shelf", mid="Local to this browser", tagline="Your saved stories · tap Save again to remove",
                         body=body, scripts=("catalog.js", "save.js", "nav.js", "saved.js"))

    def reader_page(self) -> str:
        desks = "".join(f'<a href="{h}">{t}</a>' for h, t in
                        (("index.html", "Front"), ("wire.html", "Wire"), ("build.html", "Build"), ("archive.html", "Archive"), ("saved.html", "Saved")))
        content = fill(template("reader.html"), paper_name=esc(self.name), desk_links=desks)
        return self.page(title=f"Reading — {self.name}", content=content,
                         scripts=("catalog.js", "save.js", "reader.js"), body_attrs=' class="app-shell reader-mode"')

    # -----------------------------------------------------------------------

    def public_catalog(self) -> dict:
        keep = ("id", "headline", "dek", "section", "section_label", "categories", "threads", "tags", "status", "status_chip",
                "strike", "front", "date", "fold_date", "what_happened", "why_it_matters", "related", "sources", "body_path", "cooled_in")
        return {
            "paper": self.name,
            "edition_label": self.edition_label,
            "edition": self.catalog.get("edition", {}),
            "folio": self.folio,
            "lead": self.catalog.get("lead"),
            "flash": self.catalog.get("flash"),
            "taxonomy": self.taxonomy(),
            "sections": [{**s, "page": f"stories/section-{s['key']}.html"} for s in self.sections],
            "threads": [{**t, "page": f"stories/thread-{t['key']}.html"} for t in self.threads],
            "glossary": "stories/glossary.html",
            "stories": [{k: s[k] for k in keep if k in s} for s in self.stories],
        }

    def build(self, out: Path) -> int:
        files: dict[str, str] = {
            "index.html": self.front(),
            "reader.html": self.reader_page(),
            "wire.html": self.wire_page(),
            "build.html": self.build_desk(),
            "archive.html": self.archive_page(),
            "saved.html": self.saved_page(),
            "stories/glossary.html": self.glossary_page(),
        }
        files.update(self.section_pages())
        for s in self.stories:
            if s["body_path"]:
                files[s["body_path"]] = self.story_page(s)

        cat = self.public_catalog()
        cat_json = json.dumps(cat, ensure_ascii=False, indent=2)
        site = {
            "name": self.name,
            "slug": self.cfg["paper"].get("slug", "gazette"),
            "agentSaved": [i for i in self.cfg.get("saves", {}).get("agent_saved", []) if i in self.by_id],
        }
        files["assets/catalog.js"] = f"window.GAZETTE_CATALOG = {cat_json};\n"
        files["assets/site.js"] = f"window.GAZETTE_SITE = {json.dumps(site, ensure_ascii=False)};\n"
        files["data/stories.json"] = cat_json + "\n"

        if out.exists():
            if not (out / STAMP).exists() and any(out.iterdir()):
                C.die(f"refusing to replace {out}: no {STAMP} file")
            shutil.rmtree(out)
        files[STAMP] = ("This folder is generated by scripts/build.py and is replaced on every build.\n"
                        "Do not keep your own files here.\n")
        for rel, text in files.items():
            p = out / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        for asset in ("styles.css", "nav.js", "save.js", "reader.js", "saved.js"):
            shutil.copy2(C.THEME / asset, out / "assets" / asset)
        return len(files)


def main() -> None:
    ap = argparse.ArgumentParser(description="Lay out the paper from data/ into a static site.")
    ap.add_argument("--public", action="store_true", help="drop private project stories and private blocks")
    ap.add_argument("--out", help="output folder (default out/ or out-public/)")
    args = ap.parse_args()
    out = Path(args.out) if args.out else C.ROOT / ("out-public" if args.public else "out")
    target = out.resolve()
    protected = [C.ROOT.resolve()] + [(C.ROOT / d).resolve() for d in
                 ("data", "theme", "scripts", "skills", "handbook", "notes", "hunts", "examples", "extras")]
    if target in protected or C.ROOT.resolve().is_relative_to(target):
        C.die(f"refusing to build into {target}: it is (or contains) part of the kit")
    if target.exists() and not target.is_dir():
        C.die(f"refusing to build into {target}: it is a file")
    if target.exists() and any(target.iterdir()) and not (target / STAMP).exists():
        C.die(f"refusing to replace {target}: it is not empty and was not made by build.py "
              f"(no {STAMP} file). Pick another folder, or empty it yourself.")
    paper = Paper(public=args.public)
    n = paper.build(out)
    mode = "public" if args.public else "private"
    print(f"built {mode} edition {paper.edition_label} ({paper.folio}): {n} files, "
          f"{len(paper.live())} live, {len(paper.stories) - len(paper.live())} archived -> {out}")
    print(f"open: {out / 'index.html'}")


if __name__ == "__main__":
    main()
