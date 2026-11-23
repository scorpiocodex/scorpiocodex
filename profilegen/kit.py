"""Shared pieces for the SVG generators: palette, fonts, icons and helpers.

Rules every generated image follows (tests/test_assets.py enforces most):

* Self-contained. GitHub serves repo SVGs under a strict policy, so nothing
  is loaded from outside: no scripts, no external fonts or images. Fonts are
  embedded as base64 subsets (SIL OFL, see assets/fonts/OFL.txt).
* Content is visible by default. Animations hide things only inside
  @keyframes, so a renderer that skips animation, or a reader who prefers
  reduced motion, still sees the finished image.
* Facts live in the README text and alt attributes; the images decorate.
"""

from __future__ import annotations

import base64
import random
from functools import lru_cache
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

# Portfolio design tokens (app/globals.css, default dark theme).
C = {
    "bg": "#0D1117",
    "surface": "#161B22",
    "surface2": "#21262D",
    "border": "#30363D",
    "accent": "#58A6FF",
    "purple": "#7C3AED",
    "glow": "#00E5FF",
    "text": "#E6EDF3",
    "muted": "#8B949E",
    "success": "#3FB950",
    "warn": "#F0883E",
}

SANS = "-apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
DISPLAY = "'Space Grotesk', " + SANS
MONO = (
    "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, "
    "'Liberation Mono', monospace"
)
MONO_ADVANCE = 0.6  # JetBrains Mono: every glyph is 0.6 em wide

_FONTS = {
    "display": ("Space Grotesk", 700, "space-grotesk-latin-700-normal.woff2"),
    "display-medium": ("Space Grotesk", 500, "space-grotesk-latin-500-normal.woff2"),
    "mono": ("JetBrains Mono", 400, "jetbrains-mono-latin-400-normal.woff2"),
    "mono-bold": ("JetBrains Mono", 700, "jetbrains-mono-latin-700-normal.woff2"),
}


@lru_cache(maxsize=None)
def _font_face(key: str) -> str:
    family, weight, filename = _FONTS[key]
    data = base64.b64encode((FONT_DIR / filename).read_bytes()).decode("ascii")
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


def font_faces(*keys: str) -> str:
    return "".join(_font_face(k) for k in keys)


def esc(text: str) -> str:
    return escape(text, quote=True)


BASE_CSS = (
    f"text{{font-family:{SANS}}}"
    f".d{{font-family:{DISPLAY};font-weight:700}}"
    f".dm{{font-family:{DISPLAY};font-weight:500}}"
    f".m{{font-family:{MONO}}}"
    f".mb{{font-family:{MONO};font-weight:700}}"
    "@media (prefers-reduced-motion: reduce){*{animation:none !important}}"
)


def svg(
    width: int,
    height: int,
    body: str,
    *,
    title: str,
    desc: str,
    css: str = "",
    fonts: tuple[str, ...] = (),
    defs: str = "",
) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-labelledby="t d">\n'
        f'<title id="t">{esc(title)}</title>\n<desc id="d">{esc(desc)}</desc>\n'
        f"<defs>{defs}</defs>\n"
        f"<style>{font_faces(*fonts)}{BASE_CSS}{css}</style>\n"
        f"{body}\n</svg>\n"
    )


def keyframes(name: str, body: str) -> str:
    return f"@keyframes {name}{{{body}}}"


def stars(width: int, height: int, count: int, seed: int, *, avoid=()) -> str:
    """Deterministic twinkling dots. `avoid` is a list of (x0, y0, x1, y1)."""
    rng = random.Random(seed)
    out = []
    while len(out) < count:
        x, y = rng.uniform(6, width - 6), rng.uniform(6, height - 6)
        if any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in avoid):
            continue
        r = rng.choice((0.8, 1.0, 1.2, 1.6))
        delay = rng.uniform(0, 6)
        dur = rng.uniform(3, 7)
        out.append(
            f'<circle class="tw" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" '
            f'opacity="{rng.choice((0.35, 0.5, 0.7)):.2f}" '
            f'style="animation-delay:{delay:.1f}s;animation-duration:{dur:.1f}s"/>'
        )
    return "".join(out)


