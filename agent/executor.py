"""Execution stubs for testing plans."""
from __future__ import annotations

from dataclasses import dataclass

from agent.models import Finding
from agent.planner import TestPlan
from agent.rag import KnowledgeBase


@dataclass
class ExecutionSignal:
    description: str
    confidence: str


def _signals_for_hypothesis(hypothesis: str) -> list[ExecutionSignal]:
    hypothesis_lower = hypothesis.lower()
    if "access control" in hypothesis_lower:
        return [ExecutionSignal("Role-based response discrepancy detected.", "medium")]
    if "jwt" in hypothesis_lower or "session" in hypothesis_lower:
        return [ExecutionSignal("Token validation response variance observed.", "low")]
    if "injection" in hypothesis_lower:
        return [ExecutionSignal("Input handling anomaly on special characters.", "low")]
    if "graphql" in hypothesis_lower:
        return [ExecutionSignal("Schema metadata responded to minimal query.", "low")]
    if "authentication" in hypothesis_lower:
        return [ExecutionSignal("Login flow did not enforce expected checks.", "low")]
    return []


def execute_plan(
    plan: TestPlan, knowledge_base: KnowledgeBase, config: dict
) -> list[Finding]:
    findings: list[Finding] = []
    if not plan.hypotheses:
        return findings

    demo_findings = config.get("scanner", {}).get("generate_findings", True)
    if not demo_findings:
        return findings

    references = plan.references
    for hypothesis in plan.hypotheses:
        signals = _signals_for_hypothesis(hypothesis)
        if not signals:
            continue
        signal_summary = "; ".join(signal.description for signal in signals)
        context_summary = " | ".join(
            [
                f"Endpoints: {', '.join(plan.endpoints)}",
                f"Tech stack: {', '.join(plan.tech_stack) or 'unknown'}",
                f"Constraints: {', '.join(plan.constraints)}",
            ]
        )
        severity = "Medium" if any(sig.confidence == "medium" for sig in signals) else "Low"
        findings.append(
            Finding(
                program=plan.program,
                target=plan.asset,
                title=hypothesis,
                evidence=f"{signal_summary} ({context_summary})",
                severity=severity,
                recommendation="Validate access controls and add server-side checks.",
                references=references,
            )
        )
    return findings
