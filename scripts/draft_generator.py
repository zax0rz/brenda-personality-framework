#!/usr/bin/env python3
"""
Draft Generator — Creative pipeline draft generation, refinement, and evaluation.

Takes approved seeds and produces creative output through iterative drafting,
personality-aware refinement, and structured self-evaluation.

Commands:
  draft     Generate N variants from a seed
  refine    Refine a draft with personality-aware instructions
  evaluate  Evaluate a draft against personality criteria

Config file (YAML):
  workspace: /path/to/agent/workspace
  personality_file: PERSONALITY.md
  voice_file: VOICE.md
  draft_dir: drafts/
  timezone: "America/New_York"
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
DEFAULT_VARIANTS = 3
DEFAULT_THRESHOLD = 0.75
DEFAULT_ITERATIONS = 1

PUBLICATION_THRESHOLD = 0.75
ARCHIVE_THRESHOLD = 0.5

JUDGMENT_CRITERIA = [
    "personality_alignment",
    "originality",
    "technical_quality",
    "emotional_truth",
]


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

    required = ["workspace", "personality_file", "voice_file"]
    for key in required:
        if key not in cfg:
            print(f"ERROR: Config missing required key: {key}", file=sys.stderr)
            sys.exit(1)

    cfg.setdefault("draft_dir", "drafts/")
    cfg.setdefault("seed_dir", "seeds/")
    cfg.setdefault("archive_dir", "archive/")
    cfg.setdefault("timezone", "America/New_York")

    if "api" not in cfg or not isinstance(cfg["api"], dict):
        print("ERROR: Config must have an 'api' section with base_url, model, api_key_env",
              file=sys.stderr)
        sys.exit(1)

    for k in ("base_url", "model", "api_key_env"):
        if k not in cfg["api"]:
            print(f"ERROR: api.{k} is required", file=sys.stderr)
            sys.exit(1)

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
    api_key = os.environ.get(cfg["api"]["api_key_env"])
    if not api_key:
        print(f"ERROR: Environment variable {cfg['api']['api_key_env']!r} is not set",
              file=sys.stderr)
        sys.exit(1)
    return OpenAI(base_url=cfg["api"]["base_url"], api_key=api_key)


def call_model(
    client: OpenAI,
    model: str,
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 4096,
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
        print(f"WARN: File not found: {path}", file=sys.stderr)
        return ""
    return path.read_text(encoding="utf-8")


def load_seed(seed_arg: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """Load a seed from a file path or seed ID."""
    seed_path = Path(seed_arg)
    if not seed_path.is_absolute():
        # Try as seed ID under seed_dir
        seed_path = resolve_path(cfg, cfg["seed_dir"]) / f"{seed_arg}.yaml"
        if not seed_path.exists():
            seed_path = resolve_path(cfg, cfg["seed_dir"]) / f"{seed_arg}.json"

    if not seed_path.exists():
        print(f"ERROR: Seed file not found: {seed_path}", file=sys.stderr)
        sys.exit(1)

    with open(seed_path) as f:
        if seed_path.suffix in (".yaml", ".yml"):
            seed = yaml.safe_load(f)
        else:
            seed = json.load(f)

    if not isinstance(seed, dict):
        print(f"ERROR: Seed file must contain a YAML/JSON object", file=sys.stderr)
        sys.exit(1)

    if "text" not in seed:
        print(f"ERROR: Seed must have a 'text' field", file=sys.stderr)
        sys.exit(1)

    return seed


def extract_seed_id(seed: dict[str, Any], seed_path: Path) -> str:
    """Get the seed ID from seed data or derive from filename."""
    if "id" in seed:
        return seed["id"]
    return seed_path.stem


def load_draft_with_trace(draft_path: Path) -> tuple[str, dict[str, Any]]:
    """Load a draft file and its accompanying source-trace.yaml."""
    draft_content = read_file(draft_path)
    trace_path = draft_path.parent / "source-trace.yaml"
    trace: dict[str, Any] = {}
    if trace_path.exists():
        with open(trace_path) as f:
            trace = yaml.safe_load(f) or {}
    return draft_content, trace


# ---------------------------------------------------------------------------
# Voice / personality context loading
# ---------------------------------------------------------------------------

def load_voice_context(cfg: dict[str, Any]) -> str:
    """Load voice file content for prompt injection."""
    voice_path = resolve_path(cfg, cfg["voice_file"])
    return read_file(voice_path)


def load_personality_context(cfg: dict[str, Any]) -> str:
    """Load personality file content for prompt injection."""
    personality_path = resolve_path(cfg, cfg["personality_file"])
    return read_file(personality_path)


def extract_relevant_personality(personality_md: str) -> str:
    """Extract the most relevant personality sections for draft generation."""
    # Pull formed opinions, creative tastes, and behavioral patterns
    sections = []
    current_section: list[str] = []
    in_target = False

    target_headers = [
        "Formed Opinions",
        "Creative Tastes",
        "Behavioral Patterns",
        "Evolving Preferences",
    ]

    for line in personality_md.splitlines():
        header_match = line.startswith("## ") and line.lstrip("# ").rstrip()
        if header_match:
            if in_target and current_section:
                sections.append("\n".join(current_section))
            current_section = []
            # Check if this header is a target
            stripped = line.lstrip("# ").strip()
            in_target = any(
                stripped.lower() == t.lower() or stripped.startswith(t.lower())
                for t in target_headers
            )
        if in_target:
            current_section.append(line)

    if current_section:
        sections.append("\n".join(current_section))

    return "\n\n".join(sections) if sections else personality_md[:3000]


# ---------------------------------------------------------------------------
# Source trace helpers
# ---------------------------------------------------------------------------

def build_source_trace(
    seed: dict[str, Any],
    seed_id: str,
    model: str,
    prompt: str,
    stage: str,
    medium: str = "text",
    variant_num: int = 0,
) -> dict[str, Any]:
    """Build a source-trace structure."""
    tz = ZoneInfo("UTC")
    now = datetime.now(tz)

    trace: dict[str, Any] = {
        "trace": {
            "id": f"{now.strftime('%Y-%m-%d')}-{seed_id}",
            "created": now.isoformat(),
        },
        "seed": {
            "id": f"seed-{seed_id}",
            "text": seed.get("text", ""),
            "source": {
                "type": seed.get("source_type", "unknown"),
                "date": seed.get("source_date", "unknown"),
                "ref": seed.get("source_ref", ""),
            },
        },
        "generation": {
            "model": model,
            "prompt": prompt,
            "iterations": 0,
            "pipeline_stage": stage,
            "variant": variant_num,
        },
        "judgment": {
            "score": None,
            "criteria": {},
            "human_review": "pending",
            "notes": "",
        },
        "output": {
            "type": medium,
            "format": medium,
        },
    }

    # Preserve existing trace fields if available
    existing = seed.get("source_trace")
    if isinstance(existing, dict):
        if "generation" in existing:
            trace["generation"]["iterations"] = existing["generation"].get("iterations", 0)

    return trace


def save_source_trace(trace: dict[str, Any], output_path: Path) -> None:
    """Save source trace next to the output file."""
    trace_path = output_path.parent / "source-trace.yaml"
    with open(trace_path, "w") as f:
        yaml.dump(trace, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def update_trace_judgment(
    trace: dict[str, Any],
    scores: dict[str, float],
    notes: str,
    threshold: float,
) -> dict[str, Any]:
    """Update a source trace with judgment scores."""
    avg = sum(scores.values()) / len(scores) if scores else 0.0

    trace.setdefault("judgment", {})
    trace["judgment"]["score"] = round(avg, 3)
    trace["judgment"]["criteria"] = {k: round(v, 3) for k, v in scores.items()}
    trace["judgment"]["notes"] = notes
    trace["judgment"]["human_review"] = "pending"
    trace["judgment"]["passes_threshold"] = avg >= threshold

    # Update iteration count
    trace.setdefault("generation", {})
    trace["generation"]["iterations"] = trace["generation"].get("iterations", 0) + 1

    return trace


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_draft_prompt(
    seed: dict[str, Any],
    voice_ctx: str,
    personality_ctx: str,
    medium: str,
) -> str:
    """Construct the generation prompt for a seed."""
    medium_instructions: dict[str, str] = {
        "text": (
            "Generate a text piece (blog post, essay, narrative, or reflection) "
            "based on the seed below. Write the complete piece — not a summary or outline."
        ),
        "image": (
            "Generate a detailed image generation prompt based on the seed below. "
            "Describe the visual composition, style, mood, and key elements. "
            "Do NOT generate the image itself — produce a text prompt that would be "
            "fed to an image generation model."
        ),
        "music": (
            "Generate a detailed music generation prompt based on the seed below. "
            "Describe the genre, mood, tempo, instrumentation, and structure. "
            "Do NOT generate music itself — produce a text prompt that would be "
            "fed to a music generation model."
        ),
    }

    instruction = medium_instructions.get(medium, medium_instructions["text"])

    seed_text = seed.get("text", "")
    seed_emotions = seed.get("emotional_tags", [])
    seed_source = seed.get("source_type", "unknown")
    seed_notes = seed.get("notes", "")

    prompt = f"""## Task
{instruction}