TWINKLE_CSS = keyframes("tw", "0%,100%{opacity:.15}50%{opacity:.9}") + (
    ".tw{animation:tw 5s ease-in-out infinite}"
)

# 24x24 line icons, drawn with the stroke of the wrapping <g>.
ICONS = {
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "database": (
        '<path d="M4 6c0-1.66 3.58-3 8-3s8 1.34 8 3-3.58 3-8 3-8-1.34-8-3zM4 6v6c0 1.66 '
        "3.58 3 8 3s8-1.34 8-3V6M4 12v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6\"/>"
    ),
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5"/>',
    "box": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3zM12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
    "chat": (
        '<path d="M4 5h16v11H9l-5 4V5z"/>'
        '<path d="M8.5 10.5h.01M12 10.5h.01M15.5 10.5h.01"/>'
    ),
    "atom": (
        '<ellipse cx="12" cy="12" rx="10" ry="4"/>'
        '<ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/>'
        '<ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/>'
        '<circle cx="12" cy="12" r="1.2"/>'
    ),
    "eye": (
        '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/>'
        '<circle cx="12" cy="12" r="3"/>'
    ),
    "lock": (
        '<rect x="5" y="11" width="14" height="10" rx="2"/>'
        '<path d="M8 11V8a4 4 0 0 1 8 0v3"/>'
    ),
    "globe": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18"/>'
    ),
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.2 8.3-8 9-4.8-.7-8-4.5-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "cloud": '<path d="M7 18a4 4 0 0 1-.6-7.95A6 6 0 0 1 18 9.5 4.5 4.5 0 0 1 17.5 18H7z"/><path d="M12 17v-6M9.5 13.5L12 11l2.5 2.5"/>',
    "chip": '<path d="M7 7h10v10H7zM10 10h4v4h-4zM9 3v4M15 3v4M9 17v4M15 17v4M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
}


def icon(name: str, x: float, y: float, size: float, color: str, *, width: float = 1.8, cls: str = "") -> str:
    scale = size / 24
    klass = f' class="{cls}"' if cls else ""
    # Position on the outer group and animate the inner one: a CSS `transform`
    # animation replaces the SVG transform attribute on the same element.
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.3f})">'
        f'<g{klass} fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
        f'stroke-linejoin="round">{ICONS[name]}</g></g>'
    )


def mono_width(text: str, size: float) -> float:
    return len(text) * size * MONO_ADVANCE


def pill(x: float, y: float, label: str, *, color: str, icon_name: str | None, size: int = 14, delay: float = 0.0, h: int = 30) -> tuple[str, float]:
    """A rounded label with an optional icon. Returns (svg, width)."""
    pad = 12
    icon_w = 22 if icon_name else 0
    w = pad * 2 + icon_w + mono_width(label, size)
    parts = [
        f'<g class="pl" style="animation-delay:{delay:.2f}s">',
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{h/2}" '
        f'fill="{color}" fill-opacity="0.08" stroke="{color}" stroke-opacity="0.45"/>',
    ]
    cx = x + pad
    if icon_name:
        parts.append(icon(icon_name, cx, y + (h - 16) / 2, 16, color, width=2))
        cx += icon_w
    parts.append(
        f'<text class="m" x="{cx:.1f}" y="{y + h / 2 + size * 0.35:.1f}" font-size="{size}" '
        f'fill="{C["text"]}">{esc(label)}</text></g>'
    )
    return "".join(parts), w


PILL_CSS = keyframes("pl", "0%,100%{opacity:.78}50%{opacity:1}") + ".pl{animation:pl 4.5s ease-in-out infinite}"
