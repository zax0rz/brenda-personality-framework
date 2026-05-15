#!/usr/bin/env python3
"""
Drift Detection — Monitor personality and voice drift in creative output.

Scans output files for banned phrases, measures voice similarity against
exemplars, and produces coherence reports.

Commands:
  banned   Scan output files for banned phrases from VOICE.md
  voice    Measure voice similarity of a single output against voice exemplars
  report   Full coherence report combining banned + voice + personality checks

Config file (YAML):
  workspace: /path/to/agent/workspace
  voice_file: VOICE.md
  personality_file: PERSONALITY.md
  timezone: "America/New_York"

Dependencies: Python 3.10+, pyyaml. Zero other external deps.
TF-IDF similarity is computed with stdlib only (collections.Counter + math).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
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

VOICE_WARN_THRESHOLD = 0.3
VOICE_ALERT_THRESHOLD = 0.2

# Text extensions to scan
TEXT_EXTENSIONS = {".md", ".txt", ".markdown"}


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

    required = ["workspace", "voice_file", "personality_file"]
    for key in required:
        if key not in cfg:
            print(f"ERROR: Config missing required key: {key}", file=sys.stderr)
            sys.exit(1)

    cfg.setdefault("timezone", "America/New_York")
    return cfg


def resolve_path(cfg: dict[str, Any], relative: str) -> Path:
    """Resolve a relative path against the workspace root."""
    return Path(cfg["workspace"]) / relative


def read_file(path: Path) -> str:
    """Read a text file, return empty string if not found."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Voice file parsing — extract banned phrases and exemplars
# ---------------------------------------------------------------------------

def parse_banned_phrases(voice_content: str) -> list[tuple[str, bool, Optional[re.Pattern[str]]]]:
    """
    Extract banned phrases from VOICE.md content.

    Looks for sections titled 'Banned', 'Banned Phrases', or 'Never Say'
    (case-insensitive). Each line is a banned phrase.
    Lines starting with 'regex:' are treated as regular expression patterns.

    Returns list of (raw_string, is_regex, compiled_pattern_or_None).
    """
    phrases: list[tuple[str, bool, Optional[re.Pattern[str]]]] = []
    in_section = False

    section_headers = ["banned", "banned phrases", "never say", "do not say", "prohibited phrases"]

    for line in voice_content.splitlines():
        stripped = line.strip()
        header_match = stripped.startswith("#") and stripped.lstrip("# ").strip().lower()
        if header_match:
            header_text = stripped.lstrip("# ").strip().lower()
            in_section = any(header_text == h or header_text.startswith(h) for h in section_headers)
            continue

        if in_section and stripped and not stripped.startswith("#"):
            # Skip empty lines and comments within the section
            if stripped.startswith("- ") or stripped.startswith("* "):
                stripped = stripped[2:]

            if not stripped:
                continue

            is_regex = stripped.lower().startswith("regex:")
            if is_regex:
                pattern_str = stripped[6:].strip()
                try:
                    compiled = re.compile(pattern_str, re.IGNORECASE)
                    phrases.append((pattern_str, True, compiled))
                except re.error as e:
                    print(f"WARN: Invalid regex pattern '{pattern_str}': {e}", file=sys.stderr)
            else:
                phrases.append((stripped, False, None))

    return phrases


def parse_voice_exemplars(voice_content: str) -> list[str]:
    """
    Extract good voice examples from VOICE.md.

    Looks for sections titled 'Good', 'Examples', 'Voice Exemplars',
    '✅ Good', or similar. Returns list of example text blocks.
    """
    exemplars: list[str] = []
    in_section = False
    current_example: list[str] = []

    section_headers = [
        "good", "examples", "voice exemplars", "✅ good",
        "example output", "sample output", "do say",
    ]

    for line in voice_content.splitlines():
        stripped = line.strip()
        header_match = stripped.startswith("#") and stripped.lstrip("# ").strip()

        if header_match:
            header_text = stripped.lstrip("# ").strip().lower()
            # Remove emoji for matching
            clean_header = re.sub(r"[^\w\s]", "", header_text).strip()

            is_section = any(
                clean_header == re.sub(r"[^\w\s]", "", h).strip()
                for h in section_headers
            )
            # Also check if the header CONTAINS a section keyword
            if not is_section:
                is_section = any(
                    kw in clean_header
                    for kw in ("good example", "voice example", "exemplar", "✅")
                )

            if in_section and current_example:
                block = "\n".join(current_example).strip()
                if block:
                    exemplars.append(block)
                current_example = []

            in_section = is_section
            continue

        if in_section:
            # Split on multiple consecutive blank lines to separate examples
            if not stripped and current_example and current_example[-1] == "":
                # Consecutive blank = new example
                block = "\n".join(current_example).strip()
                if block:
                    exemplars.append(block)
                current_example = []
            else:
                current_example.append(stripped)

    if current_example:
        block = "\n".join(current_example).strip()
        if block:
            exemplars.append(block)

    return exemplars


