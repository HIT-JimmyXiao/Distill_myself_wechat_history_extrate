# Distill Myself WeChat History Extrate

A sanitized local workflow for post-export WeChat archive scanning, redaction, contact tiering, and safe handoff into downstream skill / RAG pipelines.

[中文 README](README.md)

## Overview

This repository does not publish real chat histories.

It publishes a reusable open-source skeleton for:

1. scanning a local export tree,
2. redacting identifiers and path traces,
3. assigning contact tiers with a reproducible score,
4. generating a safe handoff file for the downstream repository.

The public release intentionally excludes:

- raw chat records,
- real contact names, nicknames, or `wxid`,
- SQLCipher keys, local database copies, or device paths,
- any metadata that can be reversed into private identity.

## Highlights

- `scan-export-root` builds a normalized manifest from any local export tree
- `redact-manifest` replaces identifiers, filenames, and text fragments with safe public tokens
- `tier-contacts` assigns `S / A / B / Reference` labels with a clear scoring rule
- `build-handoff` prepares the downstream input for `Distill_myself_RAG-Skill`
- example schema and sample data are included for easy replacement

## Repository Layout

```text
Distill_myself_wechat_history_extrate/
├── docs/
├── sample_data/
├── src/wechat_history_extrate/
├── LICENSE
├── README.md
├── README_EN.md
└── pyproject.toml
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .

wechat-release init-layout --workspace ./demo_workspace
wechat-release write-sample-config --workspace ./demo_workspace
wechat-release scan-export-root --export-root ./demo_workspace/mock_export --output ./demo_workspace/analysis/export_manifest.json
wechat-release redact-manifest --input ./demo_workspace/analysis/export_manifest.json --output ./demo_workspace/analysis/export_manifest.redacted.json
wechat-release tier-contacts --input ./sample_data/contact_stats.example.json --output ./demo_workspace/analysis/contact_tiers.json
wechat-release build-handoff --manifest ./demo_workspace/analysis/export_manifest.redacted.json --tiers ./demo_workspace/analysis/contact_tiers.json --output ./demo_workspace/analysis/pipeline_handoff.md
```

## Scoring Rule

```text
volume_score   = min(log(1 + message_count) / log(1 + 5000), 1)
activity_score = min(active_days, 180) / 180
relation_score = clamp(relation_strength, 0, 1)

final_score = 0.50 * volume_score
            + 0.30 * activity_score
            + 0.20 * relation_score
```

Tier cutoffs:

- `S`: `score >= 0.80`
- `A`: `0.62 <= score < 0.80`
- `B`: `0.42 <= score < 0.62`
- `Reference`: everything else

## Downstream Handoff

This repository stops at sanitized structured outputs.

To continue toward RAG bundle generation, Codex skill drafting, and automation interfaces, use:

- [Distill_myself_RAG-Skill](https://github.com/HIT-JimmyXiao/Distill_myself_RAG-Skill)

