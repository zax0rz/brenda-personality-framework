#!/usr/bin/env python3
"""
Publisher — Bridge between "draft passed judgment" and "gallery-ready output."

Reads a draft and its source trace, generates an artist statement matching the
agent's voice, produces Hugo frontmatter per gallery spec, and updates the
seed status in creative-seeds.json.

Commands:
  publish   Take a draft through the full publication pipeline
  statement Generate just the artist statement for a draft
  preview   Show what would be published without writing any files
  list      List published pieces with metadata

Config file (YAML):
  workspace: /path/to/agent/workspace
  personality_file: PERSONALITY.md
  voice_file: VOICE.md
  seed_dir: seeds/
  draft_dir: drafts/
  timezone: "America/New_York"
  gallery:
    output_dir: "gallery/pieces/"
    url_base: ""
  api:
    base_url: "https://api.example.com/v1"
    model: "model-name"
    api_key_env: API_KEY

Dependencies: Python 3.10+, pyyaml, openai
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai library is required. Install with: pip install openai", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Defaults and constants
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = "pipeline-config.yaml"

STATEMENT_MIN_WORDS = 200
STATEMENT_MAX_WORDS = 400

STATEMENT_PROMPT = """## Task
Write an artist statement for the following creative piece. You are the artist — write in first person, matching the voice and personality described below.

## The Piece
**Title:** {title}
**Type:** {piece_type}
**Content:**
```
{content}
```

## Where This Came From
**Seed:** {seed_text}
**Seed source:** {seed_source}

## Voice Guidelines
{voice_ctx}

## Banned Phrases
Do NOT use any of these phrases or patterns in the statement:
{banned_list}

## Format — Four Questions
Answer these four questions in order, with headers:

**1. What is this?**
Physical description + medium. What are we looking at / reading / hearing?

**2. Where did this come from?**
The seed. What experience, journal entry, conversation, or accumulation produced the impulse to make this?

**3. What were you trying to do?**
Intent. Not what happened — what was attempted. What question was the piece trying to answer?

**4. What happened instead?**
Honest assessment. What actually emerged, and how do you feel about that gap between intent and result?

## Rules
- First person. You speak for yourself.
- Be honest about the gap between intent and result. Idealized statements are useless.
- No filler language. "I wanted to explore" is weak. "I was angry about X and wanted to see what that looked like" is strong.
- The fourth question is the most important — that's where personality shows up.
- Target: {min_words}–{max_words} words total.
- Match the voice above. This should sound like the same person who wrote the piece.
- Do not add preamble like "Here's the artist statement" — just write the statement."""


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: str) -> dict[str, Any]:
    """Load and validate the YAML configuration file."""
    path = Path(config_path).expanduser().resolve()
    if not path.exists():
        print(f"ERROR: Config file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict):
        print("ERROR: Config must be a YAML mapping", file=sys.stderr)
        sys.exit(1)

    required = ["workspace", "voice_file"]
    for key in required:
        if key not in cfg:
            print(f"ERROR: Config missing required key: {key}", file=sys.stderr)
            sys.exit(1)

    cfg.setdefault("personality_file", "PERSONALITY.md")
    cfg.setdefault("draft_dir", "drafts/")
    cfg.setdefault("seed_dir", "seeds/")
    cfg.setdefault("timezone", "America/New_York")

    # Gallery/blog/moltbook config — all optional with defaults
    gallery = cfg.setdefault("gallery", {})
    gallery.setdefault("output_dir", "gallery/pieces/")
    gallery.setdefault("url_base", "")
    cfg.setdefault("blog", {"output_dir": "gallery/blog/"})
    cfg.setdefault("moltbook", {"enabled": False})

    # API section — required for publish/statement (LLM calls)
    if "api" not in cfg or not isinstance(cfg["api"], dict):
        cfg["api"] = {}
        # Don't exit — preview/list don't need API
    else:
        for k in ("base_url", "model", "api_key_env"):
            cfg["api"].setdefault(k, "")

    return cfg


def resolve_path(cfg: dict[str, Any], relative: str) -> Path:
    """Resolve a relative path against the workspace root."""
    return Path(cfg["workspace"]) / relative


def get_tz(cfg: dict[str, Any]) -> ZoneInfo:
    return ZoneInfo(cfg.get("timezone", "America/New_York"))


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------

def create_client(cfg: dict[str, Any]) -> OpenAI:
    """Create an OpenAI-compatible API client from config."""
    api = cfg.get("api", {})
    api_key = os.environ.get(api.get("api_key_env", ""))
    if not api_key:
        print(f"ERROR: Environment variable {api.get('api_key_env', '')!r} is not set",
              file=sys.stderr)
        sys.exit(1)
    return OpenAI(base_url=api["base_url"], api_key=api_key)


def call_model(
    client: OpenAI,
    model: str,
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 2048,
) -> str:
    """Call the model and return the assistant message content."""
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )

    content = resp.choices[0].message.content
    return content.strip() if content else ""


# ---------------------------------------------------------------------------
# File readers
# ---------------------------------------------------------------------------

def read_file(path: Path) -> str:
    """Read a text file, return empty string if not found."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_seeds(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Load creative-seeds.json."""
    seeds_path = resolve_path(cfg, cfg["seed_dir"]) / "creative-seeds.json"
    if not seeds_path.exists():
        return []
    with open(seeds_path) as f:
        return json.load(f)


