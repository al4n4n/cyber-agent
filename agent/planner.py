"""Planning logic for targeted vulnerability testing."""
from __future__ import annotations

from dataclasses import dataclass

from agent.guardrails import safe_mode_enabled
from agent.rag import KnowledgeBase
from agent.recon import AssetProfile


@dataclass
class TestPlan:
    program: str
    asset: str
    endpoints: list[str]
    tech_stack: list[str]
    recon_notes: list[str]
    hypotheses: list[str]
    steps: list[str]
    constraints: list[str]
    references: list[str]


def _derive_hypotheses(knowledge: list[str], tech_stack: list[str]) -> list[str]:
    hypotheses: list[str] = []
    corpus = " ".join(knowledge).lower()
    if "jwt" in corpus or "token" in corpus:
        hypotheses.append("JWT handling or session validation weakness")
    if "access control" in corpus or "idor" in corpus:
        hypotheses.append("Broken access control on sensitive resources")
    if "sql" in corpus:
        hypotheses.append("Input validation issue that could enable injection")
    if "xss" in corpus:
        hypotheses.append("Reflected or stored script injection in dynamic fields")
    if "graphql" in tech_stack:
        hypotheses.append("GraphQL schema exposure or excessive query depth")
    if "auth" in tech_stack:
        hypotheses.append("Authentication flow misconfiguration")
    if not hypotheses:
        hypotheses.append("General input validation and authorization gaps")
    return hypotheses


def build_plan(
    profile: AssetProfile, knowledge_base: KnowledgeBase, config: dict
) -> TestPlan:
    query = f"{profile.program} {profile.asset} {' '.join(profile.tech_stack)}"
    context = knowledge_base.search(query)
    references = list(dict.fromkeys(chunk.source for chunk in context))
    hypotheses = _derive_hypotheses([chunk.text for chunk in context], profile.tech_stack)

    constraints: list[str] = []
    if safe_mode_enabled(config):
        constraints.append("Operate in safe mode (no destructive actions).")
    rate_limit = config.get("scanner", {}).get("rate_limit_per_minute")
    if rate_limit:
        constraints.append(f"Rate limit: {rate_limit} requests per minute.")
    constraints.append("Stay within declared scope and rate limits.")

    steps = [
        "Review recon notes and enumerate prioritized endpoints.",
        "Run low-impact probes for each hypothesis.",
        "Escalate to verification steps only on positive signals.",
        "Summarize evidence and impact for reporting.",
    ]

    return TestPlan(
        program=profile.program,
        asset=profile.asset,
        endpoints=profile.endpoints,
        tech_stack=profile.tech_stack,
        recon_notes=profile.notes,
        hypotheses=hypotheses,
        steps=steps,
        constraints=constraints,
        references=references,
    )