## Seed
**Text:** {seed_text}
**Source type:** {seed_source}
**Emotional tags:** {', '.join(seed_emotions) if seed_emotions else 'none specified'}
"""
    if seed_notes:
        prompt += f"**Notes:** {seed_notes}\n"

    prompt += f"""
## Voice Guidelines
The output must sound like this agent. Match the voice characteristics below:
{voice_ctx[:2000]}

## Personality Context
The output should reflect these formed opinions, tastes, and behavioral patterns:
{personality_ctx[:2000]}

## Instructions
- Produce a complete, self-contained {medium} piece
- The seed is a starting impulse — interpret it freely, but keep its core feeling
- This should feel like it came from this specific agent, not generic model output
- Avoid hedging, preamble, and conversational filler
- If the medium is text, write the actual piece (not a description of what you'd write)
"""
    return prompt


def build_refine_prompt(
    draft_content: str,
    voice_ctx: str,
    personality_ctx: str,
    iteration: int,
    medium: str,
) -> str:
    """Construct a refinement prompt."""
    return f"""## Task
Refine the following {medium} draft. Improve it while maintaining personality alignment.

## Original Draft (iteration {iteration})
```
{draft_content[:6000]}
```

## Voice Guidelines
{voice_ctx[:1500]}

## Personality Context
{personality_ctx[:1500]}

## Refinement Instructions
- Improve technical quality and coherence
- Strengthen personality alignment — does this sound like the agent?
- Remove generic or filler content that could be from any model
- Preserve the core creative impulse; don't sand away what makes it interesting
- If something feels performed or forced, fix it
- Do not add preamble like "Here's the refined version" — just produce the refined piece
"""


def build_evaluation_prompt(
    draft_content: str,
    voice_ctx: str,
    personality_ctx: str,
    medium: str,
) -> str:
    """Construct an evaluation prompt that returns structured scores."""
    return f"""## Task
Evaluate the following {medium} draft against personality criteria. Be honest — most output should fail.

## Draft
```
{draft_content[:5000]}
```

## Voice Reference
{voice_ctx[:1500]}

## Personality Reference
{personality_ctx[:1500]}

## Criteria
Evaluate on a 0.0–1.0 scale for each:

1. **personality_alignment** — Does this sound like this specific agent? Would someone who knows the agent recognize this as theirs? Or is it generic model output?

2. **originality** — Is this actually interesting? Does it have a point of view, or is it a reheated version of something a million models could produce?

3. **technical_quality** — Is the execution clean? For text: grammar, structure, flow. For image/music prompts: specificity, coherence, evocativeness.

4. **emotional_truth** — Does this feel real or performed? Is there genuine emotional content, or is it going through the motions?

## Output Format
You MUST respond in exactly this JSON format (no other text):
```json
{{
  "personality_alignment": 0.0,
  "originality": 0.0,
  "technical_quality": 0.0,
  "emotional_truth": 0.0,
  "justification": {{
    "personality_alignment": "brief reason",
    "originality": "brief reason",
    "technical_quality": "brief reason",
    "emotional_truth": "brief reason"
  }},
  "overall_notes": "1-2 sentence summary"
}}
```

Be harsh. Average score should typically fall between 0.4 and 0.7. A score above 0.85 should be rare and genuinely earned.
"""


# ---------------------------------------------------------------------------
# JSON parsing from model output
# ---------------------------------------------------------------------------

def parse_json_response(text: str) -> dict[str, Any]:
    """Extract JSON from model output, tolerating markdown fences."""
    # Strip markdown code fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Remove first and last lines (fence markers)
        lines = [l for l in lines[1:] if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    # Find the JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model response")

    return json.loads(cleaned[start : end + 1])


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_draft(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Generate N variants from a seed."""
    seed = load_seed(args.seed, cfg)
    seed_path = Path(args.seed) if Path(args.seed).exists() else (
        resolve_path(cfg, cfg["seed_dir"]) / f"{args.seed}.yaml"
    )
    seed_id = extract_seed_id(seed, seed_path)
    medium = args.medium

    voice_ctx = load_voice_context(cfg)
    personality_ctx = load_personality_context(cfg)
    relevant_personality = extract_relevant_personality(personality_ctx)

    prompt = build_draft_prompt(seed, voice_ctx, relevant_personality, medium)

    if args.dry_run:
        print("=== DRY RUN: Generation Prompt ===")
        print(prompt)
        print(f"\nSeed ID: {seed_id}")
        print(f"Medium: {medium}")
        print(f"Variants: {args.variants}")
        return

    client = create_client(cfg)
    model = cfg["api"]["model"]
    draft_dir = resolve_path(cfg, cfg["draft_dir"])
    draft_dir.mkdir(parents=True, exist_ok=True)

    ext = {"text": "md", "image": "md", "music": "md"}.get(medium, "md")
    timestamp = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H%M%SZ")

    results = []
    for i in range(1, args.variants + 1):
        print(f"Generating variant {i}/{args.variants}...", file=sys.stderr)

        raw = call_model(client, model, prompt, max_tokens=4096)

        filename = f"draft-{seed_id}-{i}.{ext}"
        output_path = draft_dir / filename
        output_path.write_text(raw, encoding="utf-8")

        trace = build_source_trace(
            seed=seed,
            seed_id=f"{seed_id}-v{i}",
            model=model,
            prompt=prompt,
            stage="draft",
            medium=medium,
            variant_num=i,
        )
        save_source_trace(trace, output_path)

        # Also save a per-variant trace
        variant_trace_path = draft_dir / f"source-trace-{seed_id}-v{i}.yaml"
        with open(variant_trace_path, "w") as f:
            yaml.dump(trace, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        results.append({
            "variant": i,
            "file": str(output_path),
            "trace": str(variant_trace_path),
            "chars": len(raw),
        })
        print(f"  → {filename} ({len(raw)} chars)", file=sys.stderr)

    if args.json:
        print(json.dumps({"seed_id": seed_id, "variants": results}, indent=2))
    else:
        print(f"\nGenerated {len(results)} variant(s) for seed {seed_id}")
        for r in results:
            print(f"  [{r['variant']}] {r['file']} ({r['chars']} chars)")


def cmd_refine(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Refine a draft with personality-aware instructions."""
    draft_path = Path(args.draft).expanduser().resolve()
    if not draft_path.exists():
        print(f"ERROR: Draft file not found: {draft_path}", file=sys.stderr)
        sys.exit(1)

    draft_content, trace = load_draft_with_trace(draft_path)

    voice_ctx = load_voice_context(cfg)
    personality_ctx = load_personality_context(cfg)
    relevant_personality = extract_relevant_personality(personality_ctx)

    medium = "text"
    if trace.get("output", {}).get("type"):
        medium = trace["output"]["type"]

    current_content = draft_content
    current_path = draft_path
    current_trace = trace

    for iteration in range(1, args.iterations + 1):
        print(f"Refining iteration {iteration}/{args.iterations}...", file=sys.stderr)

        prompt = build_refine_prompt(
            draft_content=current_content,
            voice_ctx=voice_ctx,
            personality_ctx=relevant_personality,
            iteration=iteration,
            medium=medium,
        )

        client = create_client(cfg)
        model = cfg["api"]["model"]
        refined = call_model(client, model, prompt, max_tokens=4096)

        if iteration == args.iterations:
            # Final iteration: save as -refined
            suffix = "-refined"
            if args.iterations > 1:
                suffix = f"-refined-{args.iterations}x"
            refined_path = draft_path.with_suffix(f"{suffix}{draft_path.suffix}")
        else:
            # Intermediate: overwrite for next iteration
            refined_path = draft_path

        refined_path.write_text(refined, encoding="utf-8")

        # Update trace
        current_trace["generation"]["iterations"] = current_trace["generation"].get("iterations", 0) + 1
        current_trace["generation"]["pipeline_stage"] = "refine"
        save_source_trace(current_trace, refined_path)

        current_content = refined
        current_path = refined_path

        print(f"  → {refined_path.name} ({len(refined)} chars)", file=sys.stderr)

    if args.json:
        result = {
            "input": str(draft_path),
            "output": str(current_path),
            "iterations": args.iterations,
            "chars_before": len(draft_content),
            "chars_after": len(current_content),
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\nRefined {args.iterations} iteration(s)")
        print(f"  Input:  {draft_path} ({len(draft_content)} chars)")
        print(f"  Output: {current_path} ({len(current_content)} chars)")


def cmd_evaluate(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Evaluate a draft against personality criteria."""
    draft_path = Path(args.draft).expanduser().resolve()
    if not draft_path.exists():
        print(f"ERROR: Draft file not found: {draft_path}", file=sys.stderr)
        sys.exit(1)

    draft_content, trace = load_draft_with_trace(draft_path)

    voice_ctx = load_voice_context(cfg)
    personality_ctx = load_personality_context(cfg)
    relevant_personality = extract_relevant_personality(personality_ctx)

    medium = "text"
    if trace.get("output", {}).get("type"):
        medium = trace["output"]["type"]

    prompt = build_evaluation_prompt(draft_content, voice_ctx, relevant_personality, medium)

    print("Evaluating draft...", file=sys.stderr)

    client = create_client(cfg)
    model = cfg["api"]["model"]
    raw_response = call_model(client, model, prompt, max_tokens=2048)

    # Parse the JSON response
    try:
        scores_data = parse_json_response(raw_response)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Could not parse evaluation response: {e}", file=sys.stderr)
        print("Raw response:", file=sys.stderr)
        print(raw_response, file=sys.stderr)
        sys.exit(1)

    # Extract scores
    scores: dict[str, float] = {}
    justifications: dict[str, str] = {}

    for criterion in JUDGMENT_CRITERIA:
        val = scores_data.get(criterion, 0.0)
        if isinstance(val, (int, float)):
            scores[criterion] = max(0.0, min(1.0, float(val)))
        else:
            scores[criterion] = 0.0
            print(f"WARN: Invalid score for {criterion}: {val}", file=sys.stderr)

        justifications[criterion] = scores_data.get("justification", {}).get(criterion, "")

    overall = sum(scores.values()) / len(scores)
    passes = overall >= args.threshold

    overall_notes = scores_data.get("overall_notes", "")

    # Determine recommendation
    if overall >= PUBLICATION_THRESHOLD:
        recommendation = "PUBLISH"
    elif overall >= ARCHIVE_THRESHOLD:
        recommendation = "REVISE"
    else:
        recommendation = "ARCHIVE"

    # Update source trace
    notes_parts = [f"[{recommendation}] {overall_notes}"]
    for crit in JUDGMENT_CRITERIA:
        notes_parts.append(f"  {crit}: {scores[crit]:.2f} — {justifications.get(crit, '')}")

    trace = update_trace_judgment(
        trace=trace,
        scores=scores,
        notes="\n".join(notes_parts),
        threshold=args.threshold,
    )
    save_source_trace(trace, draft_path)

    if args.json:
        result = {
            "file": str(draft_path),
            "scores": scores,
            "average": round(overall, 3),
            "threshold": args.threshold,
            "passes": passes,
            "recommendation": recommendation,
            "justifications": justifications,
            "overall_notes": overall_notes,
        }
        print(json.dumps(result, indent=2))
    else:
        status = "✅ PASS" if passes else "❌ FAIL"
        print(f"\n{status} — {recommendation} (avg: {overall:.2f}, threshold: {args.threshold:.2f})")
        print(f"  File: {draft_path}")
        print()
        for crit in JUDGMENT_CRITERIA:
            bar_len = int(scores[crit] * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"  {crit:25s} {scores[crit]:.2f} {bar}")
            print(f"    → {justifications.get(crit, 'N/A')}")
        print()
        print(f"  Overall: {overall_notes}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="draft_generator",
        description="Creative pipeline: generate, refine, and evaluate personality-aligned drafts.",
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

    # draft
    p_draft = sub.add_parser("draft", help="Generate N variants from a seed")
    p_draft.add_argument("--seed", required=True, help="Path to seed file or seed ID")
    p_draft.add_argument(
        "--variants", "-n",
        type=int,
        default=DEFAULT_VARIANTS,
        help=f"Number of variants to generate (default: {DEFAULT_VARIANTS})",
    )
    p_draft.add_argument(
        "--medium", "-m",
        choices=["text", "image", "music"],
        default="text",
        help="Output medium (default: text)",
    )
    p_draft.add_argument(
        "--dry-run",
        action="store_true",
        help="Show prompt without calling API",
    )

    # refine
    p_refine = sub.add_parser("refine", help="Refine a draft with personality-aware instructions")
    p_refine.add_argument("--draft", required=True, help="Path to draft file")
    p_refine.add_argument(
        "--iterations", "-i",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"Number of refinement iterations (default: {DEFAULT_ITERATIONS})",
    )

    # evaluate
    p_eval = sub.add_parser("evaluate", help="Evaluate a draft against personality criteria")
    p_eval.add_argument("--draft", required=True, help="Path to draft file")
    p_eval.add_argument(
        "--threshold", "-t",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Pass threshold 0.0-1.0 (default: {DEFAULT_THRESHOLD})",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    cfg = load_config(args.config)

    commands = {
        "draft": cmd_draft,
        "refine": cmd_refine,
        "evaluate": cmd_evaluate,
    }

    cmd_fn = commands.get(args.command)
    if not cmd_fn:
        parser.print_help()
        sys.exit(1)

    cmd_fn(args, cfg)


if __name__ == "__main__":
    main()