# ---------------------------------------------------------------------------
# Personality file parsing — extract opinions and keywords
# ---------------------------------------------------------------------------

def parse_personality_keywords(personality_content: str) -> list[tuple[str, str]]:
    """
    Extract stated opinions/positions from PERSONALITY.md as keyword pairs.

    Returns list of (topic, stance) tuples for consistency checking.
    Looks under '## Formed Opinions' and extracts topic + stance lines.
    """
    keywords: list[tuple[str, str]] = []
    in_opinions = False
    current_topic = ""

    for line in personality_content.splitlines():
        stripped = line.strip()
        header_match = stripped.startswith("## ") and stripped.lstrip("# ").strip()

        if header_match:
            header_text = stripped.lstrip("# ").strip().lower()
            in_opinions = "formed opinions" in header_text
            continue

        if in_opinions:
            # ### marks a new opinion topic
            if stripped.startswith("### "):
                current_topic = stripped.lstrip("# ").strip()
                continue

            # Extract stance
            if stripped.lower().startswith("- **stance:**") or "**stance:**" in stripped.lower():
                stance = stripped.split("**stance:**", 1)[-1].strip()
                if current_topic and stance:
                    keywords.append((current_topic, stance.lower()))

            # Also extract from - **Stance:**
            if "- **Stance:" in stripped or "- **stance:" in stripped:
                parts = re.split(r"\*\*[Ss]tance:\*\*\s*", stripped, maxsplit=1)
                if len(parts) > 1:
                    stance = parts[1].strip().rstrip("—-").strip()
                    if current_topic and stance:
                        keywords.append((current_topic, stance.lower()))

    return keywords


# ---------------------------------------------------------------------------
# Banned phrase scanning
# ---------------------------------------------------------------------------

def scan_file_for_banned(
    file_path: Path,
    banned_phrases: list[tuple[str, bool, Optional[re.Pattern[str]]]],
) -> list[dict[str, Any]]:
    """
    Scan a single file for banned phrases.

    Returns list of matches: [{"phrase": ..., "line": ..., "line_num": int}, ...]
    """
    content = read_file(file_path)
    if not content:
        return []

    matches: list[dict[str, Any]] = []
    lines = content.splitlines()

    for line_num, line in enumerate(lines, start=1):
        for raw, is_regex, compiled in banned_phrases:
            if is_regex and compiled:
                if compiled.search(line):
                    matches.append({
                        "phrase": raw,
                        "line": line.strip(),
                        "line_num": line_num,
                        "type": "regex",
                    })
            else:
                # Case-insensitive substring search
                if raw.lower() in line.lower():
                    matches.append({
                        "phrase": raw,
                        "line": line.strip(),
                        "line_num": line_num,
                        "type": "literal",
                    })

    return matches


def scan_directory_for_banned(
    directory: Path,
    banned_phrases: list[tuple[str, bool, Optional[re.Pattern[str]]]],
) -> dict[str, Any]:
    """
    Scan all text files in a directory for banned phrases.

    Returns scan results dict.
    """
    files_scanned = 0
    files_with_matches = 0
    total_matches = 0
    file_results: list[dict[str, Any]] = []

    if not directory.is_dir():
        print(f"ERROR: Not a directory: {directory}", file=sys.stderr)
        sys.exit(1)

    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        matches = scan_file_for_banned(path, banned_phrases)
        files_scanned += 1

        if matches:
            files_with_matches += 1
            total_matches += len(matches)
            file_results.append({
                "file": str(path),
                "matches": matches,
                "match_count": len(matches),
            })

    return {
        "files_scanned": files_scanned,
        "files_with_matches": files_with_matches,
        "total_matches": total_matches,
        "results": file_results,
    }


