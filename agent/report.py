"""Report writer for findings."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from agent.scanner import Finding


def write_reports(findings: list[Finding], config: dict) -> None:
    reports_dir = Path(config["output"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)

    for finding in findings:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = reports_dir / f"{finding.program}-{timestamp}.md"
        content = render_report(finding)
        filename.write_text(content, encoding="utf-8")


def render_report(finding: Finding) -> str:
    data = asdict(finding)
    references = "\n".join([f"- {ref}" for ref in data["references"]]) or "- None"
    return "\n".join(
        [
            f"# {data['title']}",
            "",
            f"**Program:** {data['program']}",
            f"**Target:** {data['target']}",
            f"**Severity:** {data['severity']}",
            "",
            "## Evidence",
            data["evidence"],
            "",
            "## Recommendation",
            data["recommendation"],
            "",
            "## References",
            references,
        ]
    )
