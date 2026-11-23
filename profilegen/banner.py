"""The hero banner: headline, a self-typing terminal and a row of stack pills."""

from __future__ import annotations

from . import kit
from .kit import C, esc, icon, keyframes, mono_width

W, H = 880, 340
TERM = {"x": 462, "y": 30, "w": 374, "h": 226}
TERM_BG = "#0A0E14"
LOOP = 16.0  # seconds for one pass of the terminal


def _terminal(facts: dict, meta: dict) -> tuple[str, str]:
    """Returns (svg, css). Each line is revealed by a cover rectangle that
    slides off it in `steps()`, so the typing is driven by CSS alone."""
    size = 14
    adv = mono_width("x", size)  # width of one character
    x0 = TERM["x"] + 20
    base_y = TERM["y"] + 62
    step_y = 24
    slack = 3  # extra characters of cover, so a fallback font can't clip the end

    lines = [
        # (kind, text, start_s, end_s)
        ("cmd", "ls ~/projects", 0.6, 1.5),
        ("out", "bakeriq/  scorpiowatch/  nyxora/", 1.8, 2.3),
        ("cmd", "cd bakeriq && pytest -q", 2.8, 4.3),
        ("ok", f"{facts['tests']} passed", 4.9, 5.4),
        ("cmd", "pip install scorpiowatch nyxora", 6.1, 8.1),
        ("ok", "both installed from PyPI", 8.8, 9.6),
        ("end", "github.com/scorpiocodex", 10.3, 11.6),
    ]

    css = [keyframes("tfade", "0%,92%{opacity:1}99%,100%{opacity:0}")]
    css.append(".tf{animation:tfade %ss linear infinite}" % LOOP)
    css.append(keyframes("blink", "0%,49%{opacity:1}50%,100%{opacity:0}"))
    css.append(".cur{animation:blink 1.1s steps(1) infinite}")

    body = []
    for i, (kind, text, start, end) in enumerate(lines):
        y = base_y + i * step_y
        prefix_w = 0.0
        parts = []
        if kind == "cmd":
            parts.append(f'<text class="mb" x="{x0}" y="{y}" font-size="{size}" fill="{C["accent"]}">$</text>')
            parts.append(f'<text class="m" x="{x0 + 2 * adv:.1f}" y="{y}" font-size="{size}" fill="{C["text"]}">{esc(text)}</text>')
            prefix_w = 2 * adv
        elif kind == "out":
            parts.append(f'<text class="m" x="{x0}" y="{y}" font-size="{size}" fill="{C["muted"]}" xml:space="preserve">{esc(text)}</text>')
        elif kind == "ok":
            parts.append(icon("check", x0, y - 12, 14, C["success"], width=2.6))
            parts.append(f'<text class="m" x="{x0 + 2 * adv:.1f}" y="{y}" font-size="{size}" fill="{C["success"]}">{esc(text)}</text>')
            prefix_w = 2 * adv
        else:  # end line with the blinking cursor
            parts.append(f'<text class="mb" x="{x0}" y="{y}" font-size="{size}" fill="{C["glow"]}">&gt;</text>')
            parts.append(f'<text class="m" x="{x0 + 2 * adv:.1f}" y="{y}" font-size="{size}" fill="{C["text"]}">{esc(text)}</text>')
            prefix_w = 2 * adv
            cur_x = x0 + prefix_w + len(text) * adv + 3
            parts.append(f'<rect class="cur" x="{cur_x:.1f}" y="{y - 12}" width="{adv:.1f}" height="16" fill="{C["glow"]}"/>')
        body.append("".join(parts))

        n_chars = len(text) + (2 if kind != "out" else 0)
        run = n_chars + slack  # characters the cover travels; the slack is the margin for a wider fallback font
        shift = run * adv
        # At rest the cover sits `slack` characters past the text; it starts on the
        # line's left edge and slides right in one step per character.
        cover_x = x0 + shift
        cover_w = TERM["x"] + TERM["w"] - x0
        body.append(
            f'<rect class="cv{i}" x="{cover_x:.1f}" y="{y - 16}" width="{cover_w + shift:.1f}" height="24" fill="{TERM_BG}"/>'
        )
        s_pct, e_pct = start / LOOP * 100, end / LOOP * 100
        css.append(
            keyframes(
                f"cv{i}",
                f"0%,{s_pct:.2f}%{{transform:translateX({-shift:.1f}px);"
                f"animation-timing-function:steps({run},end)}}"
                f"{e_pct:.2f}%,100%{{transform:translateX(0)}}",
            )
        )
        css.append(f".cv{i}{{animation:cv{i} {LOOP}s linear infinite}}")

    t = TERM
    svg = [
        # soft glow behind the window
        f'<rect x="{t["x"]}" y="{t["y"]}" width="{t["w"]}" height="{t["h"]}" rx="12" fill="{C["glow"]}" opacity=".10" filter="url(#blur)"/>',
        f'<rect x="{t["x"]}" y="{t["y"]}" width="{t["w"]}" height="{t["h"]}" rx="12" fill="{TERM_BG}" stroke="{C["border"]}"/>',
        f'<path d="M{t["x"]} {t["y"] + 30}H{t["x"] + t["w"]}" stroke="{C["border"]}"/>',
        f'<circle cx="{t["x"] + 18}" cy="{t["y"] + 15}" r="5" fill="#FF5F56"/>',
        f'<circle cx="{t["x"] + 36}" cy="{t["y"] + 15}" r="5" fill="#FFBD2E"/>',
        f'<circle cx="{t["x"] + 54}" cy="{t["y"] + 15}" r="5" fill="#27C93F"/>',
        f'<text class="m" x="{t["x"] + 74}" y="{t["y"] + 19}" font-size="12" fill="{C["muted"]}">{esc(meta["title"])}</text>',
        f'<g clip-path="url(#termclip)"><g class="tf">{"".join(body)}</g></g>',
        f'<text class="m" x="{t["x"] + t["w"] / 2}" y="{t["y"] + t["h"] + 18}" text-anchor="middle" font-size="10" '
        f'letter-spacing="3" fill="{C["muted"]}" opacity=".7">{esc(meta["label"])}</text>',
    ]
    return "".join(svg), "".join(css)