# ---------------------------------------------------------------------------
# TF-IDF cosine similarity (stdlib-only implementation)
# ---------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    """
    Simple tokenizer: lowercase, split on non-alphanumeric, remove short tokens.
    """
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+(?:['-][a-z0-9]+)*", text)
    # Remove very short tokens (single chars) and common stop words
    stop_words = {
        "a", "an", "the", "is", "it", "in", "on", "at", "to", "for", "of",
        "and", "or", "but", "not", "with", "as", "by", "be", "was", "were",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can", "this",
        "that", "these", "those", "from", "into", "than", "so", "if", "no",
        "its", "my", "your", "his", "her", "our", "their", "i", "me", "you",
        "he", "she", "we", "they", "what", "which", "who", "when", "where",
        "how", "why", "all", "each", "every", "both", "few", "more", "most",
        "other", "some", "such", "only", "same", "just", "also", "very",
    }
    return [t for t in tokens if len(t) > 1 and t not in stop_words]


def compute_tf(tokens: list[str]) -> Counter[str]:
    """Compute term frequency."""
    return Counter(tokens)


def compute_idf(documents: list[list[str]]) -> dict[str, float]:
    """
    Compute inverse document frequency across a corpus.

    idf(t) = log(N / (1 + df(t)))
    """
    n = len(documents)
    if n == 0:
        return {}

    # Document frequency: how many docs contain each term
    df: Counter[str] = Counter()
    for doc_tokens in documents:
        unique_terms = set(doc_tokens)
        for term in unique_terms:
            df[term] += 1

    return {
        term: math.log(n / (1 + count))
        for term, count in df.items()
    }


def compute_tfidf(tf: Counter[str], idf: dict[str, float]) -> dict[str, float]:
    """Compute TF-IDF vector from term frequencies and IDF."""
    return {
        term: freq * idf.get(term, 0.0)
        for term, freq in tf.items()
    }


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """
    Compute cosine similarity between two sparse vectors (dicts).

    Returns 0.0 if either vector has zero magnitude.
    """
    # Dot product (only over shared keys)
    dot = sum(vec_a[k] * vec_b[k] for k in vec_a if k in vec_b)
    if dot == 0.0:
        return 0.0

    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot / (mag_a * mag_b)


def measure_voice_similarity(
    target_text: str,
    exemplar_texts: list[str],
) -> dict[str, Any]:
    """
    Measure voice similarity between target text and voice exemplars.

    Uses TF-IDF cosine similarity — a lightweight heuristic.

    NOTE: This is a rough approximation. Full voice drift measurement requires
    embedding cosine similarity over 20-30 curated exemplars using an
    embedding model (see personality-schema.md, voice_drift computation).
    This script provides a fast, dependency-free check. Scores should be
    interpreted as relative indicators, not absolute measures.

    Returns dict with score, threshold assessments, and details.
    """
    if not exemplar_texts:
        return {
            "score": 0.0,
            "status": "NO_EXEMPLARS",
            "message": "No voice exemplars found in VOICE.md. Cannot measure similarity.",
            "exemplar_count": 0,
        }

    # Tokenize
    target_tokens = tokenize(target_text)
    exemplar_token_lists = [tokenize(ex) for ex in exemplar_texts]

    # Filter out empty exemplars
    exemplar_token_lists = [tl for tl in exemplar_token_lists if tl]

    if not exemplar_token_lists:
        return {
            "score": 0.0,
            "status": "NO_EXEMPLARS",
            "message": "Voice exemplars contain no parseable text.",
            "exemplar_count": 0,
        }

    # Build corpus: target + all exemplars for IDF computation
    all_docs = [target_tokens] + exemplar_token_lists
    idf = compute_idf(all_docs)

    # Target TF-IDF
    target_tf = compute_tf(target_tokens)
    target_tfidf = compute_tfidf(target_tf, idf)

    # Compute similarity to each exemplar, then average
    similarities: list[float] = []
    for ex_tokens in exemplar_token_lists:
        ex_tf = compute_tf(ex_tokens)
        ex_tfidf = compute_tfidf(ex_tf, idf)
        sim = cosine_similarity(target_tfidf, ex_tfidf)
        similarities.append(sim)

    avg_similarity = sum(similarities) / len(similarities)
    max_similarity = max(similarities)
    min_similarity = min(similarities)

    # Threshold assessment
    if avg_similarity >= VOICE_WARN_THRESHOLD:
        status = "OK"
        message = f"Voice similarity {avg_similarity:.3f} is above warning threshold ({VOICE_WARN_THRESHOLD}). Voice appears consistent."
    elif avg_similarity >= VOICE_ALERT_THRESHOLD:
        status = "WARN"
        message = f"Voice similarity {avg_similarity:.3f} is below warning threshold ({VOICE_WARN_THRESHOLD}) but above alert ({VOICE_ALERT_THRESHOLD}). Minor drift detected."
    else:
        status = "ALERT"
        message = f"Voice similarity {avg_similarity:.3f} is below alert threshold ({VOICE_ALERT_THRESHOLD}). Significant voice drift detected — review recommended."

    return {
        "score": round(avg_similarity, 4),
        "max": round(max_similarity, 4),
        "min": round(min_similarity, 4),
        "status": status,
        "message": message,
        "exemplar_count": len(exemplar_token_lists),
        "per_exemplar": [round(s, 4) for s in similarities],
        "method": "tfidf_cosine",
        "caveat": (
            "TF-IDF cosine is a lightweight heuristic. For production voice drift "
            "measurement, use embedding cosine similarity over curated exemplar sets "
            "(see personality-schema.md)."
        ),
    }


# ---------------------------------------------------------------------------
# Personality consistency check
# ---------------------------------------------------------------------------

def check_personality_consistency(
    text: str,
    personality_keywords: list[tuple[str, str]],
) -> dict[str, Any]:
    """
    Check if output text is consistent with stated personality positions.

    Uses simple keyword overlap — if a topic from PERSONALITY.md is mentioned
    in the text, verify the stance direction is compatible.

    This is a coarse heuristic. False positives and false negatives are expected.
    """
    text_lower = text.lower()
    checks: list[dict[str, Any]] = []

    for topic, stance in personality_keywords:
        # Extract key terms from topic (split camelCase, lowercase)
        topic_terms = re.findall(r"[a-z]+(?:'[a-z]+)?", topic.lower())
        topic_terms = [t for t in topic_terms if len(t) > 2]

        # Check if any topic terms appear in the text
        topic_mentions = [t for t in topic_terms if t in text_lower]

        if topic_mentions:
            checks.append({
                "topic": topic,
                "stance": stance,
                "matched_terms": topic_mentions,
                "mentioned": True,
            })

    return {
        "topics_mentioned": len(checks),
        "total_tracked": len(personality_keywords),
        "checks": checks,
        "note": (
            "This is a keyword-overlap heuristic. It detects topic mentions but "
            "cannot verify deep semantic alignment. Manual review is recommended "
            "for personality-critical output."
        ),
    }


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_banned(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Scan for banned phrases in output files."""
    voice_content = read_file(resolve_path(cfg, cfg["voice_file"]))
    if not voice_content:
        print("ERROR: Voice file is empty or not found", file=sys.stderr)
        sys.exit(1)

    banned_phrases = parse_banned_phrases(voice_content)
    if not banned_phrases:
        print("No banned phrases found in VOICE.md.")
        print("Add a '## Banned Phrases' or '## Never Say' section to configure scanning.")
        if args.json_output:
            print(json.dumps({"scanned": 0, "matches": 0, "banned_count": 0}, indent=2))
        return

    print(f"Loaded {len(banned_phrases)} banned phrase(s) from VOICE.md\n", file=sys.stderr)

    # Determine scan targets
    if args.file:
        targets = [Path(args.file).expanduser().resolve()]
        file_mode = True
    elif args.dir:
        scan_dir = Path(args.dir).expanduser().resolve()
        file_mode = False
    else:
        print("ERROR: Specify --file or --dir", file=sys.stderr)
        sys.exit(1)

    if file_mode:
        matches = scan_file_for_banned(targets[0], banned_phrases)
        result = {
            "files_scanned": 1,
            "files_with_matches": 1 if matches else 0,
            "total_matches": len(matches),
            "results": [
                {"file": str(targets[0]), "matches": matches, "match_count": len(matches)}
            ] if matches else [],
        }
    else:
        result = scan_directory_for_banned(scan_dir, banned_phrases)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"Scanned {result['files_scanned']} file(s)")
        print(f"Found {result['total_matches']} match(es) in {result['files_with_matches']} file(s)")

        if result["total_matches"] == 0:
            print("\n✅ No banned phrases detected.")

        for file_result in result["results"]:
            print(f"\n{file_result['file']} ({file_result['match_count']} match(es))")
            for m in file_result["matches"]:
                loc = f"line {m['line_num']}"
                ptype = f"[{m['type']}]" if m["type"] == "regex" else ""
                print(f"  {loc} {ptype} '{m['phrase']}'")
                print(f"    → {m['line'][:120]}")


