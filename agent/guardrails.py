"""Scope and safety guardrails for the agent workflow."""
from __future__ import annotations

from urllib.parse import urlparse


def normalize_host(asset: str) -> str:
    parsed = urlparse(asset)
    if parsed.scheme:
        return parsed.netloc
    return asset.split("/")[0]


def is_in_scope(asset: str, config: dict) -> bool:
    scanner_config = config.get("scanner", {})
    allowlist = scanner_config.get("allowlist", [])
    denylist = scanner_config.get("denylist", [])
    host = normalize_host(asset).lower()

    if any(block.lower() in host for block in denylist):
        return False
    if allowlist:
        return any(allowed.lower() in host for allowed in allowlist)
    return True


def safe_mode_enabled(config: dict) -> bool:
    return bool(config.get("scanner", {}).get("safe_mode", True))
