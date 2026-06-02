from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .export_scanner import scan_export_root
from .redaction import redact_manifest
from .tiering import tier_contacts


SAMPLE_EXTRACTOR_CONFIG = {
    "extractor_name": "replace_with_your_local_exporter",
    "notes": [
        "Keep raw exports on local disk only",
        "Write contacts into export_root/contacts/*.json",
        "Write groups into export_root/groups/*.json",
    ],
}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def init_layout(workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    created = [
        workspace / "config",
        workspace / "analysis",
        workspace / "mock_export" / "contacts",
        workspace / "mock_export" / "groups",
    ]
    for path in created:
        path.mkdir(parents=True, exist_ok=True)
    return {"status": "ok", "workspace": str(workspace), "created": [str(path) for path in created]}


def write_sample_config(workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    init_layout(workspace)
    write_json(workspace / "config" / "extractor.example.json", SAMPLE_EXTRACTOR_CONFIG)
    write_json(
        workspace / "mock_export" / "contacts" / "sample_peer.json",
        [{"role": "sender", "text": "placeholder message"}],
    )
    write_json(
        workspace / "mock_export" / "groups" / "sample_group.json",
        [{"role": "sender", "text": "placeholder group message"}],
    )
    return {
        "status": "ok",
        "workspace": str(workspace),
        "files": [
            str(workspace / "config" / "extractor.example.json"),
            str(workspace / "mock_export" / "contacts" / "sample_peer.json"),
            str(workspace / "mock_export" / "groups" / "sample_group.json"),
        ],
    }


def build_handoff(manifest: dict[str, Any], tiers: dict[str, Any]) -> str:
    records = manifest.get("records", [])
    contacts = tiers.get("contacts", [])
    tier_counts = tiers.get("tier_counts", {})
    top_contacts = contacts[:5]
    lines = [
        "# Pipeline Handoff",
        "",
        "## Summary",
        "",
        f"- private records: {manifest.get('private_contact_count', 0)}",
        f"- group records: {manifest.get('group_count', 0)}",
        f"- redacted records: {len(records)}",
        f"- tier counts: {json.dumps(tier_counts, ensure_ascii=False)}",
        "",
        "## Top Public Contacts",
        "",
    ]
    if top_contacts:
        for contact in top_contacts:
            lines.append(
                f"- {contact.get('public_contact_id', 'unknown')}: tier={contact.get('tier', 'Reference')}, "
                f"score={contact.get('score', 0)}, topics={contact.get('topic_tags', [])}"
            )
    else:
        lines.append("- no contacts scored")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Pass the redacted manifest and tier output into the downstream RAG / skill repository.",
        ]
    )
    return "\n".join(lines) + "\n"


def cmd_init_layout(args: argparse.Namespace) -> None:
    print(json.dumps(init_layout(Path(args.workspace)), ensure_ascii=False, indent=2))


def cmd_write_sample_config(args: argparse.Namespace) -> None:
    print(json.dumps(write_sample_config(Path(args.workspace)), ensure_ascii=False, indent=2))


def cmd_scan_export_root(args: argparse.Namespace) -> None:
    result = scan_export_root(Path(args.export_root))
    write_json(Path(args.output), result)
    print(json.dumps({"status": "ok", "output": str(Path(args.output).resolve())}, ensure_ascii=False, indent=2))


def cmd_redact_manifest(args: argparse.Namespace) -> None:
    result = redact_manifest(load_json(Path(args.input)))
    write_json(Path(args.output), result)
    print(json.dumps({"status": "ok", "output": str(Path(args.output).resolve())}, ensure_ascii=False, indent=2))


def cmd_tier_contacts(args: argparse.Namespace) -> None:
    result = tier_contacts(load_json(Path(args.input)))
    write_json(Path(args.output), result)
    print(json.dumps({"status": "ok", "output": str(Path(args.output).resolve())}, ensure_ascii=False, indent=2))


def cmd_build_handoff(args: argparse.Namespace) -> None:
    manifest = load_json(Path(args.manifest))
    tiers = load_json(Path(args.tiers))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_handoff(manifest, tiers), encoding="utf-8")
    print(json.dumps({"status": "ok", "output": str(output.resolve())}, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sanitized WeChat export packaging helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-layout")
    init_parser.add_argument("--workspace", required=True)
    init_parser.set_defaults(func=cmd_init_layout)

    sample_parser = subparsers.add_parser("write-sample-config")
    sample_parser.add_argument("--workspace", required=True)
    sample_parser.set_defaults(func=cmd_write_sample_config)

    scan_parser = subparsers.add_parser("scan-export-root")
    scan_parser.add_argument("--export-root", required=True)
    scan_parser.add_argument("--output", required=True)
    scan_parser.set_defaults(func=cmd_scan_export_root)

    redact_parser = subparsers.add_parser("redact-manifest")
    redact_parser.add_argument("--input", required=True)
    redact_parser.add_argument("--output", required=True)
    redact_parser.set_defaults(func=cmd_redact_manifest)

    tier_parser = subparsers.add_parser("tier-contacts")
    tier_parser.add_argument("--input", required=True)
    tier_parser.add_argument("--output", required=True)
    tier_parser.set_defaults(func=cmd_tier_contacts)

    handoff_parser = subparsers.add_parser("build-handoff")
    handoff_parser.add_argument("--manifest", required=True)
    handoff_parser.add_argument("--tiers", required=True)
    handoff_parser.add_argument("--output", required=True)
    handoff_parser.set_defaults(func=cmd_build_handoff)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

