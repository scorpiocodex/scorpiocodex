"""Static cards: project cards, the skills matrix and the link buttons."""

from __future__ import annotations

from . import kit
from .activity import _panel
from .kit import C, esc, icon, keyframes, mono_width

W = 880

FLOAT_CSS = keyframes("fl", "0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}") + ".fl{animation:fl 5s ease-in-out infinite}"


def project_card(project: dict, login: str) -> str:
    color = project["color"]
    h = 190
    defs, panel = _panel(W, h, color)

    body = [panel, f'<rect x="0" y="3" width="6" height="{h - 6}" fill="{color}" opacity=".9"/>']

    # glowing emblem
    body.append(f'<circle cx="92" cy="{h / 2:.0f}" r="46" fill="{color}" fill-opacity=".10" stroke="{color}" stroke-opacity=".4"/>')
    body.append(icon(project["icon"], 66, h / 2 - 26, 52, color, width=1.5, cls="fl"))

    body.append(f'<text class="d" x="170" y="66" font-size="36" fill="{C["text"]}">{kit.esc(project["name"])}</text>')
    body.append(f'<text class="m" x="170" y="92" font-size="15" fill="{C["muted"]}">github.com/{esc(login)}/{esc(project["repo"])}</text>')

    # top-right badge: how to install, or what it was
    badge = f"pip install {project['pypi']}" if project.get("pypi") else "internship project"
    bw = 24 + mono_width(badge, 14)
    body.append(
        f'<rect x="{W - 44 - bw:.1f}" y="44" width="{bw:.1f}" height="30" rx="15" fill="{color}" fill-opacity=".10" stroke="{color}" stroke-opacity=".5"/>'
        f'<text class="m" x="{W - 44 - bw / 2:.1f}" y="63" font-size="14" text-anchor="middle" fill="{C["text"]}">{esc(badge)}</text>'
    )

    body.append(f'<text x="170" y="126" font-size="22" fill="#C9D1D9">{esc(project["short"])}</text>')

    x, y = 170.0, h - 52
    for i, chip in enumerate(project["chips"]):
        s, w = kit.pill(x, y, chip, color=color, icon_name=None, delay=i * 0.6)
        body.append(s)
        x += w + 10

    return kit.svg(
        W, h, "".join(body),
        title=f"{project['name']} project card",
        desc=f"{project['name']}: {project['short']}. Built with {', '.join(project['chips'])}.",
        css=kit.PILL_CSS + FLOAT_CSS, fonts=("display", "mono"), defs=defs,
    )


def skills_card(stack: list[dict]) -> str:
    left, avail, chip_h, row_gap = 220, W - 220 - 44, 30, 10
    layout, y = [], 34.0
    for gi, group in enumerate(stack):
        x, rows, start_y = 0.0, 0, y
        placed = []
        for item in group["items"]:
            w = 24 + mono_width(item, 14)
            if x + w > avail and x > 0:
                x, rows = 0.0, rows + 1
            placed.append((item, x, rows, w))
            x += w + 8
        height = (rows + 1) * chip_h + rows * row_gap
        layout.append((group, placed, start_y, height))
        y = start_y + height + 28
    h = int(y - 28 + 34)

    defs, panel = _panel(W, h, C["purple"])
    body = [panel]
    n = 0
    for gi, (group, placed, start_y, height) in enumerate(layout):
        color = group["color"]
        mid = start_y + height / 2
        body.append(f'<circle cx="52" cy="{mid:.1f}" r="5" fill="{color}"/>')
        body.append(f'<text class="m" x="68" y="{mid + 5:.1f}" font-size="14" letter-spacing="1.6" fill="{C["muted"]}">{esc(group["area"].upper())}</text>')
        for item, cx, row, _w in placed:
            s, _ = kit.pill(left + cx, start_y + row * (chip_h + row_gap), item, color=color, icon_name=None, delay=(n % 9) * 0.5)
            body.append(s)
            n += 1
        if gi < len(layout) - 1:
            sep = start_y + height + 14
            body.append(f'<path d="M44 {sep:.1f}H{W - 44}" stroke="{C["border"]}" stroke-opacity=".6"/>')

    summary = "; ".join(f"{g['area']}: {', '.join(g['items'])}" for g in stack)
    return kit.svg(W, h, "".join(body), title="Technical stack", desc=summary, css=kit.PILL_CSS, fonts=("mono",), defs=defs)


def button(kind: str, label: str, color: str) -> str:
    size = 15
    h = 44
    icon_name = {"portfolio": "globe", "email": "mail"}.get(kind)
    text_x = 48
    w = text_x + mono_width(label, size) + 22
    glyph = (
        icon(icon_name, 18, 12, 20, color, width=2)
        if icon_name
        else f'<rect x="18" y="12" width="20" height="20" rx="4" fill="none" stroke="{color}" stroke-width="2"/>'
        f'<text class="mb" x="28" y="27" font-size="12" text-anchor="middle" fill="{color}">in</text>'
    )
    defs = (
        f'<linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["surface"]}"/><stop offset="1" stop-color="{C["bg"]}"/></linearGradient>'
    )
    body = (
        f'<rect x=".5" y=".5" width="{w - 1:.1f}" height="{h - 1}" rx="22" fill="url(#b)" stroke="{color}" stroke-opacity=".6"/>'
        f"{glyph}"
        f'<text class="mb" x="{text_x}" y="28" font-size="{size}" fill="{C["text"]}">{esc(label)}</text>'
    )
    return kit.svg(int(w) + 1, h, body, title=label, desc=f"Link button: {label}", fonts=("mono-bold",), defs=defs)
