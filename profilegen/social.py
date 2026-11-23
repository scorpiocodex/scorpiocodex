"""Social-preview cards (1280x640) for the project repositories.

GitHub shows these when a repo link is shared (LinkedIn, Slack, X, ...). They are
static: no animation, because they are exported to PNG for the repository settings.
Only facts already in data/profile.json appear on them.
"""

from __future__ import annotations

from . import kit
from .kit import C, esc, icon, mono_width

W, H = 1280, 640


def render(project: dict, profile: dict) -> str:
    color = project["color"]
    name, repo = project["name"], project["repo"]
    handle = profile["handle"]

    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg"]}"/><stop offset="1" stop-color="#101626"/></linearGradient>'
        f'<radialGradient id="g1" cx=".80" cy=".50" r=".55"><stop offset="0" stop-color="{color}" stop-opacity=".30"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="g2" cx=".02" cy=".02" r=".5"><stop offset="0" stop-color="{C["purple"]}" stop-opacity=".25"/><stop offset="1" stop-color="{C["purple"]}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{color}"/><stop offset=".6" stop-color="{C["accent"]}"/><stop offset="1" stop-color="{C["purple"]}"/></linearGradient>'
        '<pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#fff" opacity=".07"/></pattern>'
        '<filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="24"/></filter>'
    )

    # chips
    chips, x = [], 80.0
    for chip in project["chips"]:
        s, w = kit.pill(x, 396, chip, color=color, icon_name=None, size=22, h=46)
        chips.append(s)
        x += w + 14

    # bottom line: how to install it, or what it was
    if project.get("pypi"):
        cmd = f"pip install {project['pypi']}"
        bw = 76 + mono_width(cmd, 28)
        bottom = (
            f'<rect x="80" y="500" width="{bw:.0f}" height="64" rx="14" fill="{C["bg"]}" stroke="{color}" stroke-opacity=".6" stroke-width="2"/>'
            f'<text class="mb" x="106" y="543" font-size="28" fill="{color}">$</text>'
            f'<text class="m" x="140" y="543" font-size="28" fill="{C["text"]}">{esc(cmd)}</text>'
        )
    else:
        bottom = (
            f'<text x="80" y="543" font-size="30" fill="#C9D1D9">Built during an internship at Digital Mesh Softech</text>'
        )

    body = (
        f'<clipPath id="card"><rect width="{W}" height="{H}"/></clipPath>'
        f'<g clip-path="url(#card)">'
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'
        f'<rect width="{W}" height="{H}" fill="url(#g1)"/><rect width="{W}" height="{H}" fill="url(#g2)"/>'
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>'
        f"{kit.stars(W, H, 70, seed=11 + len(repo), avoid=[(60, 40, 860, 640), (860, 150, 1180, 490)])}"
        f'<rect width="{W}" height="8" fill="url(#bar)"/></g>'
        # emblem
        f'<circle cx="1020" cy="320" r="170" fill="{color}" opacity=".16" filter="url(#blur)"/>'
        f'<circle cx="1020" cy="320" r="150" fill="{color}" fill-opacity=".10" stroke="{color}" stroke-opacity=".55" stroke-width="2"/>'
        f"{icon(project['icon'], 940, 240, 160, color, width=1.4)}"
        # text
        f'<text class="m" x="80" y="100" font-size="26" fill="{C["muted"]}">github.com/{esc(handle)}/{esc(repo)}</text>'
        f'<text class="d" x="80" y="244" font-size="104" fill="{C["text"]}">{esc(name)}</text>'
        f'<rect x="84" y="272" width="120" height="8" rx="4" fill="{color}"/>'
        f'<text x="80" y="352" font-size="38" fill="#C9D1D9">{esc(project["short"])}</text>'
        f'{"".join(chips)}{bottom}'
        f'<text x="80" y="606" font-size="22" fill="{C["muted"]}">{esc(profile["name"])} · {esc(profile["role"])}</text>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" fill="none" stroke="{C["border"]}"/>'
    )
    return kit.svg(
        W,
        H,
        body,
        title=f"{name} social preview",
        desc=f"Preview card for the {name} repository: {project['short']}. Built with {', '.join(project['chips'])}.",
        css="",  # static: it is exported to PNG
        fonts=("display", "mono", "mono-bold"),
        defs=defs,
    )