def cmd_voice(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Measure voice similarity of a single output file."""
    voice_content = read_file(resolve_path(cfg, cfg["voice_file"]))
    if not voice_content:
        print("ERROR: Voice file is empty or not found", file=sys.stderr)
        sys.exit(1)

    file_path = Path(args.file).expanduser().resolve()
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    target_text = read_file(file_path)
    if not target_text:
        print(f"ERROR: File is empty: {file_path}", file=sys.stderr)
        sys.exit(1)

    exemplars = parse_voice_exemplars(voice_content)

    print(f"Loaded {len(exemplars)} voice exemplar(s) from VOICE.md", file=sys.stderr)
    print(f"Measuring voice similarity for: {file_path}\n", file=sys.stderr)

    result = measure_voice_similarity(target_text, exemplars)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        status_icon = {
            "OK": "✅",
            "WARN": "⚠️",
            "ALERT": "🔴",
            "NO_EXEMPLARS": "⚠️",
        }.get(result["status"], "❓")

        print(f"{status_icon} {result['status']} — {result['message']}")
        print(f"\n  Score:  {result['score']:.4f}")
        print(f"  Max:    {result['max']:.4f}")
        print(f"  Min:    {result['min']:.4f}")
        print(f"  Exemplars: {result['exemplar_count']}")

        if result["status"] != "NO_EXEMPLARS" and result.get("per_exemplar"):
            print(f"\n  Per-exemplar scores: {[f'{s:.3f}' for s in result['per_exemplar']]}")

        if result.get("caveat"):
            print(f"\n  ℹ️  {result['caveat']}")


def cmd_report(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Generate full coherence report."""
    voice_content = read_file(resolve_path(cfg, cfg["voice_file"]))
    personality_content = read_file(resolve_path(cfg, cfg["personality_file"]))

    if not voice_content:
        print("WARN: Voice file is empty or not found — voice checks skipped", file=sys.stderr)
    if not personality_content:
        print("WARN: Personality file is empty or not found — consistency check skipped",
              file=sys.stderr)

    # Determine scan directory
    if args.dir:
        scan_dir = Path(args.dir).expanduser().resolve()
    else:
        # Default: draft directory from config
        scan_dir = resolve_path(cfg, cfg.get("draft_dir", "drafts/"))

    if not scan_dir.is_dir():
        print(f"ERROR: Scan directory not found: {scan_dir}", file=sys.stderr)
        sys.exit(1)

    report: dict[str, Any] = {
        "scan_dir": str(scan_dir),
        "timestamp": None,
        "banned_scan": None,
        "voice_scores": [],
        "personality_consistency": None,
        "recommendations": [],
    }

    # 1. Banned phrase scan
    banned_phrases = parse_banned_phrases(voice_content) if voice_content else []
    if banned_phrases:
        banned_result = scan_directory_for_banned(scan_dir, banned_phrases)
        report["banned_scan"] = banned_result

        if banned_result["total_matches"] > 0:
            report["recommendations"].append(
                f"{banned_result['total_matches']} banned phrase(s) detected across "
                f"{banned_result['files_with_matches']} file(s). Review flagged lines."
            )
    else:
        report["banned_scan"] = {"files_scanned": 0, "total_matches": 0, "note": "No banned phrases configured"}

    # 2. Voice similarity per file
    exemplars = parse_voice_exemplars(voice_content) if voice_content else []

    if exemplars:
        for path in sorted(scan_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue

            target_text = read_file(path)
            if not target_text:
                continue

            voice_result = measure_voice_similarity(target_text, exemplars)
            voice_result["file"] = str(path)
            report["voice_scores"].append(voice_result)

            if voice_result["status"] == "ALERT":
                report["recommendations"].append(
                    f"Voice ALERT for {path.name}: similarity {voice_result['score']:.3f} "
                    f"is below threshold. Significant drift detected."
                )
            elif voice_result["status"] == "WARN":
                report["recommendations"].append(
                    f"Voice WARN for {path.name}: similarity {voice_result['score']:.3f}. "
                    f"Monitor for further drift."
                )

        if not report["voice_scores"]:
            report["recommendations"].append(
                "No text files found in scan directory for voice analysis."
            )
    else:
        report["voice_scores"] = []
        report["recommendations"].append(
            "No voice exemplars found in VOICE.md. Add a '## Examples' or '## ✅ Good' "
            "section to enable voice similarity measurement."
        )

    # 3. Personality consistency check
    personality_keywords = parse_personality_keywords(personality_content) if personality_content else []

    if personality_keywords:
        # Check all text files collectively
        all_text = ""
        for path in sorted(scan_dir.rglob("*")):
            if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
                all_text += read_file(path) + "\n"

        if all_text.strip():
            report["personality_consistency"] = check_personality_consistency(
                all_text, personality_keywords
            )
            pc = report["personality_consistency"]
            report["recommendations"].append(
                f"{pc['topics_mentioned']}/{pc['total_tracked']} personality topics "
                f"detected in output. Review flagged topics for alignment."
            )
    else:
        report["personality_consistency"] = {"note": "No personality opinions found to check against"}

    # Summary
    alert_count = sum(1 for v in report["voice_scores"] if v["status"] == "ALERT")
    warn_count = sum(1 for v in report["voice_scores"] if v["status"] == "WARN")
    banned_total = report["banned_scan"].get("total_matches", 0) if report["banned_scan"] else 0

    report["summary"] = {
        "files_analyzed": len(report["voice_scores"]),
        "voice_alerts": alert_count,
        "voice_warnings": warn_count,
        "banned_matches": banned_total,
        "overall_status": "ALERT" if alert_count > 0 else ("WARN" if (warn_count > 0 or banned_total > 0) else "OK"),
    }

    if report["summary"]["overall_status"] == "OK":
        report["recommendations"].append("All checks passed. Output appears consistent with personality and voice.")

    from datetime import datetime
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(cfg.get("timezone", "America/New_York"))
    report["timestamp"] = datetime.now(tz).isoformat()

    if args.json_output:
        print(json.dumps(report, indent=2))
    else:
        status = report["summary"]["overall_status"]
        icon = {"OK": "✅", "WARN": "⚠️", "ALERT": "🔴"}.get(status, "❓")

        print(f"\n{'='*60}")
        print(f"  Coherence Report — {scan_dir}")
        print(f"  {report['timestamp']}")
        print(f"{'='*60}\n")

        print(f"Overall: {icon} {status}")
        print(f"  Files analyzed:  {report['summary']['files_analyzed']}")
        print(f"  Voice alerts:    {report['summary']['voice_alerts']}")
        print(f"  Voice warnings:  {report['summary']['voice_warnings']}")
        print(f"  Banned matches:  {report['summary']['banned_matches']}")

        # Banned scan
        print(f"\n--- Banned Phrase Scan ---")
        if report["banned_scan"]:
            bs = report["banned_scan"]
            print(f"  Files scanned: {bs['files_scanned']}")
            print(f"  Matches: {bs['total_matches']}")
            for fr in bs.get("results", []):
                for m in fr["matches"]:
                    print(f"    {fr['file'].split('/')[-1]}:{m['line_num']} — '{m['phrase']}'")

        # Voice scores
        print(f"\n--- Voice Similarity ---")
        for vs in report["voice_scores"]:
            fname = Path(vs["file"]).name
            sicon = {"OK": "✅", "WARN": "⚠️", "ALERT": "🔴"}.get(vs["status"], "❓")
            print(f"  {sicon} {fname}: {vs['score']:.4f} ({vs['status']})")

        # Personality consistency
        if report["personality_consistency"] and "checks" in report["personality_consistency"]:
            pc = report["personality_consistency"]
            print(f"\n--- Personality Consistency ---")
            print(f"  Topics detected: {pc['topics_mentioned']}/{pc['total_tracked']}")
            for check in pc["checks"]:
                print(f"    • {check['topic']}")
                print(f"      Stance: {check['stance'][:80]}")
                print(f"      Matched: {', '.join(check['matched_terms'])}")

        # Recommendations
        print(f"\n--- Recommendations ---")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")

        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drift_detection",
        description="Monitor personality and voice drift in creative output.",
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

    # banned
    p_banned = sub.add_parser("banned", help="Scan output files for banned phrases")
    p_banned.add_argument("--dir", help="Directory of output files to scan")
    p_banned.add_argument("--file", help="Single file to scan")

    # voice
    p_voice = sub.add_parser("voice", help="Measure voice similarity of a single file")
    p_voice.add_argument("--file", required=True, help="Path to output file")

    # report
    p_report = sub.add_parser("report", help="Full coherence report")
    p_report.add_argument(
        "--dir", "-d",
        help="Directory to scan (default: draft_dir from config)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    cfg = load_config(args.config)

    commands = {
        "banned": cmd_banned,
        "voice": cmd_voice,
        "report": cmd_report,
    }

    cmd_fn = commands.get(args.command)
    if not cmd_fn:
        parser.print_help()
        sys.exit(1)

    cmd_fn(args, cfg)


if __name__ == "__main__":
    main()
