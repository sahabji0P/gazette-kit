"""Shared helpers for gazette-kit scripts. Python 3.9+, standard library only."""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
THEME = ROOT / "theme"
CONFIG_PATH = ROOT / "gazette.config.json"

LIVE_STATUSES = ("lead", "confirmed", "brief", "rumor")
ALL_STATUSES = LIVE_STATUSES + ("archive",)
STATUS_LABEL = {
    "lead": "Lead",
    "confirmed": "Confirmed",
    "brief": "Brief",
    "rumor": "Rumor",
    "archive": "Archived",
}
FACT_STATUSES = ("CONFIRMED", "VENDOR-REPORTED", "RUMOR", "UNVERIFIED")


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def load_json(path: Path, default=None):
    path = Path(path)
    if not path.exists():
        if default is not None:
            return default
        die(f"missing file: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{path.name}: invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}")


def save_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_config() -> dict:
    cfg = load_json(CONFIG_PATH)
    missing = [k for k in ("paper", "agent", "schedule", "edition", "beats", "sources", "policy") if k not in cfg]
    if missing:
        die(f"gazette.config.json is missing: {', '.join(missing)}")
    if not cfg["beats"].get("sections"):
        die("gazette.config.json: beats.sections must list at least one section")
    try:
        ZoneInfo(cfg["schedule"]["timezone"])
    except Exception:
        die(f"gazette.config.json: unknown timezone {cfg['schedule'].get('timezone')!r}")
    cfg.setdefault("project", {"enabled": False})
    cfg.setdefault("saves", {"agent_saved": []})
    cfg.setdefault("theme", {})
    return cfg


def tz(cfg: dict) -> ZoneInfo:
    return ZoneInfo(cfg["schedule"]["timezone"])


def now(cfg: dict) -> datetime:
    return datetime.now(tz(cfg)).replace(microsecond=0)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


# ---- dedupe helpers -------------------------------------------------------

TRACKING_PARAMS = re.compile(r"^(utm_.*|fbclid|gclid|mc_cid|mc_eid|ref|ref_src|source|igshid|si)$", re.I)


def canonical_url(url: str) -> str:
    """Normalise a URL so the same article fetched twice compares equal."""
    if not url:
        return ""
    parts = urlsplit(url.strip())
    scheme = "https" if parts.scheme in ("http", "https") else parts.scheme
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":443") or host.endswith(":80"):
        host = host.rsplit(":", 1)[0]
    path = re.sub(r"/+$", "", parts.path) or "/"
    query = urlencode(sorted((k, v) for k, v in parse_qsl(parts.query) if not TRACKING_PARAMS.match(k)))
    return urlunsplit((scheme, host, path, query, ""))


STOPWORDS = set("a an the and or of to in on for with by at from is are was were be its it this that as new".split())


def title_tokens(title: str) -> set[str]:
    words = re.findall(r"[a-z0-9][a-z0-9.\-]*", (title or "").lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ---- catalog helpers ------------------------------------------------------

def project(cfg: dict) -> dict:
    return cfg.get("project") or {}


def is_private_story(story: dict, cfg: dict) -> bool:
    if story.get("private"):
        return True
    p = project(cfg)
    prefix = p.get("id_prefix")
    return bool(p.get("enabled") and p.get("private", True) and prefix and story.get("id", "").startswith(prefix))


def private_markers(cfg: dict) -> list[str]:
    p = project(cfg)
    markers = list(p.get("private_markers") or [])
    if p.get("enabled") and p.get("private", True):
        if p.get("name"):
            markers.append(p["name"])
        if p.get("id_prefix"):
            markers.append(p["id_prefix"])
    markers.append("for-you")  # the CSS class of the private box; must never reach a public build
    seen, out = set(), []
    for m in markers:
        if m and m.lower() not in seen:
            seen.add(m.lower())
            out.append(m)
    return out


def edition_label(cfg: dict, catalog: dict) -> str:
    ed = catalog.get("edition") or {}
    return f"Vol. {cfg['edition'].get('volume', 1)}, No. {ed.get('number', 1)}"


def folio(cfg: dict, catalog: dict) -> str:
    ed = catalog.get("edition") or {}
    dt = parse_dt(ed.get("published"))
    if not dt:
        return ""
    dt = dt.astimezone(tz(cfg))
    slot = ed.get("slot") or ""
    text = f"{dt.strftime('%A')} · {dt.day} {dt.strftime('%B %Y')}"
    return f"{text} · {slot}" if slot else text


def short_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        d = datetime.strptime(value[:10], "%Y-%m-%d")
    except ValueError:
        return value
    return f"{d.day} {d.strftime('%b %Y')}"


def ttl_cutoff(cfg: dict) -> datetime:
    days = int(cfg["policy"].get("seen_ttl_days", 45))
    return now(cfg) - timedelta(days=days)
