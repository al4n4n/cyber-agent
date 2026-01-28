"""Reconnaissance stubs for target profiling."""
from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse

from agent.guardrails import is_in_scope


@dataclass
class AssetProfile:
    program: str
    asset: str
    host: str
    endpoints: list[str]
    tech_stack: list[str]
    notes: list[str] = field(default_factory=list)


def _infer_endpoints(asset: str) -> list[str]:
    parsed = urlparse(asset)
    base_path = parsed.path.rstrip("/") or "/"
    candidates = {base_path, "/login", "/api", "/graphql"}
    return sorted(candidates)


def _infer_tech_stack(asset: str, endpoints: list[str]) -> list[str]:
    tech_stack: list[str] = []
    asset_lower = asset.lower()
    if "graphql" in asset_lower or "/graphql" in endpoints:
        tech_stack.append("graphql")
    if "api" in asset_lower or "/api" in endpoints:
        tech_stack.append("rest-api")
    if "login" in asset_lower or "/login" in endpoints:
        tech_stack.append("auth")
    return tech_stack


def run_recon(config: dict) -> list[AssetProfile]:
    profiles: list[AssetProfile] = []
    for target in config.get("scanner", {}).get("targets", []):
        program = target["program"]
        for asset in target["scope"]:
            if not is_in_scope(asset, config):
                continue
            parsed = urlparse(asset)
            host = parsed.netloc or asset.split("/")[0]
            endpoints = _infer_endpoints(asset)
            tech_stack = _infer_tech_stack(asset, endpoints)
            profiles.append(
                AssetProfile(
                    program=program,
                    asset=asset,
                    host=host,
                    endpoints=endpoints,
                    tech_stack=tech_stack,
                    notes=[
                        "Recon is running in stub mode; no live requests sent.",
                        f"Discovered endpoints: {', '.join(endpoints)}",
                        f"Inferred tech stack: {', '.join(tech_stack) or 'none'}",
                    ],
                )
            )
    return profiles
