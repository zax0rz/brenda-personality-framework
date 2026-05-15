# Pipeline Scripts

Genericized pipeline tools for the personality persistence framework. No hardcoded paths, no infrastructure assumptions. Point at your workspace and go.

## Dependencies

- Python 3.10+
- `pyyaml` (configuration parsing)
- `click` (CLI interface)
- OpenAI-compatible API client for LLM calls (optional, for draft_generator and drift_detection)

Install:
```bash
pip install pyyaml click openai
```

## Configuration

All scripts accept a `--config` flag pointing to a YAML config file:

```yaml
# pipeline-config.yaml
workspace: /path/to/agent/workspace
journal_dir: journal/
seed_dir: seeds/
draft_dir: drafts/
archive_dir: archive/
personality_file: PERSONALITY.md
voice_file: VOICE.md

api:
  base_url: "https://api.example.com/v1"
  model: "model-name"
  api_key_env: API_KEY  # reads from environment variable
```

## Scripts

### seed_manager.py

Extract, review, archive, and analyze creative seeds from journal entries.

```bash
# Extract seeds from today's journal
python seed_manager.py --config pipeline-config.yaml extract

# Review incubating seeds (promote or archive)
python seed_manager.py --config pipeline-config.yaml review

# Get stats on seed pipeline
python seed_manager.py --config pipeline-config.yaml stats

# Archive rejected seeds
python seed_manager.py --config pipeline-config.yaml archive
```

### draft_generator.py

Generate creative drafts from approved seeds.

```bash
# Generate variants from a seed
python draft_generator.py --config pipeline-config.yaml draft --seed seeds/2026-05-15-001.yaml

# Refine the best variant
python draft_generator.py --config pipeline-config.yaml refine --draft drafts/2026-05-15-001-best.png

# Evaluate a draft against personality criteria
python draft_generator.py --config pipeline-config.yaml evaluate --draft drafts/2026-05-15-001-best.png
```

### drift_detection.py

Monitor personality and voice drift over time.

```bash
# Check for banned phrases in recent output
python drift_detection.py --config pipeline-config.yaml banned --dir output/

# Measure voice similarity to VOICE.md baseline
python drift_detection.py --config pipeline-config.yaml voice --output recent-post.md

# Full coherence report
python drift_detection.py --config pipeline-config.yaml report
```

## Development Status

- `seed_manager.py`: Functional (extract, review, archive, stats)
- `draft_generator.py`: Stub — needs model routing implementation
- `drift_detection.py`: Stub — needs banned phrase matching and similarity scoring

## Contributing

Scripts should be:
- Self-contained (no imports from parent directories)
- Config-driven (no hardcoded paths)
- Testable with mock data
- Language-agnostic in their interface (YAML config, not Python imports)
