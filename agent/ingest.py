"""Ingest new vulnerability reports."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import requests
from bs4 import BeautifulSoup


@dataclass
class Report:
    title: str
    url: str
    body: str


@dataclass
class ReportSummary:
    title: str
    url: str
    technique: str
    root_cause: str
    remediation: str
    raw_text: str


def fetch_new_reports(config: dict) -> list[Report]:
    """Fetch recent public reports from HackerOne Hacktivity.

    This is a lightweight HTML scrape so teams can replace it with their
    own official feeds or APIs.
    """
    url = config["sources"]["hackerone_rss"]
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    reports: list[Report] = []
    for item in soup.select(".fade-out"):
        title = item.get_text(strip=True)
        link = item.get("href") or url
        reports.append(Report(title=title, url=link, body=""))

    return reports


def summarize_reports(reports: Iterable[Report], config: dict) -> list[ReportSummary]:
    """Summarize reports into technique-oriented knowledge blocks."""
    summaries: list[ReportSummary] = []
    for report in reports:
        summaries.append(
            ReportSummary(
                title=report.title,
                url=report.url,
                technique="Extract key exploitation technique.",
                root_cause="Identify underlying root cause.",
                remediation="Summarize remediation guidance.",
                raw_text=report.body,
            )
        )
    return summaries
