"""Read-only GitHub data for the generated cards. Standard library only.

Transport:
  * In GitHub Actions (GITHUB_ACTIONS set) a GITHUB_TOKEN is required and used
    directly. There is no silent fallback: if the token is missing the build
    fails instead of publishing stale or empty numbers.
  * On a developer machine, with no token in the environment, calls go through
    the `gh` CLI, which uses whatever login the developer already has.

Only public data is requested.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request

API = "https://api.github.com"
TIMEOUT = 30

CONTRIBUTIONS_QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes { name isArchived stargazerCount primaryLanguage { name } }
    }
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""


class GitHubError(RuntimeError):
    pass


def _token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None


def _use_cli() -> bool:
    if _token():
        return False
    if os.environ.get("GITHUB_ACTIONS"):
        raise GitHubError("GITHUB_TOKEN is not set in GitHub Actions; refusing to fall back.")
    if not shutil.which("gh"):
        raise GitHubError("No GITHUB_TOKEN and no `gh` CLI available.")
    return True


def _http(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {_token()}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "profile-readme-generator",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:  # include the status but never the token
        raise GitHubError(f"{method} {path} failed with HTTP {e.code}") from None


def rest(path: str) -> dict:
    if _use_cli():
        out = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
        if out.returncode != 0:
            raise GitHubError(f"gh api {path} failed: {out.stderr.strip()[:200]}")
        return json.loads(out.stdout)
    return _http("GET", path)


def graphql(query: str, **variables: str) -> dict:
    if _use_cli():
        args = ["gh", "api", "graphql", "-f", f"query={query}"]
        for key, value in variables.items():
            args += ["-f", f"{key}={value}"]
        out = subprocess.run(args, capture_output=True, text=True, timeout=60)
        if out.returncode != 0:
            raise GitHubError(f"gh api graphql failed: {out.stderr.strip()[:200]}")
        payload = json.loads(out.stdout)
    else:
        payload = _http("POST", "/graphql", {"query": query, "variables": variables})
    if payload.get("errors"):
        raise GitHubError(f"GraphQL errors: {payload['errors'][0].get('message', '')[:200]}")
    return payload["data"]


def fetch(login: str, excluded_repos: list[str], pypi_count: int) -> dict:
    """Everything the stats, language and heatmap cards need."""
    user = graphql(CONTRIBUTIONS_QUERY, login=login)["user"]
    contrib = user["contributionsCollection"]
    repos = [r for r in user["repositories"]["nodes"] if not r["isArchived"]]

    languages: dict[str, int] = {}
    for repo in repos:
        if repo["name"] in excluded_repos:
            continue
        for lang, size in rest(f"/repos/{login}/{repo['name']}/languages").items():
            languages[lang] = languages.get(lang, 0) + size

    weeks = contrib["contributionCalendar"]["weeks"]
    return {
        "login": login,
        "contributions_total": contrib["contributionCalendar"]["totalContributions"],
        "commits": contrib["totalCommitContributions"],
        "pull_requests": contrib["totalPullRequestContributions"],
        "issues": contrib["totalIssueContributions"],
        "reviews": contrib["totalPullRequestReviewContributions"],
        "public_repos": user["repositories"]["totalCount"],
        "pypi_packages": pypi_count,
        "languages": languages,
        "weeks": [
            [{"date": d["date"], "count": d["contributionCount"], "level": d["contributionLevel"]} for d in w["contributionDays"]]
            for w in weeks
        ],
    }
