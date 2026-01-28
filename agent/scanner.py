"""Heuristic scanner for bug bounty targets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from agent.rag import KnowledgeBase


@dataclass
class Finding:
    program: str
    target: str
    title: str
    evidence: str
    severity: str
    recommendation: str
    references: list[str]


def scan_targets(config: dict, knowledge_base: KnowledgeBase) -> list[Finding]:
    findings: list[Finding] = []
    for target in config["scanner"]["targets"]:
        program = target["program"]
        for asset in target["scope"]:
            query = f"{program} {asset} vulnerability technique"
            context = knowledge_base.search(query)
            references = [chunk.source for chunk in context]
            findings.append(
                Finding(
                    program=program,
                    target=asset,
                    title="Potential input validation issue",
                    evidence="Heuristic signals matched past patterns; validate manually.",
                    severity="Medium",
                    recommendation="Add strict server-side validation and logging.",
                    references=references,
                )
            )
    return findings
