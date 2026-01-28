"""Heuristic scanner for bug bounty targets."""
from __future__ import annotations

from agent.executor import execute_plan
from agent.models import Finding
from agent.planner import build_plan
from agent.rag import KnowledgeBase
from agent.recon import run_recon


def scan_targets(config: dict, knowledge_base: KnowledgeBase) -> list[Finding]:
    findings: list[Finding] = []
    profiles = run_recon(config)
    for profile in profiles:
        plan = build_plan(profile, knowledge_base, config)
        findings.extend(execute_plan(plan, knowledge_base, config))
    return findings