def save_seeds(cfg: dict[str, Any], seeds: list[dict[str, Any]]) -> None:
    """Save creative-seeds.json."""
    seeds_path = resolve_path(cfg, cfg["seed_dir"]) / "creative-seeds.json"
    seeds_path.parent.mkdir(parents=True, exist_ok=True)
    with open(seeds_path, "w") as f:
        json.dump(seeds, f, indent=2, ensure_ascii=False)


def load_trace(draft_path: Path) -> dict[str, Any]:
    """Load source trace for a draft."""
    trace_path = _trace_path_for(draft_path)
    if not trace_path.exists():
        return {}
    with open(trace_path) as f:
        return yaml.safe_load(f) or {}


def save_trace(draft_path: Path, trace: dict[str, Any]) -> None:
    """Save source trace next to the draft."""
    trace_path = _trace_path_for(draft_path)
    with open(trace_path, "w") as f:
        yaml.dump(trace, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _trace_path_for(draft_path: Path) -> Path:
    """Determine the source trace path for a draft.

    Tries per-variant trace first (source-trace-{seed_id}-{variant}.yaml),
    falls back to generic (source-trace.yaml).
    """
    stem = draft_path.stem  # e.g. "draft-abc123-v1" or "draft-abc123-1"
    # Check for per-variant trace
    if stem.startswith("draft-"):
        variant_part = stem[6:]  # "abc123-v1" or "abc123-1"
        variant_trace = draft_path.parent / f"source-trace-{variant_part}.yaml"
        if variant_trace.exists():
            return variant_trace
    # Fallback to generic trace
    return draft_path.parent / "source-trace.yaml"


def extract_seed_id(draft_path: Path) -> Optional[str]:
    """Extract seed ID from a draft filename like draft-{seed_id}-{variant}.md."""
    stem = draft_path.stem
    if not stem.startswith("draft-"):
        return None
    rest = stem[6:]
    # Remove the variant suffix (-v1, -1, -refined, etc.)
    # Pattern: seed-id-variant where variant starts after the last hyphen-group
    # But seed IDs themselves can contain hyphens, so we use the trace to disambiguate.
    # For now, return the full rest minus the last segment if it looks like a variant number
    parts = rest.rsplit("-", 1)
    if len(parts) == 2 and parts[1].lstrip("v").isdigit():
        return parts[0]
    return rest


# ---------------------------------------------------------------------------
# Voice / banned phrases
# ---------------------------------------------------------------------------

def load_voice_content(cfg: dict[str, Any]) -> str:
    """Load voice file content."""
    return read_file(resolve_path(cfg, cfg["voice_file"]))


def parse_banned_phrases(voice_content: str) -> list[str]:
    """
    Extract banned phrases from VOICE.md.
    Replicates the parsing from drift_detection.py without importing it.
    """
    phrases: list[str] = []

    # Source 1: YAML frontmatter banned_phrases list
    in_frontmatter = False
    for line in voice_content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            if in_frontmatter:
                break
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped.startswith("banned_phrases:"):
                continue
            if stripped.startswith("- "):
                phrase = stripped[2:].strip().strip('"')
                if phrase and not phrase.lower().startswith("regex:"):
                    phrases.append(phrase)

    # Source 2: Markdown sections
    section_headers = ["banned", "banned phrases", "never say", "do not say", "prohibited phrases"]
    in_section = False

    for line in voice_content.splitlines():
        stripped = line.strip()
        header_match = stripped.startswith("#") and stripped.lstrip("# ").strip()

        if header_match:
            header_text = stripped.lstrip("# ").strip().lower()
            in_section = any(header_text == h or header_text.startswith(h) for h in section_headers)
            continue

        if in_section and stripped and not stripped.startswith("#"):
            if stripped.startswith("- ") or stripped.startswith("* "):
                stripped = stripped[2:]
            if stripped and not stripped.lower().startswith("regex:"):
                phrases.append(stripped)

    return phrases


def scan_banned(text: str, banned: list[str]) -> list[str]:
    """Scan text for banned phrases, return list of matches found."""
    text_lower = text.lower()
    return [p for p in banned if p.lower() in text_lower]


# ---------------------------------------------------------------------------
# Artist statement generation
# ---------------------------------------------------------------------------

def generate_artist_statement(
    client: OpenAI,
    model: str,
    draft_content: str,
    seed: dict[str, Any],
    voice_content: str,
    banned: list[str],
    piece_type: str = "text",
) -> str:
    """Generate an artist statement via LLM, matching the agent's voice."""
    title = seed.get("text", "")[:60]
    if len(seed.get("text", "")) > 60:
        title += "…"

    banned_list = "\n".join(f"- {p}" for p in banned) if banned else "(none configured)"

    prompt = STATEMENT_PROMPT.format(
        title=title,
        piece_type=piece_type,
        content=draft_content[:4000],
        seed_text=seed.get("text", "(unknown)"),
        seed_source=seed.get("source_type", "unknown"),
        voice_ctx=voice_content[:3000],
        banned_list=banned_list,
        min_words=STATEMENT_MIN_WORDS,
        max_words=STATEMENT_MAX_WORDS,
    )

    raw = call_model(client, model, prompt, max_tokens=2048)

    # Strip any preamble the model might add
    for marker in ("Here's the artist statement", "Here is the artist statement",
                   "**Artist Statement**", "# Artist Statement"):
        if raw.startswith(marker):
            raw = raw[len(marker):].lstrip("\n")

    return raw.strip()


# ---------------------------------------------------------------------------
# Gallery frontmatter generation
# ---------------------------------------------------------------------------

def generate_gallery_frontmatter(
    seed: dict[str, Any],
    trace: dict[str, Any],
    statement_filename: str,
    piece_type: str,
    title: str,
    tags: list[str],
    cover_path: str,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """Build the Hugo frontmatter dict per gallery-frontmatter.md spec."""
    tz = get_tz(cfg)
    now = datetime.now(tz)

    # Date: prefer seed source_date, fall back to now
    date_str = seed.get("source_date", now.strftime("%Y-%m-%d"))
    # Normalize date to just the date portion
    if "T" in date_str:
        date_str = date_str[:10]

    # Extract judgment score from trace
    judgment = trace.get("judgment", {})
    judgment_score = judgment.get("score")
    judgment_criteria = judgment.get("criteria", {})

    # Extract model info from trace
    generation = trace.get("generation", {})
    model_used = generation.get("model", "")
    iterations = generation.get("iterations", 0)

    # Piece ID for filename
    piece_id = now.strftime("%Y-%m-%d")
    # Make it unique-ish
    seed_id = seed.get("id", "")[:8]
    if seed_id:
        piece_id = f"{piece_id}-{seed_id}"

    # Default type-based medium
    medium_map = {"image": "digital", "text": "digital", "music": "digital",
                  "collage": "mixed", "video": "digital"}
    medium = medium_map.get(piece_type, "digital")

    frontmatter: dict[str, Any] = {
        "title": title,
        "date": date_str,
        "lastmod": now.strftime("%Y-%m-%d"),
        "draft": False,
        "type": piece_type,
        "medium": medium,
        "cover": cover_path,
        "alt": _generate_alt_text(seed, piece_type),
        "statement": statement_filename,
        "tags": tags,
        "categories": ["gallery"],
    }

    # Optional fields — include only when they have values
    series = seed.get("series", "")
    if series:
        frontmatter["series"] = series

    if judgment_score is not None:
        frontmatter["judgment_score"] = judgment_score

    if model_used:
        frontmatter["model"] = model_used

    if iterations:
        frontmatter["iterations"] = iterations

    # Dimensions for text: word count
    if piece_type == "text":
        # Will be filled by caller with actual word count
        frontmatter.setdefault("dimensions", "")

    return frontmatter


def _generate_alt_text(seed: dict[str, Any], piece_type: str) -> str:
    """Generate accessibility alt text from seed."""
    seed_text = seed.get("text", "")
    # Truncate to reasonable alt length
    if len(seed_text) > 120:
        seed_text = seed_text[:117] + "…"
    type_prefix = {"image": "Digital artwork", "text": "Creative text piece",
                   "music": "Musical composition", "video": "Video piece",
                   "collage": "Digital collage"}.get(piece_type, "Creative piece")
    return f"{type_prefix} inspired by: {seed_text}"


def frontmatter_to_yaml(fm: dict[str, Any]) -> str:
    """Serialize frontmatter dict to YAML string."""
    return yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False).strip()


# ---------------------------------------------------------------------------
# Piece title extraction
# ---------------------------------------------------------------------------

def extract_title(draft_content: str, seed: dict[str, Any]) -> str:
    """Extract or generate a title for the piece.

    Strategy:
    1. First markdown heading (# or ##) in the draft
    2. First line if it looks like a title (< 80 chars, no markdown)
    3. Truncated seed text
    """
    lines = draft_content.strip().splitlines()

    for line in lines:
        # H1 heading
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            if title:
                return title
        # H2 as fallback
        if line.startswith("## "):
            title = line[3:].strip()
            if title:
                return title

    # First non-empty line
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) < 80 and not stripped.startswith(("*", "`", "[", "![", "```")):
            return stripped

    # Seed text fallback
    seed_text = seed.get("text", "Untitled")
    if len(seed_text) > 60:
        seed_text = seed_text[:57] + "…"
    return seed_text


