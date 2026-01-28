"""Shared dataclasses for the agent workflow."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Finding:
    program: str
    target: str
    title: str
    evidence: str
    severity: str
    recommendation: str
    references: list[str]
