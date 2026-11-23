"""Checks every generated SVG must pass before it is committed.

GitHub renders repository SVGs as images under a strict policy, and a profile
page is public, so the rules are conservative: nothing active, nothing that
loads from outside, nothing hidden when animations don't run.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

MAX_BYTES = 80_000

_FORBIDDEN_TAGS = ("script", "foreignobject", "iframe", "object", "embed", "image", "use", "a", "set")
_KEYFRAMES = re.compile(r"@keyframes\s+[\w-]+\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", re.S)
_EXTERNAL_URL = re.compile(r"url\(\s*(?!#|data:font/woff2;base64,)", re.I)
_REF = re.compile(r"(?:xlink:)?href\s*=\s*[\"'](?!#)", re.I)
_EVENT = re.compile(r"\son[a-z]+\s*=", re.I)
_HIDDEN = re.compile(r"(?<![\w-])opacity\s*[:=]\s*[\"']?0(?:\.0+)?[\"']?\s*(?:[;}\"'/>]|$)|visibility\s*:\s*hidden|display\s*:\s*none", re.I)


def problems(svg_text: str, name: str = "svg") -> list[str]:
    out: list[str] = []
    if len(svg_text.encode("utf-8")) > MAX_BYTES:
        out.append(f"{name}: larger than {MAX_BYTES} bytes")
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as e:
        return [f"{name}: not well-formed XML ({e})"]

    tags = {el.tag.split("}")[-1].lower() for el in root.iter()}
    for tag in _FORBIDDEN_TAGS:
        if tag in tags:
            out.append(f"{name}: forbidden element <{tag}>")
    if "title" not in tags or "desc" not in tags:
        out.append(f"{name}: missing <title> or <desc>")

    lowered = svg_text.lower()
    if "javascript:" in lowered:
        out.append(f"{name}: javascript: URL")
    if "@import" in lowered:
        out.append(f"{name}: @import")
    if _EVENT.search(svg_text):
        out.append(f"{name}: inline event handler")
    if _EXTERNAL_URL.search(svg_text):
        out.append(f"{name}: url() that is not an internal reference or an embedded font")
    if _REF.search(svg_text):
        out.append(f"{name}: href that is not an internal reference")
    if re.search(r"https?://(?!www\.w3\.org/)", svg_text):
        out.append(f"{name}: external URL")

    # Hiding is only allowed inside @keyframes (so content is visible when animation is off).
    without_keyframes = _KEYFRAMES.sub("", svg_text)
    if _HIDDEN.search(without_keyframes):
        out.append(f"{name}: element hidden outside @keyframes")
    if "prefers-reduced-motion" not in svg_text and "@keyframes" in svg_text:
        out.append(f"{name}: animated but no prefers-reduced-motion rule")
    return out