def render(profile: dict) -> str:
    stars = kit.stars(W, H, 46, seed=7, avoid=[(TERM["x"] - 6, TERM["y"] - 6, TERM["x"] + TERM["w"] + 6, TERM["y"] + TERM["h"] + 24)])
    term_svg, term_css = _terminal(profile["bakeriq_facts"], profile["terminal"])

    head = profile["headline"]
    sub = profile["subheadline"]
    headline = (
        f'<text class="d" x="44" y="92" font-size="40" fill="{C["text"]}">{esc(head[0])}</text>'
        f'<text class="d" x="44" y="140" font-size="40" fill="url(#hero)">{esc(head[1])}</text>'
        f'<text class="d" x="44" y="188" font-size="40" fill="{C["text"]}">{esc(head[2])}</text>'
    )
    subtitle = "".join(
        f'<text x="44" y="{222 + i * 24}" font-size="17" fill="{C["muted"]}">{esc(line)}</text>'
        for i, line in enumerate(sub)
    )

    # pill row
    pills, x = [], 44.0
    palette = [C["glow"], C["accent"], C["purple"], C["success"], C["warn"], C["glow"]]
    for i, p in enumerate(profile["banner_pills"]):
        s, w = kit.pill(x, 288, p["label"], color=palette[i % len(palette)], icon_name=p["icon"], delay=i * 0.5)
        pills.append(s)
        x += w + 10
    assert x - 10 <= W - 44, "pill row overflows the banner"

    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg"]}"/><stop offset="1" stop-color="#101626"/></linearGradient>'
        f'<radialGradient id="g1" cx="0.88" cy="0.05" r="0.6"><stop offset="0" stop-color="{C["purple"]}" stop-opacity=".38"/><stop offset="1" stop-color="{C["purple"]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="g2" cx="0.06" cy="0.98" r="0.55"><stop offset="0" stop-color="{C["glow"]}" stop-opacity=".20"/><stop offset="1" stop-color="{C["glow"]}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="hero" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["glow"]}"/><stop offset="1" stop-color="{C["accent"]}"/></linearGradient>'
        f'<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["glow"]}"/><stop offset=".55" stop-color="{C["accent"]}"/><stop offset="1" stop-color="{C["purple"]}"/></linearGradient>'
        f'<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["glow"]}" stop-opacity="0"/><stop offset=".5" stop-color="{C["glow"]}" stop-opacity=".07"/><stop offset="1" stop-color="{C["glow"]}" stop-opacity="0"/></linearGradient>'
        '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="#fff" opacity=".07"/></pattern>'
        '<filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>'
        f'<clipPath id="termclip"><rect x="{TERM["x"]}" y="{TERM["y"] + 31}" width="{TERM["w"]}" height="{TERM["h"] - 32}" rx="10"/></clipPath>'
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
    )

    css = (
        kit.TWINKLE_CSS
        + kit.PILL_CSS
        + keyframes("scan", f"0%{{transform:translateY(-70px)}}100%{{transform:translateY({H + 10}px)}}")
        + ".sc{animation:scan 9s linear infinite}"
        + term_css
    )

    body = (
        f'<g clip-path="url(#card)">'
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'
        f'<rect width="{W}" height="{H}" fill="url(#g1)"/><rect width="{W}" height="{H}" fill="url(#g2)"/>'
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>'
        f"{stars}"
        f'<rect class="sc" y="0" width="{W}" height="70" fill="url(#scan)"/>'
        f'<rect width="{W}" height="3" fill="url(#bar)"/>'
        f"</g>"
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{C["border"]}"/>'
        f"{headline}{subtitle}{term_svg}{''.join(pills)}"
    )
    return kit.svg(
        W,
        H,
        body,
        title=f"{profile['name']}: building full-stack apps and dev tools",
        desc="Banner with the headline 'Building Full-Stack Apps and Dev Tools', a simulated terminal session "
        "listing the bakeriq, scorpiowatch and nyxora projects, and stack labels for FastAPI, PostgreSQL, React, "
        "Celery, Docker and Ollama LLMs.",
        css=css,
        fonts=("display", "mono", "mono-bold"),
        defs=defs,
    )