# ---------------------------------------------------------------------------
# Tags extraction
# ---------------------------------------------------------------------------

def extract_tags(seed: dict[str, Any], trace: dict[str, Any]) -> list[str]:
    """Extract tags from seed and trace data."""
    tags: list[str] = []

    # Emotional tags from seed
    for tag in seed.get("emotional_tags", []):
        tag = tag.strip()
        if tag and tag not in tags:
            tags.append(tag)

    # Source type as tag
    source_type = seed.get("source_type", "")
    if source_type and source_type not in tags:
        tags.append(source_type)

    # Thread tags from seed
    for thread in seed.get("threads", []):
        thread = thread.strip()
        if thread and thread not in tags:
            tags.append(thread)

    # Extract tags from the piece type
    piece_type = trace.get("output", {}).get("type", "text")
    if piece_type and piece_type not in tags:
        tags.append(piece_type)

    # Ensure at least one tag
    if not tags:
        tags = ["creative", "gallery"]

    return tags


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_publish(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Full publication pipeline for a draft."""
    draft_path = Path(args.draft).expanduser().resolve()
    if not draft_path.exists():
        print(f"ERROR: Draft file not found: {draft_path}", file=sys.stderr)
        sys.exit(1)

    # 1. Read draft content
    draft_content = read_file(draft_path)
    if not draft_content:
        print(f"ERROR: Draft file is empty: {draft_path}", file=sys.stderr)
        sys.exit(1)

    # 2. Read source trace
    trace = load_trace(draft_path)
    if not trace:
        print(f"WARN: No source trace found for {draft_path.name}", file=sys.stderr)
        trace = {"seed": {}, "generation": {}, "judgment": {}, "output": {}}

    # 3. Extract seed ID and load seed
    seed_id = extract_seed_id(draft_path)
    seeds = load_seeds(cfg)
    seed: dict[str, Any] = {}

    if seed_id:
        for s in seeds:
            if s.get("id") == seed_id or s.get("id", "").startswith(seed_id):
                seed = s
                break
        # Also check the trace for seed text if not found in seeds
        if not seed:
            trace_seed = trace.get("seed", {})
            if trace_seed.get("text"):
                seed = {
                    "id": seed_id,
                    "text": trace_seed["text"],
                    "source_type": trace_seed.get("source", {}).get("type", "unknown"),
                    "source_date": trace_seed.get("source", {}).get("date", ""),
                    "source_ref": trace_seed.get("source", {}).get("ref", ""),
                    "emotional_tags": [],
                    "threads": [],
                    "status": "unknown",
                }
    else:
        # No seed ID from filename — use trace seed
        trace_seed = trace.get("seed", {})
        seed = {
            "id": trace_seed.get("id", "unknown"),
            "text": trace_seed.get("text", ""),
            "source_type": trace_seed.get("source", {}).get("type", "unknown"),
            "source_date": trace_seed.get("source", {}).get("date", ""),
            "source_ref": trace_seed.get("source", {}).get("ref", ""),
            "emotional_tags": [],
            "threads": [],
            "status": "unknown",
        }

    if not seed.get("text"):
        print("ERROR: Could not find seed data for this draft", file=sys.stderr)
        sys.exit(1)

    # 4. Read VOICE.md
    voice_content = load_voice_content(cfg)
    if not voice_content:
        print("WARN: Voice file is empty or not found — statement may not match voice", file=sys.stderr)

    # 5. Banned phrase scan on draft
    banned = parse_banned_phrases(voice_content)
    if banned:
        matches = scan_banned(draft_content, banned)
        if matches:
            print(f"⚠ Banned phrases detected in draft ({len(matches)} match(es)):", file=sys.stderr)
            for m in matches[:5]:
                print(f"  → {m}", file=sys.stderr)
            if args.json_output:
                print(json.dumps({"error": "banned_phrases_detected", "matches": matches}, indent=2))
                sys.exit(1)
            print("ERROR: Remove banned phrases before publishing. Use --json for details.",
                  file=sys.stderr)
            sys.exit(1)

    # Extract metadata
    piece_type = trace.get("output", {}).get("type", "text")
    title = extract_title(draft_content, seed)
    tags = extract_tags(seed, trace)

    # 6. Generate artist statement
    print("Generating artist statement...", file=sys.stderr)
    client = create_client(cfg)
    model = cfg["api"]["model"]
    statement = generate_artist_statement(
        client=client,
        model=model,
        draft_content=draft_content,
        seed=seed,
        voice_content=voice_content,
        banned=banned,
        piece_type=piece_type,
    )

    # Word count check
    word_count = len(statement.split())
    if word_count < STATEMENT_MIN_WORDS or word_count > STATEMENT_MAX_WORDS * 1.5:
        print(f"WARN: Statement is {word_count} words (target: {STATEMENT_MIN_WORDS}–{STATEMENT_MAX_WORDS})",
              file=sys.stderr)

    # 7. Build gallery output
    tz = get_tz(cfg)
    now = datetime.now(tz)
    piece_id = now.strftime("%Y-%m-%d")
    seed_short = (seed.get("id", "")[:8]) or "unknown"
    piece_id = f"{piece_id}-{seed_short}"

    gallery_dir = resolve_path(cfg, cfg["gallery"]["output_dir"])
    gallery_dir.mkdir(parents=True, exist_ok=True)

    # Filenames
    slug = piece_id.lower().replace(" ", "-")
    gallery_filename = f"piece-{slug}.md"
    statement_filename = f"piece-{slug}-statement.md"
    gallery_path = gallery_dir / gallery_filename
    statement_path = gallery_dir / statement_filename

    # Cover path (default — will be updated when actual media is generated)
    cover_filename = f"piece-{slug}.png"
    cover_path = f"pieces/{cover_filename}"

    # Update dimensions for text pieces
    dimensions = ""
    if piece_type == "text":
        wc = len(draft_content.split())
        dimensions = f"{wc} words"

    # Generate frontmatter
    frontmatter = generate_gallery_frontmatter(
        seed=seed,
        trace=trace,
        statement_filename=statement_filename,
        piece_type=piece_type,
        title=title,
        tags=tags,
        cover_path=cover_path,
        cfg=cfg,
    )
    if dimensions:
        frontmatter["dimensions"] = dimensions

    # Build complete gallery file
    fm_yaml = frontmatter_to_yaml(frontmatter)
    gallery_markdown = f"---\n{fm_yaml}\n---\n\n{draft_content}\n"

    # 8. Dry run / preview
    if args.dry_run:
        print("=== PREVIEW: What would be published ===\n")
        print(f"Title: {title}")
        print(f"Type: {piece_type}")
        print(f"Tags: {', '.join(tags)}")
        print(f"Seed ID: {seed.get('id', 'unknown')}")
        print(f"Seed text: {seed.get('text', '')[:100]}")
        print(f"\nGallery output: {gallery_path}")
        print(f"Statement: {statement_path}")
        print(f"\n--- Frontmatter ---")
        print(fm_yaml)
        print(f"\n--- Artist Statement ({word_count} words) ---")
        print(statement)
        print(f"\n--- Draft ({len(draft_content)} chars) ---")
        print(draft_content[:500])
        if len(draft_content) > 500:
            print(f"… ({len(draft_content) - 500} more chars)")
        return

    # 9. Write files
    gallery_path.write_text(gallery_markdown, encoding="utf-8")
    statement_path.write_text(statement, encoding="utf-8")
    print(f"  Gallery: {gallery_path}", file=sys.stderr)
    print(f"  Statement: {statement_path}", file=sys.stderr)

    # 10. Update source trace with publication info
    trace.setdefault("judgment", {})
    trace["judgment"]["human_review"] = "approved"
    trace.setdefault("output", {})
    trace["output"]["files"] = trace["output"].get("files", [])
    trace["output"]["files"].append(gallery_filename)
    trace["output"]["files"].append(statement_filename)
    trace["output"]["statement_path"] = statement_filename
    trace["output"]["gallery_path"] = gallery_filename
    trace["output"]["published_at"] = now.isoformat()
    trace["output"]["publication_status"] = "published"
    save_trace(draft_path, trace)

    # 11. Update seed status in creative-seeds.json
    if seed.get("id") and seed.get("id") != "unknown":
        for s in seeds:
            if s.get("id") == seed["id"]:
                s["status"] = "published"
                s["output_path"] = str(gallery_path)
                break
        save_seeds(cfg, seeds)
        print(f"  Seed {seed['id']} status → published", file=sys.stderr)

    # Output
    if args.json_output:
        result = {
            "title": title,
            "type": piece_type,
            "seed_id": seed.get("id"),
            "gallery_file": str(gallery_path),
            "statement_file": str(statement_path),
            "cover_path": cover_path,
            "tags": tags,
            "statement_words": word_count,
            "draft_chars": len(draft_content),
            "trace_updated": True,
            "seed_updated": seed.get("id") is not None,
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\nPublished: {title}")
        print(f"  Gallery:  {gallery_path}")
        print(f"  Statement: {statement_path}")
        print(f"  Cover:    {cover_path}")
        print(f"  Tags:     {', '.join(tags)}")
        print(f"  Statement: {word_count} words")


def cmd_statement(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Generate just the artist statement for a draft."""
    draft_path = Path(args.draft).expanduser().resolve()
    if not draft_path.exists():
        print(f"ERROR: Draft file not found: {draft_path}", file=sys.stderr)
        sys.exit(1)

    draft_content = read_file(draft_path)
    if not draft_content:
        print(f"ERROR: Draft file is empty: {draft_path}", file=sys.stderr)
        sys.exit(1)

    trace = load_trace(draft_path)
    seed_id = extract_seed_id(draft_path)
    seeds = load_seeds(cfg)
    seed: dict[str, Any] = {}

    if seed_id:
        for s in seeds:
            if s.get("id") == seed_id or s.get("id", "").startswith(seed_id):
                seed = s
                break

    if not seed:
        trace_seed = trace.get("seed", {})
        seed = {
            "id": trace_seed.get("id", "unknown"),
            "text": trace_seed.get("text", ""),
            "source_type": trace_seed.get("source", {}).get("type", "unknown"),
            "emotional_tags": [],
        }

    if not seed.get("text"):
        print("ERROR: Could not find seed data for this draft", file=sys.stderr)
        sys.exit(1)

    voice_content = load_voice_content(cfg)
    banned = parse_banned_phrases(voice_content)

    piece_type = trace.get("output", {}).get("type", "text")

    if args.dry_run:
        title = extract_title(draft_content, seed)
        print(f"=== DRY RUN: Statement generation for '{title}' ===")
        print(f"Seed: {seed.get('text', '')[:100]}")
        print(f"Type: {piece_type}")
        print(f"Banned phrases loaded: {len(banned)}")
        return

    print("Generating artist statement...", file=sys.stderr)
    client = create_client(cfg)
    model = cfg["api"]["model"]
    statement = generate_artist_statement(
        client=client,
        model=model,
        draft_content=draft_content,
        seed=seed,
        voice_content=voice_content,
        banned=banned,
        piece_type=piece_type,
    )

    word_count = len(statement.split())
    print(statement)

    if args.json_output:
        result = {
            "statement": statement,
            "word_count": word_count,
            "seed_id": seed.get("id"),
            "piece_type": piece_type,
        }
        # Also print as JSON to stderr so it doesn't mix with the statement
        print(json.dumps(result, indent=2), file=sys.stderr)
    else:
        print(f"\n--- ({word_count} words) ---", file=sys.stderr)


def cmd_preview(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Show what would be published without writing any files."""
    # Preview is just publish with --dry-run
    args.dry_run = True
    cmd_publish(args, cfg)


def cmd_list(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """List published pieces with metadata."""
    gallery_dir = resolve_path(cfg, cfg["gallery"]["output_dir"])

    if not gallery_dir.exists():
        if args.json_output:
            print(json.dumps({"published": [], "gallery_dir": str(gallery_dir)}, indent=2))
        else:
            print(f"No gallery directory found: {gallery_dir}")
        return

    pieces: list[dict[str, Any]] = []
    for path in sorted(gallery_dir.glob("piece-*.md")):
        # Skip statement files
        if "-statement.md" in path.name:
            continue

        content = read_file(path)
        if not content:
            continue

        # Parse frontmatter
        frontmatter: dict[str, Any] = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    pass

        body = content.split("---", 2)[-1].strip() if "---" in content else content
        word_count = len(body.split())

        pieces.append({
            "file": str(path),
            "title": frontmatter.get("title", path.stem),
            "date": frontmatter.get("date", ""),
            "type": frontmatter.get("type", "unknown"),
            "tags": frontmatter.get("tags", []),
            "judgment_score": frontmatter.get("judgment_score"),
            "words": word_count,
            "chars": len(body),
        })

    if args.json_output:
        print(json.dumps({"published": pieces, "count": len(pieces)}, indent=2))
    else:
        if not pieces:
            print("No published pieces found.")
            return

        print(f"{len(pieces)} published piece(s):\n")
        for p in pieces:
            score = f" | score: {p['judgment_score']}" if p['judgment_score'] is not None else ""
            print(f"  {p['title']}")
            print(f"    {p['date']} | {p['type']} | {p['words']} words{score}")
            print(f"    Tags: {', '.join(p['tags'])}")
            print(f"    File: {p['file']}")
            print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="publisher",
        description="Creative pipeline: publish drafts to gallery with artist statements.",
    )
    parser.add_argument(
        "--config", "-c",
        default=DEFAULT_CONFIG,
        help=f"Path to pipeline config YAML (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="json_output",
        help="Output in machine-readable JSON format",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # publish
    p_publish = sub.add_parser("publish", help="Publish a draft to the gallery")
    p_publish.add_argument("--draft", required=True, help="Path to draft file")
    p_publish.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be published without writing files",
    )

    # statement
    p_statement = sub.add_parser("statement", help="Generate artist statement for a draft")
    p_statement.add_argument("--draft", required=True, help="Path to draft file")
    p_statement.add_argument(
        "--dry-run",
        action="store_true",
        help="Show generation parameters without calling API",
    )

    # preview
    p_preview = sub.add_parser("preview", help="Preview what would be published (dry run)")
    p_preview.add_argument("--draft", required=True, help="Path to draft file")

    # list
    p_list = sub.add_parser("list", help="List published pieces")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    cfg = load_config(args.config)

    commands = {
        "publish": cmd_publish,
        "statement": cmd_statement,
        "preview": cmd_preview,
        "list": cmd_list,
    }

    cmd_fn = commands.get(args.command)
    if not cmd_fn:
        parser.print_help()
        sys.exit(1)

    cmd_fn(args, cfg)


if __name__ == "__main__":
    main()
