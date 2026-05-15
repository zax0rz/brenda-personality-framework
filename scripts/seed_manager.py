#!/usr/bin/env python3
"""
Seed Manager — Creative pipeline seed lifecycle management.

Generic, config-driven version. No hardcoded paths or agent-specific naming.
Point at your YAML config and go.

Commands:
  extract   Scan journal entries for seeds and add to seed file
  review    Present incubating seeds older than min_age for activation decision
  archive   Move rejected seeds to archive file
  activate  Promote a seed to active status with chosen medium
  stats     Show seed counts, age distribution, rejection rate
  validate  Validate config and verify all configured paths exist

Config file (YAML):
  workspace: /path/to/agent/workspace
  journal_dir: journal/
  seed_dir: seeds/
  draft_dir: drafts/
  archive_dir: archive/
  personality_file: PERSONALITY.md
  voice_file: VOICE.md
  timezone: "America/New_York"
  api:
    base_url: "https://api.example.com/v1"
    model: "model-name"
    api_key_env: API_KEY

Seed lifecycle:
  1. extract  — seeds pulled from journal entries, status='incubating'
  2. review   — seeds that have incubated >= min_incubation_hours are shown
  3. activate or archive — reviewer decides fate

Dependencies: Python 3.9+, pyyaml. Zero other external deps.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Any, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Defaults and constants
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = "pipeline-config.yaml"
MIN_INCUBATION_HOURS = 24
STALE_HOURS = 96


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: str) -> dict:
    """Load and validate the YAML configuration file."""
    path = Path(config_path).expanduser().resolve()
    if not path.exists():
        print(f"ERROR: Config file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict):
        print("ERROR: Config file must contain a YAML mapping (top-level dict)", file=sys.stderr)
        sys.exit(1)

    if "workspace" not in cfg:
        print("ERROR: Config must include 'workspace' path", file=sys.stderr)
        sys.exit(1)

    return cfg


def resolve_config_path(cfg: dict, key: str, default: str = "") -> Path:
    """
    Resolve a config path relative to workspace.
    If the path is already absolute, use it as-is.
    """
    workspace = Path(cfg["workspace"]).expanduser().resolve()
    raw = cfg.get(key, default)
    p = Path(raw).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (workspace / p).resolve()


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def get_timezone(cfg: dict) -> ZoneInfo:
    """Return ZoneInfo object from config, defaulting to UTC."""
    tz_name = cfg.get("timezone", "UTC")
    try:
        return ZoneInfo(tz_name)
    except (KeyError, TypeError):
        print(f"WARNING: Unknown timezone '{tz_name}', falling back to UTC", file=sys.stderr)
        return ZoneInfo("UTC")


def _now(cfg: dict) -> str:
    """ISO-formatted current time in the configured timezone."""
    tz = get_timezone(cfg)
    return datetime.now(tz).isoformat()


def _hours_ago(ts: str, cfg: dict) -> float:
    """Hours since a timestamp string, in configured timezone."""
    dt = datetime.fromisoformat(ts)
    tz = get_timezone(cfg)
    return (datetime.now(tz) - dt).total_seconds() / 3600


# ---------------------------------------------------------------------------
# Section name helpers — "brewing" section is configurable
# ---------------------------------------------------------------------------

def get_seed_section_name(cfg: dict) -> str:
    """Return the journal section name used for secondary seed extraction (e.g. 'brewing', 'seeds', 'impulses')."""
    return cfg.get("seed_section", "brewing")


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def seeds_dir(cfg: dict) -> Path:
    return resolve_config_path(cfg, "seed_dir", "seeds")


def archive_dir(cfg: dict) -> Path:
    return resolve_config_path(cfg, "archive_dir", "archive")


def seeds_file(cfg: dict) -> Path:
    return seeds_dir(cfg) / "creative-seeds.json"


def archive_file(cfg: dict) -> Path:
    return archive_dir(cfg) / "creative-seeds-archive.json"


def journal_dir(cfg: dict) -> Path:
    return resolve_config_path(cfg, "journal_dir", "journal")


def _load_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _save_json(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _seed_id(text: str, source_path: str) -> str:
    """Deterministic ID from seed text + source."""
    raw = f"{text}:{source_path}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Prose extraction helpers
# ---------------------------------------------------------------------------

# Patterns that indicate seed-like content in prose
_PROSE_PATTERNS = [
    # "What if" / "Imagine" openings
    (re.compile(r"^(?:what if|imagine)[\s,]", re.IGNORECASE), 0.85),
    # "The [noun] of [noun]" metaphor pattern
    (re.compile(r"^the\s+\w+\s+of\s+\w+", re.IGNORECASE), 0.80),
    # Vivid metaphor/analogy markers
    (re.compile(r"\b(?:like|as if|feels? like|smells? like|sounds? like|tastes? like)\b", re.IGNORECASE), 0.70),
    # Sensory description — color/texture/light/sound words in clusters
    (re.compile(r"\b(?:glow|glint|shimmer|haze|shadow|echo|silence|static|pulse|hum)\b", re.IGNORECASE), 0.65),
    # Emotional insight / reflection markers
    (re.compile(r"\b(?:i\s+(?:don'?t\s+know|wonder|carry|hold|feel|remember|forget|need|want))\b", re.IGNORECASE), 0.60),
    # Vivid visual fragments — short lines with strong imagery
    (re.compile(r"\b(?:neon|rust|chrome|dust|glass|bone|ash|smoke|rain|fog|amber|crimson|gold)\b", re.IGNORECASE), 0.55),
    # Abstract philosophical fragments
    (re.compile(r"\b(?:maybe|perhaps|somewhere|somehow|always|never|nothing|everything)\s+(?:that|this|we|they|it|he|she)\b", re.IGNORECASE), 0.55),
]

# Lines that are definitely NOT seeds
_NOISE_PREFIXES = re.compile(
    r"^(?:---\s*$|##\s|\*\s|\d+\.\s|\[\S+\]\(\S+\)|\[\^|!\[|>\s|```|\|\s)",
    re.IGNORECASE,
)

# Lines that are pure narration/transitions — skip these
_NARRATION_VERBS = ("said|told|walked|went|came|looked|sat|stood|nodded|smiled|frowned|laughed|cried|sighed|woke|fell|dropped|picked|put|got|took|turned|opened|closed|ran|drove")
_NARRATION_PATTERN = re.compile(
    r"^(?:he|she)\s+(?:" + _NARRATION_VERBS + r")"
    r"|i\s+(?:woke|went|came|walked|drove|sat|stood|left|got|picked|put|took|turned|opened|closed|read|wrote|called|texted|checked)"
    r"|zach\s+(?:said|told|found|showed|asked|told|left|came|went|called)"
    r"|we\s+(?:went|came|sat|stood|walked|drove|talked|ate|drank|left|met)"
    r"|they\s+(?:went|came|sat|stood|walked|left)",
    re.IGNORECASE,
)


def _score_line(line: str) -> float:
    """
    Heuristic confidence score for a single line being a seed.
    Returns 0.0–1.0. Lines scoring < 0.6 are discarded.
    """
    stripped = line.strip()

    # Length gate: seeds are short fragments (20–200 chars)
    if len(stripped) < 20 or len(stripped) > 200:
        return 0.0

    # Skip noise lines
    if _NOISE_PREFIXES.match(stripped):
        return 0.0

    # Skip pure narration
    if _NARRATION_PATTERN.match(stripped):
        return 0.0

    # Skip lines that are mostly whitespace or very short on content
    words = stripped.split()
    if len(words) < 4:
        return 0.0

    # Score: take the highest pattern match
    best = 0.0
    for pattern, base_score in _PROSE_PATTERNS:
        if pattern.search(stripped):
            best = max(best, base_score)

    if best == 0.0:
        return 0.0

    # Boost: lines that end with ellipsis or em-dash feel more seed-like
    if stripped.endswith("...") or stripped.endswith("…") or stripped.endswith("—"):
        best = min(1.0, best + 0.05)

    # Boost: lines containing a question mark
    if "?" in stripped:
        best = min(1.0, best + 0.05)

    # Penalty: very long lines (150+) are probably prose, not seeds
    if len(stripped) > 150:
        best = max(0.0, best - 0.1)

    return round(best, 2)


def _parse_journal_md_entries(content: str) -> list[tuple[str, str]]:
    """
    Parse a journal.md file that contains inline entries separated by ---
    and/or links to external journal files.

    Returns list of (date_label, body_text) tuples.
    """
    entries = []
    lines = content.split("\n")
    current_body: list[str] = []
    current_date = ""

    i = 0
    while i < len(lines):
        line = lines[i]

        # Match date headers like "## 2026-04-29" or "## April 29, 2026"
        date_match = re.match(r"^##\s+(\d{4}-\d{2}-\d{2}(?:\s+.*)?)", line)
        if date_match:
            # Flush previous entry
            if current_body:
                entries.append((current_date, "\n".join(current_body).strip()))
                current_body = []
            current_date = date_match.group(1).strip()
            i += 1
            continue

        # Match separator --- (but not frontmatter delimiters at top)
        if line.strip() == "---" and current_body:
            entries.append((current_date, "\n".join(current_body).strip()))
            current_body = []
            i += 1
            continue

        # Match external links: [text](memory/journal/filename.md)
        link_match = re.match(r"^\s*\[([^\]]*)\]\((memory/journal/[^)]+\.md)\)", line)
        if link_match:
            # This is a reference to an external file, skip it here
            # The external file will be processed separately via journal_dir glob
            i += 1
            continue

        current_body.append(line)
        i += 1

    # Flush last entry
    if current_body:
        entries.append((current_date, "\n".join(current_body).strip()))

    return entries


def _extract_prose_seeds(body_text: str, source_path: str) -> list[dict]:
    """
    Scan a journal entry's body text for seed-like fragments.
    Returns a list of seed dicts (no id, no timestamps — caller fills those).
    """
    seeds = []
    seen_texts: set[str] = set()

    for line in body_text.split("\n"):
        confidence = _score_line(line)
        if confidence < 0.6:
            continue

        text = line.strip()
        # Deduplicate within same entry
        if text in seen_texts:
            continue
        seen_texts.add(text)

        seeds.append({
            "text": text,
            "extraction_confidence": confidence,
        })

    return seeds


def _make_seed_dict(text: str, source_type: str, source_path: str,
                     emotional_tags: list[str], color: list[str] | None,
                     sound: str, threads: list[str], now_fn,
                     confidence: float | None = None) -> dict:
    """Build a seed dict. Shared by all three extraction methods."""
    seed = {
        "id": _seed_id(text, source_path),
        "text": text,
        "created_at": now_fn(),
        "source_type": source_type,
        "source_path": source_path,
        "emotional_tags": emotional_tags,
        "color": color or [],
        "sound": sound,
        "threads": threads,
        "status": "incubating",
        "incubation_start": now_fn(),
        "activation_date": None,
        "archive_reason": None,
        "medium_approaches": None,
        "selected_medium": None,
        "output_path": None,
        "synthesis_source_entries": [],
        "personality_alignment": None,
    }
    if confidence is not None:
        seed["extraction_confidence"] = confidence
    return seed


# ---------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------

def extract(cfg: dict, dry_run: bool = False, source: str = "all") -> dict:
    """
    Scan journal entries for seeds from three sources:
    1. Frontmatter `seed:` field (primary)
    2. Configurable section — e.g. `brewing`, `seeds`, `impulses` (secondary)
    3. Raw journal text for seed-like fragments (tertiary, heuristic)

    Args:
        cfg: Pipeline config dict.
        dry_run: If True, don't write to seed file.
        source: Which extraction methods to use. One of:
            "all" — try all three methods
            "frontmatter" — only YAML frontmatter seed: field
            "brewing" — only the configurable section (brewing/seeds/impulses)
            "prose" — only body text heuristics
    """
    seeds = _load_json(seeds_file(cfg))
    existing_ids = {s["id"] for s in seeds}
    new_seeds = []
    section_name = get_seed_section_name(cfg)
    jdir = journal_dir(cfg)
    now_fn = lambda: _now(cfg)  # noqa: E731

    if not jdir.exists():
        return {"error": f"Journal directory not found: {jdir}"}

    valid_sources = {"all", "frontmatter", "brewing", "prose"}
    if source not in valid_sources:
        return {"error": f"Invalid --source '{source}'. Must be one of: {', '.join(sorted(valid_sources))}"}

    use_frontmatter = source in ("all", "frontmatter")
    use_brewing = source in ("all", "brewing")
    use_prose = source in ("all", "prose")

    for journal_file in sorted(jdir.glob("*.md")):
        content = journal_file.read_text()
        lines = content.split("\n")

        # Parse frontmatter
        fm = {}
        in_fm = False
        fm_lines = []
        for line in lines:
            if line.strip() == "---":
                if in_fm:
                    break
                in_fm = True
                continue
            if in_fm:
                fm_lines.append(line)

        for fl in fm_lines:
            if ":" in fl:
                key, _, val = fl.partition(":")
                fm[key.strip()] = val.strip().strip('"\'').strip("[]")

        # Compute body text (everything after frontmatter)
        body_start = 0
        fm_count = 0
        for idx, line in enumerate(lines):
            if line.strip() == "---":
                fm_count += 1
                if fm_count == 2:
                    body_start = idx + 1
                    break
        body_text = "\n".join(lines[body_start:]).strip()

        source_path = f"{jdir.name}/{journal_file.name}"

        # Source 1: frontmatter seed field
        if use_frontmatter and "seed" in fm and fm["seed"]:
            sid = _seed_id(fm["seed"], journal_file.name)
            if sid not in existing_ids:
                seed = _make_seed_dict(
                    text=fm["seed"],
                    source_type="journal_frontmatter",
                    source_path=source_path,
                    emotional_tags=fm.get("mood", "").split(","),
                    color=fm.get("color", []),
                    sound=fm.get("sound", ""),
                    threads=fm.get("threads", "").split(","),
                    now_fn=now_fn,
                )
                new_seeds.append(seed)
                existing_ids.add(sid)

        # Source 2: configurable section (e.g. "brewing", "seeds", "impulses")
        if use_brewing:
            section_lines = []
            in_section = False
            section_header = f"## {section_name}"
            for line in lines:
                if line.strip().lower().startswith(section_header.lower()):
                    in_section = True
                    continue
                if in_section and line.strip().startswith("## "):
                    break
                if in_section and line.strip():
                    section_lines.append(line)

            if section_lines:
                section_text = "\n".join(section_lines).strip()
                if len(section_text) > 20:
                    for fragment in section_text.split("\n\n"):
                        fragment = fragment.strip().strip("*").strip()
                        if 15 < len(fragment) < 300:
                            sid = _seed_id(fragment, journal_file.name)
                            if sid not in existing_ids:
                                seed = _make_seed_dict(
                                    text=fragment,
                                    source_type="journal_brewing",
                                    source_path=source_path,
                                    emotional_tags=fm.get("mood", "").split(","),
                                    color=fm.get("color", []),
                                    sound=fm.get("sound", ""),
                                    threads=fm.get("threads", "").split(","),
                                    now_fn=now_fn,
                                )
                                new_seeds.append(seed)
                                existing_ids.add(sid)

        # Source 3: prose heuristic extraction
        if use_prose:
            # For individual journal files, scan the body text directly
            prose_seeds = _extract_prose_seeds(body_text, source_path)
            for ps in prose_seeds:
                sid = _seed_id(ps["text"], journal_file.name)
                if sid not in existing_ids:
                    seed = _make_seed_dict(
                        text=ps["text"],
                        source_type="journal_prose",
                        source_path=source_path,
                        emotional_tags=fm.get("mood", "").split(","),
                        color=fm.get("color", []),
                        sound=fm.get("sound", ""),
                        threads=fm.get("threads", "").split(","),
                        now_fn=now_fn,
                        confidence=ps["extraction_confidence"],
                    )
                    new_seeds.append(seed)
                    existing_ids.add(sid)

            # For journal.md files, also parse inline entries
            if journal_file.name == "journal.md":
                inline_entries = _parse_journal_md_entries(content)
                for date_label, entry_body in inline_entries:
                    if not entry_body:
                        continue
                    prose_seeds = _extract_prose_seeds(entry_body, source_path)
                    for ps in prose_seeds:
                        # Use date_label in the source to disambiguate same-text seeds
                        disambig = f"{journal_file.name}:{date_label}"
                        sid = _seed_id(ps["text"], disambig)
                        if sid not in existing_ids:
                            seed = _make_seed_dict(
                                text=ps["text"],
                                source_type="journal_prose",
                                source_path=source_path,
                                emotional_tags=fm.get("mood", "").split(","),
                                color=fm.get("color", []),
                                sound=fm.get("sound", ""),
                                threads=fm.get("threads", "").split(","),
                                now_fn=now_fn,
                                confidence=ps["extraction_confidence"],
                            )
                            new_seeds.append(seed)
                            existing_ids.add(sid)

    if dry_run:
        return {"dry_run": True, "new_seeds_found": len(new_seeds), "seeds": new_seeds}

    all_seeds = seeds + new_seeds
    _save_json(seeds_file(cfg), all_seeds)

    return {
        "extracted": len(new_seeds),
        "total_seeds": len(all_seeds),
        "incubating": sum(1 for s in all_seeds if s["status"] == "incubating"),
        "active": sum(1 for s in all_seeds if s["status"] == "active"),
        "new_seeds": new_seeds,
    }


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

def review(cfg: dict) -> dict:
    """
    Present incubating seeds older than MIN_INCUBATION_HOURS for review.
    Returns seeds ready for activation decision — the caller evaluates:
    1. Is this still alive?
    2. What medium?
    3. What specific detail is yours?
    """
    seeds = _load_json(seeds_file(cfg))
    reviewable = []

    for seed in seeds:
        if seed["status"] != "incubating":
            continue
        age_hours = _hours_ago(seed["incubation_start"], cfg)
        if age_hours < MIN_INCUBATION_HOURS:
            continue
        reviewable.append({
            "id": seed["id"],
            "text": seed["text"],
            "source": seed["source_path"],
            "age_hours": round(age_hours, 1),
            "emotional_tags": seed.get("emotional_tags", []),
            "color": seed.get("color", []),
            "sound": seed.get("sound", ""),
        })

    stale = []
    for seed in seeds:
        if seed["status"] != "incubating":
            continue
        age_hours = _hours_ago(seed["incubation_start"], cfg)
        if age_hours >= STALE_HOURS:
            stale.append({
                "id": seed["id"],
                "text": seed["text"],
                "age_hours": round(age_hours, 1),
                "status": "STALE — force decision required",
            })

    # Build medium choices dynamically from config (fallback to Brenda-era defaults)
    mediums = cfg.get("mediums", ["gallery", "moltbook", "blog", "audio"])
    medium_list = " | ".join(mediums)

    return {
        "reviewable": reviewable,
        "stale": stale,
        "prompt": (
            f"For each seed above, answer three questions:\n"
            f"1. Is this still alive?\n"
            f"2. What medium? ({medium_list} | archive)\n"
            f"3. What specific detail is yours?\n\n"
            f"Return JSON array of {{id, alive: bool, medium: str, detail: str}}"
        ),
    }


# ---------------------------------------------------------------------------
# Medium Suggestion (optional — requires `openai` library)
# ---------------------------------------------------------------------------

def _try_suggest_approaches(cfg: dict, seed_text: str) -> list[dict]:
    """
    Call the API to suggest 2-3 medium approaches for a seed.
    Uses the config's suggest_model (should be a model that handles JSON well, e.g. deepseek).
    Returns empty list if openai library isn't available or API call fails.
    """
    mediums = cfg.get("mediums", ["gallery", "moltbook", "blog", "audio"])
    medium_list = json.dumps(mediums)
    suggest_model = cfg.get("api", {}).get("suggest_model", cfg.get("api", {}).get("model", "deepseek-v4-flash"))

    prompt = (
        f"You are a creative director reviewing an artist's seed idea. "
        f"Suggest 2-3 specific approaches from this medium list: {medium_list}. "
        f"For each approach, give the medium, a one-line concept, and a key question. "
        f"Be specific. Seed idea: \"{seed_text}\"\n\n"
        f"Return ONLY a JSON array of objects with fields: medium, concept, question"
    )

    try:
        from openai import OpenAI
    except ImportError:
        return []

    try:
        api_key = os.environ.get(cfg.get("api", {}).get("api_key_env", ""))
        if not api_key:
            return []
        client = OpenAI(base_url=cfg["api"]["base_url"], api_key=api_key)
        response = client.chat.completions.create(
            model=suggest_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024,
        )
        content = response.choices[0].message.content
    except Exception:
        return []

    if not content or len(content.strip()) < 10:
        return []

    # Parse JSON from response (handle markdown-wrapped JSON)
    import re
    content = content.strip()
    # Strip markdown code blocks
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
    if m:
        content = m.group(1).strip()
    try:
        import json as _json
        approaches = _json.loads(content)
        if isinstance(approaches, list):
            return approaches[:3]
    except Exception:
        pass

    return []


# ---------------------------------------------------------------------------
# Activate / Archive
# ---------------------------------------------------------------------------

def activate(cfg: dict, seed_id: str, medium: str, detail: str) -> dict:
    """Mark a seed as active with chosen medium and specific detail."""
    seeds = _load_json(seeds_file(cfg))
    for seed in seeds:
        if seed["id"] == seed_id:
            seed["status"] = "active"
            seed["activation_date"] = _now(cfg)
            seed["selected_medium"] = medium
            seed["medium_approaches"] = {"detail": detail, "approaches": []}
            _save_json(seeds_file(cfg), seeds)
            return {"activated": seed_id, "medium": medium}
    return {"error": f"Seed {seed_id} not found"}


def archive_seed(cfg: dict, seed_id: str, reason: str) -> dict:
    """Move a seed to the archive with a reason."""
    seeds = _load_json(seeds_file(cfg))
    archived = _load_json(archive_file(cfg))
    archived_ids = {s["id"] for s in archived}

    for i, seed in enumerate(seeds):
        if seed["id"] == seed_id:
            seed["status"] = "archived"
            seed["archive_reason"] = reason
            seed["archived_at"] = _now(cfg)
            if seed_id not in archived_ids:
                archived.append(seed)
            seeds.pop(i)
            _save_json(seeds_file(cfg), seeds)
            _save_json(archive_file(cfg), archived)
            return {"archived": seed_id, "reason": reason}

    return {"error": f"Seed {seed_id} not found"}


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def stats(cfg: dict) -> dict:
    """Seed counts, age distribution, rejection rate."""
    seeds = _load_json(seeds_file(cfg))
    archived = _load_json(archive_file(cfg))

    status_counts: dict[str, int] = {}
    for s in seeds:
        status_counts[s["status"]] = status_counts.get(s["status"], 0) + 1

    incubating_ages = []
    for s in seeds:
        if s["status"] == "incubating":
            incubating_ages.append(_hours_ago(s["incubation_start"], cfg))

    archive_reasons: dict[str, int] = {}
    for s in archived:
        reason = s.get("archive_reason", "unknown")
        archive_reasons[reason] = archive_reasons.get(reason, 0) + 1

    total_created = len(seeds) + len(archived)
    rejection_rate = (len(archived) / total_created * 100) if total_created > 0 else 0

    return {
        "total_seeds": len(seeds),
        "total_archived": len(archived),
        "total_created_ever": total_created,
        "rejection_rate_pct": round(rejection_rate, 1),
        "by_status": status_counts,
        "incubating_ages_hours": (
            {
                "min": round(min(incubating_ages), 1),
                "max": round(max(incubating_ages), 1),
                "avg": round(sum(incubating_ages) / len(incubating_ages), 1),
            }
            if incubating_ages
            else "none"
        ),
        "archive_reasons": archive_reasons,
        "target_rejection_pct": "70-80",
        "note": "Low publication ratio = aesthetic judgment, not failure",
    }


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

def validate(cfg: dict) -> dict:
    """
    Validate configuration and verify paths exist.
    Returns a report of what's good and what's broken.
    """
    issues: list[str] = []
    checks: dict[str, Any] = {}

    # Check workspace
    workspace = Path(cfg["workspace"]).expanduser().resolve()
    checks["workspace"] = str(workspace)
    if workspace.exists():
        checks["workspace_ok"] = True
    else:
        checks["workspace_ok"] = False
        issues.append(f"workspace does not exist: {workspace}")

    # Check timezone validity
    tz_name = cfg.get("timezone", "UTC")
    try:
        tz = ZoneInfo(tz_name)
        checks["timezone"] = tz_name
        checks["timezone_ok"] = True
    except (KeyError, TypeError):
        checks["timezone"] = tz_name
        checks["timezone_ok"] = False
        issues.append(f"unknown timezone: {tz_name}")

    # Check seed section name
    section = get_seed_section_name(cfg)
    checks["seed_section"] = section

    # Check resolved paths
    for key, label in [
        ("journal_dir", "journal directory"),
        ("seed_dir", "seed directory"),
        ("draft_dir", "draft directory"),
        ("archive_dir", "archive directory"),
    ]:
        try:
            p = resolve_config_path(cfg, key)
            checks[key] = str(p)
            if p.exists():
                checks[f"{key}_ok"] = True
            else:
                checks[f"{key}_ok"] = False
                issues.append(f"{label} does not exist: {p}")
        except Exception as e:
            checks[key] = str(e)
            checks[f"{key}_ok"] = False
            issues.append(f"cannot resolve {label}: {e}")

    # Check personality/voice files (optional — warn if missing)
    for key, label in [("personality_file", "personality file"), ("voice_file", "voice file")]:
        try:
            p = resolve_config_path(cfg, key)
            checks[key] = str(p)
            if p.exists():
                checks[f"{key}_ok"] = True
            else:
                checks[f"{key}_ok"] = False
                issues.append(f"{label} not found (optional): {p}")
        except Exception as e:
            checks[key] = str(e)
            checks[f"{key}_ok"] = False
            issues.append(f"cannot resolve {label}: {e}")

    # Check API config (optional)
    api = cfg.get("api", {})
    if api:
        checks["api_configured"] = True
        if "base_url" in api:
            checks["api_base_url"] = api["base_url"]
        if "api_key_env" in api:
            key_present = api["api_key_env"] in os.environ
            checks["api_key_env"] = api["api_key_env"]
            checks["api_key_found"] = key_present
            if not key_present:
                issues.append(f"API key env var '{api['api_key_env']}' is not set")
    else:
        checks["api_configured"] = False

    checks["valid"] = len(issues) == 0
    checks["issues"] = issues

    return checks


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_medium_choices(cfg: dict) -> list[str]:
    """Return medium choices from config, with a sensible fallback."""
    return cfg.get("mediums", ["gallery", "moltbook", "blog", "audio"])


def main():
    # Top-level args (before subcommand)
    parser = argparse.ArgumentParser(
        description="Seed Manager — Creative pipeline seed lifecycle management."
    )
    parser.add_argument(
        "--config",
        "-c",
        default=DEFAULT_CONFIG,
        help=f"Path to YAML config file (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    sub = parser.add_subparsers(dest="command", required=True)

    def _add_common_flags(sp):
        """Add --dry-run and --json flags to a subparser so they work
        after the subcommand name too (not just before it)."""
        sp.add_argument("--dry-run", action="store_true", help=argparse.SUPPRESS)
        sp.add_argument("--json", action="store_true", help=argparse.SUPPRESS)

    # extract
    p_extract = sub.add_parser("extract", help="Scan journals for new seeds")
    _add_common_flags(p_extract)
    p_extract.add_argument(
        "--source",
        default="all",
        choices=["all", "frontmatter", "brewing", "prose"],
        help=(
            "Which extraction method to use (default: all). "
            "frontmatter = YAML seed: field, "
            "brewing = configurable section, "
            "prose = body text heuristics"
        ),
    )

    # review
    p_review = sub.add_parser("review", help="Show seeds ready for activation review")
    _add_common_flags(p_review)
    p_review.add_argument(
        "--suggest",
        action="store_true",
        help="Generate AI-powered medium suggestions for each seed (requires openai lib)",
    )

    # stats
    p_stats = sub.add_parser("stats", help="Seed statistics")
    _add_common_flags(p_stats)

    # validate
    p_validate = sub.add_parser("validate", help="Validate config and check paths exist")
    _add_common_flags(p_validate)

    # archive
    p_archive = sub.add_parser("archive", help="Archive a seed")
    p_archive.add_argument("seed_id", help="Seed ID to archive")
    p_archive.add_argument("--reason", "-r", required=True, help="Archive reason")
    _add_common_flags(p_archive)

    # activate
    p_activate = sub.add_parser("activate", help="Activate a seed")
    p_activate.add_argument("seed_id", help="Seed ID to activate")
    p_activate.add_argument("--medium", "-m", required=True, help="Medium for output")
    p_activate.add_argument(
        "--detail",
        "-d",
        required=True,
        help="Specific detail that makes this yours",
    )
    _add_common_flags(p_activate)

    # Parse
    args = parser.parse_args()

    # Load config
    cfg = load_config(args.config)

    # Resolve medium choices for activate help text
    medium_choices = build_medium_choices(cfg)

    if args.command == "extract":
        result = extract(cfg, dry_run=args.dry_run, source=args.source)
    elif args.command == "review":
        result = review(cfg)
        if args.suggest:
            suggestions = {}
            for s in result.get("reviewable", []):
                approaches = _try_suggest_approaches(cfg, s["text"])
                if approaches:
                    suggestions[s["id"]] = approaches
            result["suggestions"] = suggestions
    elif args.command == "stats":
        result = stats(cfg)
    elif args.command == "validate":
        result = validate(cfg)
    elif args.command == "archive":
        result = archive_seed(cfg, args.seed_id, args.reason)
    elif args.command == "activate":
        # Validate medium against configured choices
        if args.medium not in medium_choices:
            result = {
                "error": (
                    f"Invalid medium '{args.medium}'. "
                    f"Choose from: {', '.join(medium_choices)}"
                )
            }
        else:
            result = activate(cfg, args.seed_id, args.medium, args.detail)
    else:
        result = {"error": f"Unknown command: {args.command}"}

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Human-readable output
    if args.command == "extract":
        print(f"Extracted {result.get('extracted', 0)} new seeds")
        print(f"Total: {result.get('total_seeds', 0)} | Incubating: {result.get('incubating', 0)} | Active: {result.get('active', 0)}")
        for s in result.get("new_seeds", []):
            print(f"  + [{s['source_type']}] {s['text'][:80]}")
        if "error" in result:
            print(f"\nERROR: {result['error']}", file=sys.stderr)

    elif args.command == "review":
        reviewable = result.get("reviewable", [])
        stale = result.get("stale", [])
        suggestions = result.get("suggestions", {})
        print(f"{len(reviewable)} seeds ready for review")
        for s in reviewable:
            print(f"  {s['id']} ({s['age_hours']}h) — {s['text'][:80]}")
            if suggestions and s['id'] in suggestions:
                for approach in suggestions[s['id']]:
                    medium = approach.get("medium", "?")
                    concept = approach.get("concept", "")
                    q = approach.get("question", "")
                    print(f"    → {medium}: {concept}")
                    if q:
                        print(f"      ? {q}")
        if stale:
            print(f"\n⚠ {len(stale)} STALE seeds (>{STALE_HOURS}h, force decision):")
            for s in stale:
                print(f"  {s['id']} ({s['age_hours']}h) — {s['text'][:80]}")

    elif args.command == "stats":
        r = result
        print(f"Active seeds: {r['total_seeds']} | Archived: {r['total_archived']} | Ever created: {r['total_created_ever']}")
        print(f"Rejection rate: {r['rejection_rate_pct']}% (target: {r['target_rejection_pct']}%)")
        print(f"By status: {r['by_status']}")
        if isinstance(r['incubating_ages_hours'], dict):
            a = r['incubating_ages_hours']
            print(f"Incubating ages: {a['min']}-{a['max']}h (avg {a['avg']}h)")
        if r['archive_reasons']:
            print(f"Archive reasons: {r['archive_reasons']}")

    elif args.command == "validate":
        r = result
        if r["valid"]:
            print("✓ Config is valid")
        else:
            print(f"✗ {len(r['issues'])} issue(s) found:")
            for issue in r["issues"]:
                print(f"  • {issue}")
        print()
        print("Paths:")
        for key in ["workspace", "journal_dir", "seed_dir", "draft_dir", "archive_dir"]:
            label = key.replace("_", " ").title()
            ok = r.get(f"{key}_ok", False)
            status = "✓" if ok else "✗"
            print(f"  {status} {label}: {r.get(key, '?')}")
        if r.get("personality_file"):
            ok = r.get("personality_file_ok", False)
            status = "✓" if ok else "⚠"
            print(f"  {status} Personality: {r['personality_file']}")
        if r.get("voice_file"):
            ok = r.get("voice_file_ok", False)
            status = "✓" if ok else "⚠"
            print(f"  {status} Voice: {r['voice_file']}")
        print(f"  Timezone: {r.get('timezone', '?')}")
        print(f"  Seed section: {r.get('seed_section', 'brewing')}")
        if r.get("api_configured"):
            print(f"  API: {r.get('api_base_url', '?')} (key {'found' if r.get('api_key_found') else 'not set'})")

    elif args.command in ("activate", "archive"):
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
