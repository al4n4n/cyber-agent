"""Entry point for the cyber agent workflow."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from agent.ingest import fetch_new_reports, summarize_reports
from agent.rag import KnowledgeBase
from agent.report import write_reports
from agent.scanner import scan_targets


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def run(config: dict) -> None:
    reports = fetch_new_reports(config)
    summaries = summarize_reports(reports, config)

    knowledge_base = KnowledgeBase.from_config(config)
    knowledge_base.ingest(summaries)
    knowledge_base.persist()

    findings = scan_targets(config, knowledge_base)
    write_reports(findings, config)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cyber agent orchestrator")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("agent/config.yaml"),
        help="Path to configuration YAML",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    run(config)


if __name__ == "__main__":
    main()
