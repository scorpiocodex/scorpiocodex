"""Cards built from live GitHub data: activity stats, top languages, contribution map."""

from __future__ import annotations

from datetime import date

from . import kit
from .kit import C, esc, keyframes

W = 880

LANG_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178C6",
    "JavaScript": "#F1E05A",
    "CSS": "#8A63D2",
    "HTML": "#E34C26",
    "Shell": "#89E051",
    "Dockerfile": "#4D7A93",
    "Mako": "#7E858D",
    "PLpgSQL": "#336790",
}
FALLBACK_COLOR = "#8B949E"

LEVEL_FILL = {
    "NONE": "#161B22",
    "FIRST_QUARTILE": "#0B3C4A",
    "SECOND_QUARTILE": "#0E6B83",
    "THIRD_QUARTILE": "#12A4C4",
    "FOURTH_QUARTILE": "#00E5FF",
}

GROW_CSS = (
    keyframes("gr", "from{transform:scaleX(0)}to{transform:scaleX(1)}")
    + ".gr{transform-box:fill-box;transform-origin:0 50%;animation:gr 1.2s cubic-bezier(.2,.7,.2,1) both}"
)
RISE_CSS = (
    keyframes("rs", "from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}")
    + ".rs{animation:rs .7s ease both}"
)


def _panel(w: int, h: int, accent: str = C["glow"]) -> tuple[str, str]:
    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg"]}"/><stop offset="1" stop-color="#101626"/></linearGradient>'
        f'<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["glow"]}"/><stop offset=".55" stop-color="{C["accent"]}"/><stop offset="1" stop-color="{C["purple"]}"/></linearGradient>'
        f'<radialGradient id="gl" cx=".95" cy="0" r=".7"><stop offset="0" stop-color="{accent}" stop-opacity=".16"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="card"><rect width="{w}" height="{h}" rx="16"/></clipPath>'
    )
    body = (
        f'<g clip-path="url(#card)"><rect width="{w}" height="{h}" fill="url(#bg)"/>'
        f'<rect width="{w}" height="{h}" fill="url(#gl)"/><rect width="{w}" height="3" fill="url(#bar)"/></g>'
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{C["border"]}"/>'
    )
    return defs, body


def _label(x: float, y: float, text: str, anchor: str = "start") -> str:
    return (
        f'<text class="m" x="{x}" y="{y}" font-size="13" letter-spacing="2.4" text-anchor="{anchor}" '
        f'fill="{C["muted"]}">{esc(text)}</text>'
    )


# --- activity stats ---------------------------------------------------------


