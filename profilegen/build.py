"""Render every image. `python3 build.py` from the repository root."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from . import activity, banner, cards, github_data, social, validate
from .kit import C, ROOT

OUT = ROOT / "assets" / "generated"
SOCIAL_OUT = ROOT / "assets" / "social"


def load_profile() -> dict:
    return json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))


def render_all(profile: dict, data: dict) -> dict[str, str]:
    files = {
        "banner.svg": banner.render(profile),
        "stats.svg": activity.stats_card(data),
        "languages.svg": activity.languages_card(data),
        "heatmap.svg": activity.heatmap_card(data),
        "skills.svg": cards.skills_card(profile["stack"]),
        "btn-portfolio.svg": cards.button("portfolio", "Portfolio", C["glow"]),
        "btn-linkedin.svg": cards.button("linkedin", "LinkedIn", C["accent"]),
        "btn-email.svg": cards.button("email", "Email", C["purple"]),
    }
    for project in profile["projects"]:
        files[f"project-{project['repo'].lower()}.svg"] = cards.project_card(project, profile["handle"])
    return files


def render_social(profile: dict) -> dict[str, str]:
    """1280x640 repository preview cards, one per project (exported to PNG by hand)."""
    return {f"{p['repo'].lower()}.svg": social.render(p, profile) for p in profile["projects"]}


def main(argv: list[str]) -> int:
    check = "--check" in argv
    profile = load_profile()
    pypi = sum(1 for p in profile["projects"] if p.get("pypi"))
    data = github_data.fetch(profile["handle"], profile["excluded_repos_from_language_stats"], pypi)
    files = render_all(profile, data)
    social_files = render_social(profile)

    everything = {**files, **{f"social/{name}": text for name, text in social_files.items()}}
    bad = [msg for name, text in everything.items() for msg in validate.problems(text, name)]
    if bad:
        print("Validation failed:\n  " + "\n  ".join(bad), file=sys.stderr)
        return 1

    target = Path(tempfile.mkdtemp(prefix="profile-assets-")) if check else OUT
    social_target = target / "social" if check else SOCIAL_OUT
    for folder, group in ((target, files), (social_target, social_files)):
        folder.mkdir(parents=True, exist_ok=True)
        for name, text in group.items():
            (folder / name).write_text(text, encoding="utf-8", newline="\n")
    verb = "checked (not written to the repo)" if check else "wrote"
    print(
        f"{verb} {len(files)} images + {len(social_files)} social cards; "
        f"{data['contributions_total']} contributions, {data['commits']} commits"
    )
    return 0