def stats_card(data: dict) -> str:
    h = 292
    defs, panel = _panel(W, h)
    total = data["contributions_total"]
    tiles = [
        ("Commits", data["commits"], C["glow"]),
        ("Pull requests", data["pull_requests"], C["accent"]),
        ("Issues", data["issues"], C["purple"]),
        ("Public repos", data["public_repos"], C["success"]),
        ("PyPI packages", data["pypi_packages"], C["warn"]),
    ]
    body = [panel, _label(44, 44, "ACTIVITY  /  LAST 12 MONTHS")]
    body.append(f'<text class="d rs" x="44" y="132" font-size="92" fill="url(#bar)">{total}</text>')
    body.append(f'<text class="rs" x="48" y="162" font-size="19" fill="{C["muted"]}" style="animation-delay:.1s">contributions on GitHub</text>')

    col_w, row_h, x0, y0 = 152, 80, 416, 70
    for i, (name, value, color) in enumerate(tiles):
        cx = x0 + (i % 3) * col_w
        cy = y0 + (i // 3) * row_h
        body.append(
            f'<g class="rs" style="animation-delay:{0.12 * (i + 1):.2f}s">'
            f'<rect x="{cx}" y="{cy}" width="{col_w - 14}" height="{row_h - 14}" rx="10" fill="{color}" fill-opacity=".07" stroke="{color}" stroke-opacity=".35"/>'
            f'<text class="d" x="{cx + 14}" y="{cy + 36}" font-size="34" fill="{C["text"]}">{value}</text>'
            f'<text x="{cx + 14}" y="{cy + 58}" font-size="16" fill="{C["muted"]}">{esc(name)}</text></g>'
        )

    # share of commits / pull requests / issues, drawn as one growing bar
    parts = [("Commits", data["commits"], C["glow"]), ("Pull requests", data["pull_requests"], C["accent"]), ("Issues", data["issues"], C["purple"])]
    denom = sum(v for _, v, _ in parts) or 1
    bx, by, bw, bh = 44, 232, W - 88, 14
    body.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="7" fill="{C["surface2"]}"/>')
    cursor = float(bx)
    for i, (_, value, color) in enumerate(parts):
        seg = bw * value / denom
        if seg <= 0:
            continue
        body.append(
            f'<rect class="gr" x="{cursor:.1f}" y="{by}" width="{max(seg - 3, 2):.1f}" height="{bh}" rx="7" fill="{color}" '
            f'style="animation-delay:{0.3 + i * 0.2:.1f}s"/>'
        )
        cursor += seg
    body.append(_label(44, 272, "COMMITS / PULL REQUESTS / ISSUES"))

    return kit.svg(
        W, h, "".join(body),
        title="GitHub activity over the last 12 months",
        desc=f"{total} contributions: {data['commits']} commits, {data['pull_requests']} pull requests, "
        f"{data['issues']} issues. {data['public_repos']} public repositories and {data['pypi_packages']} PyPI packages.",
        css=RISE_CSS + GROW_CSS, fonts=("display", "mono"), defs=defs,
    )


# --- languages ---------------------------------------------------------------


def top_languages(languages: dict[str, int], limit: int = 5) -> list[tuple[str, float]]:
    total = sum(languages.values())
    if not total:
        return []
    ranked = sorted(languages.items(), key=lambda kv: kv[1], reverse=True)
    top = [(name, size / total * 100) for name, size in ranked[:limit]]
    rest = sum(size for _, size in ranked[limit:]) / total * 100
    if rest >= 1:
        top.append(("Other", rest))
    return top


def languages_card(data: dict) -> str:
    items = top_languages(data["languages"])
    rows = (len(items) + 2) // 3
    h = 128 + rows * 36
    defs, panel = _panel(W, h, C["accent"])
    body = [panel, _label(44, 44, "TOP LANGUAGES  /  BY CODE IN MY PUBLIC REPOS")]

    bx, by, bw, bh = 44, 64, W - 88, 18
    body.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="9" fill="{C["surface2"]}"/>')
    cursor = float(bx)
    for i, (name, pct) in enumerate(items):
        seg = bw * pct / 100
        color = LANG_COLORS.get(name, FALLBACK_COLOR)
        body.append(
            f'<rect class="gr" x="{cursor:.1f}" y="{by}" width="{max(seg - 3, 2):.1f}" height="{bh}" rx="9" fill="{color}" '
            f'style="animation-delay:{i * 0.15:.2f}s"/>'
        )
        cursor += seg

    col_w = (W - 88) / 3
    for i, (name, pct) in enumerate(items):
        x = 44 + (i % 3) * col_w
        y = 124 + (i // 3) * 36
        color = LANG_COLORS.get(name, FALLBACK_COLOR)
        body.append(
            f'<g class="rs" style="animation-delay:{0.1 * i + 0.3:.2f}s"><circle cx="{x + 7}" cy="{y - 6}" r="7" fill="{color}"/>'
            f'<text x="{x + 24}" y="{y}" font-size="20" fill="{C["text"]}">{esc(name)}</text>'
            f'<text class="m" x="{x + col_w - 28}" y="{y}" font-size="17" text-anchor="end" fill="{C["muted"]}">{pct:.1f}%</text></g>'
        )
    summary = ", ".join(f"{n} {p:.1f}%" for n, p in items)
    return kit.svg(
        W, h, "".join(body),
        title="Top languages across my public repositories",
        desc=f"Share of code by language: {summary}.",
        css=RISE_CSS + GROW_CSS, fonts=("mono",), defs=defs,
    )


# --- contribution map -------------------------------------------------------


def heatmap_card(data: dict) -> str:
    h = 214
    defs, panel = _panel(W, h)
    cell, gap, x0, y0 = 12, 3, 44, 80
    body = [panel, _label(44, 40, "CONTRIBUTION MAP")]
    body.append(_label(W - 44, 40, f"{data['contributions_total']} IN THE LAST YEAR", "end"))

    last_month, last_x = None, -999.0
    cols = []
    for ci, week in enumerate(data["weeks"]):
        x = x0 + ci * (cell + gap)
        first = date.fromisoformat(week[0]["date"])
        if first.month != last_month and x - last_x >= 44:
            body.append(f'<text class="m" x="{x}" y="66" font-size="12" fill="{C["muted"]}">{first.strftime("%b")}</text>')
            last_month, last_x = first.month, x
        rects = []
        for day in week:
            wd = (date.fromisoformat(day["date"]).weekday() + 1) % 7  # Sunday = 0
            fill = LEVEL_FILL.get(day["level"], LEVEL_FILL["NONE"])
            rects.append(f'<rect x="{x}" y="{y0 + wd * (cell + gap)}" width="{cell}" height="{cell}" rx="3" fill="{fill}"/>')
        cols.append(f'<g class="cl" style="animation-delay:{ci * 0.018:.3f}s">{"".join(rects)}</g>')
    body.append("".join(cols))

    # legend
    lx = W - 44 - 5 * (cell + 4) - 60
    body.append(f'<text class="m" x="{lx}" y="{h - 16}" font-size="12" text-anchor="end" fill="{C["muted"]}">Less</text>')
    for i, key in enumerate(("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")):
        body.append(f'<rect x="{lx + 10 + i * (cell + 4)}" y="{h - 26}" width="{cell}" height="{cell}" rx="3" fill="{LEVEL_FILL[key]}"/>')
    body.append(f'<text class="m" x="{lx + 18 + 5 * (cell + 4)}" y="{h - 16}" font-size="12" fill="{C["muted"]}">More</text>')

    # a slow scan across the grid
    body.append(f'<rect class="sw" x="{x0}" y="{y0 - 6}" width="90" height="{7 * (cell + gap) + 6}" fill="url(#sweep)"/>')
    defs += (
        f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["glow"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{C["glow"]}" stop-opacity=".14"/><stop offset="1" stop-color="{C["glow"]}" stop-opacity="0"/></linearGradient>'
    )
    css = (
        keyframes("cl", "from{opacity:0}to{opacity:1}")
        + ".cl{animation:cl .5s ease both}"
        + keyframes("sw", f"0%{{transform:translateX(-100px)}}100%{{transform:translateX({W}px)}}")
        + ".sw{animation:sw 8s linear infinite}"
    )
    return kit.svg(
        W, h, "".join(body),
        title="Contribution map for the last 12 months",
        desc=f"A heat map of daily GitHub contributions over the last year, {data['contributions_total']} in total.",
        css=css, fonts=("mono",), defs=defs,
    )
