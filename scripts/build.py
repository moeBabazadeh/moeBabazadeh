#!/usr/bin/env python3
"""Generate the SVG artwork for the profile README.

Edit the content below and run `python3 scripts/build.py`. Every image is
written twice into assets/, once per GitHub theme (`-dark.svg`, `-light.svg`),
and README.md picks between them with <picture>. SVGs in assets/ that the
build no longer produces are removed.

Images rendered through <img> can't load web fonts, so all text uses system
font stacks. Card text is wrapped by hand: keep description lines short.
"""

import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
MONO_ADVANCE = 0.6  # width of one monospace glyph, in em
SANS_ADVANCE = 0.58  # rough average for semibold sans text, in em

# Dark follows babazadeh.dev (navy + mint); light keeps the same accent, deepened for contrast.
THEMES = {
    "dark": {
        "bg": "#0a192f", "bg2": "#112240", "surface": "#112240", "border": "#233554",
        "heading": "#e6f1ff", "body": "#a8b2d1", "muted": "#8892b0",
        "accent": "#64ffda", "accent_text": "#64ffda",
        "chip_bg": "#0a192f", "chip_text": "#a8b2d1", "grid": "#1d3150",
    },
    "light": {
        "bg": "#f0fdfa", "bg2": "#ffffff", "surface": "#ffffff", "border": "#d0d7de",
        "heading": "#0a192f", "body": "#424a53", "muted": "#59636e",
        "accent": "#0d9488", "accent_text": "#0f766e",
        "chip_bg": "#f6f8fa", "chip_text": "#424a53", "grid": "#cfe6e1",
    },
}

HEADER = {
    "prompt": "~ $ whoami",
    "name": "Moe Babazadeh",
    "role": "CTO · Neuroject",
    "tagline": "I architect AI-driven platforms and scalable digital products.",
    "chips": ["AI platforms", "Web · iOS · Android", "Embedded hardware", "Cloud & DevOps"],
}

# Dates and commit counts are from my own commits only (all branches, all my
# author emails), not the repos' full history.
STATS = [
    ("11.8k+", "commits since 2021"),
    ("10+", "products live"),
    ("5 devices", "hardware in production"),
    ("0.5B+", "sensor records logged"),
    ("2 apps", "on App Store + Play"),
]

WIDE = [
    {
        "slug": "neurobuild",
        "label": "Neuroject · 2024 → now · CTO since 2026",
        "title": "NeuroBuild",
        "lines": [
            "The alignment layer for construction enterprises: a cloud-native, multi-tenant",
            "platform that connects BIM, schedules, budgets and risks into traceable decisions.",
            "Now adding AI: natural-language access to project data and early risk warnings.",
        ],
        "chips": ["Next.js", "React 19", "Laravel 11", "Vapor", "AWS", "Autodesk APS", "AG Grid"],
        "stat": "4,750 commits · 5 repos",
        "visual": "city",
    },
    {
        "slug": "smartclaim",
        "label": "SmartClaim · 2026 → now",
        "title": "SmartClaim",
        "lines": [
            "AI-assisted R&D tax credit claims for the UK, Ireland, Australia and South Africa.",
            "I work across the FastAPI + pgvector API, the SvelteKit app and the TypeScript SDK,",
            "and added its security gates: secret scanning, Semgrep and Trivy on every PR.",
        ],
        "chips": ["FastAPI", "OpenAI", "pgvector", "SvelteKit", "TypeScript", "Playwright", "AWS"],
        "stat": "500 commits · 5 repos",
        "visual": "claim",
    },
]

COMPANY = {
    "slug": "0and1",
    "label": "0&1 · Lead frontend developer · 2021 → 2025",
    "title": "0&1",
    "tagline": "Edtech for universities and schools, shipped end to end: web, mobile and the hardware in the room.",
    "stat": "6,600 commits · 29 repos",
    "tiles": [
        ("appstore", "App Store", "2 apps live"),
        ("play", "Google Play", "2 apps live"),
        ("chip", "Hardware", "readers + beacons"),
        ("globe", "Web", "10+ apps & sites"),
    ],
    "chips": ["React", "Next.js", "React Native", "Expo", "MUI", "Redux", "Firebase", "Office.js", "ESP-IDF", "Zephyr"],
}

# Figures from the one university I have numbers for, so the real totals are higher.
ATTENDUM = {
    "slug": "attendum",
    "label": "0&1 · Hardware + apps · 2023 → 2025",
    "title": "Attendum",
    "tagline": "Attendance monitoring live at UK and US universities. At just one of them:",
    "glyph": "beacon",
    "tiles": [
        ("chip", "200+", "devices online"),
        ("database", "3M+", "records in 2 years"),
        ("school", "100+", "classrooms"),
        ("calendar", "10K+", "classes covered"),
    ],
    "platforms": ["iOS", "Android", "Hardware", "Web"],
    "chips": ["ESP32", "nRF52840", "Zephyr", "Expo"],
}

# Devices that run in the field but have no public code.
LOGGER = {
    "slug": "logger",
    "label": "Weather telemetry · In production",
    "title": "Logger",
    "tagline": "Weather stations that take several sensors each and send their logs home over GSM.",
    "glyph": "station",
    "tiles": [
        ("clock", "15+ years", "online"),
        ("database", "0.5B+", "records logged"),
        ("tower", "50+", "active stations"),
        ("signal", "GSM", "multi-sensor uplink"),
    ],
    "platforms": ["Hardware", "Firmware"],
    "chips": ["GSM", "Multi-sensor", "Telemetry"],
}

HARDWARE = [
    {
        "slug": "epc",
        "label": "Process control",
        "title": "EPC",
        "lines": [
            "Electronic pressure and flow controller:",
            "embedded hardware and firmware that hold",
            "pressure and flow at their setpoints.",
        ],
        "platforms": ["Hardware", "In production"],
        "chips": ["Firmware", "Pressure", "Flow"],
        "glyph": "gauge",
    },
    {
        "slug": "mini-plc",
        "label": "Automation",
        "title": "Mini PLC",
        "lines": [
            "A compact PLC controller built on STM",
            "microcontrollers: the board and firmware",
            "for automation on a small footprint.",
        ],
        "platforms": ["Hardware", "In production"],
        "chips": ["STM", "Firmware", "PLC"],
        "glyph": "plc",
    },
]

# Smaller 0&1 products, three to a row. Labels stay short to clear the glyph.
PRODUCTS = [
    {
        "slug": "active-class",
        "label": "LMS · 2021 → 2024",
        "title": "Active-Class",
        "lines": [
            "An LMS with live exam proctoring",
            "and Azure Face identity checks.",
            "I built the user dashboard, the",
            "Office add-in and the website.",
        ],
        "platforms": ["Web", "Office add-in"],
        "chips": ["React"],
        "glyph": "slides",
    },
    {
        "slug": "education-guide",
        "label": "Mobile app · 2024",
        "title": "Education Guide",
        "lines": [
            "Helps students starting university",
            "get to know their course, campus,",
            "city and career options. A React",
            "Native app on both stores + site.",
        ],
        "platforms": ["iOS", "Android", "Web"],
        "chips": ["Expo"],
        "glyph": "phone",
    },
    {
        "slug": "school-how",
        "label": "Tutoring · 2022 → 2023",
        "title": "School.how",
        "lines": [
            "Tutoring for every child:",
            "diagnostic tests, courses, quizzes",
            "and live 1-to-1 video lessons.",
            "I built the dashboard and site.",
        ],
        "platforms": ["Web"],
        "chips": ["Next.js", "MUI", "VideoSDK"],
        "glyph": "video",
    },
]

HOBBIES = [
    {
        "slug": "pulse-iot",
        "label": "IoT · 2026",
        "title": "Pulse IoT",
        "lines": [
            "Device telemetry on plain shared",
            "PHP hosting: rollups, alarms with",
            "hysteresis, OTA firmware, reports.",
            "No Composer, npm or build step.",
        ],
        "chips": ["PHP 8", "Vanilla JS", "OTA"],
        "glyph": "pulse",
    },
    {
        "slug": "photo-dedup",
        "label": "macOS · 2026",
        "title": "Photo Dedup",
        "lines": [
            "Native macOS app that finds",
            "duplicate and look-alike photos by",
            "how they look. Fully offline, and",
            "nothing is ever deleted.",
        ],
        "chips": ["Swift", "SwiftUI", "Vision"],
        "glyph": "photos",
    },
    {
        "slug": "matrix-keypad",
        "label": "Open source · 2023",
        "title": "matrix-keypad-freertos",
        "lines": [
            "Reads matrix keypads as a FreeRTOS",
            "task, with built-in debouncing and",
            "configurable layouts and pin maps.",
            "Portable across microcontrollers.",
        ],
        "chips": ["C", "FreeRTOS"],
        "glyph": "keypad",
    },
]

# (when, organisation, role, note, marker): marker True = current, False = past, None = education.
JOURNEY = [
    ("2026 → now", "Neuroject", "CTO",
     "The alignment layer for construction enterprises: BIM, schedules, budgets and risks, now with AI.", True),
    ("2026 → now", "Neuroship", "Chief Full-Stack Engineer · contract", "", True),
    ("2024 → 2026", "Neuroject", "Chief Full-Stack Engineer",
     "Led the architecture and build of NeuroBuild on Next.js, Laravel, AWS Amplify and Vapor.", False),
    ("2021 → 2024", "0&1", "Lead Frontend Developer → Technical Consultant",
     "LMS and exam proctoring with Azure Face API, attendance hardware, apps on both stores.", False),
    ("2020 → 2021", "Alget.nl", "Senior Frontend Developer",
     "A React marketplace that brought local supermarkets online.", False),
    ("2012 → 2020", "Niknam Electronic Rayan", "Software → Senior Software Engineer",
     "IoT platforms and connected devices: monitoring, live GPS tracking and data visualisation.", False),
    ("2007 → 2012", "Freelance", "Web developer",
     "Websites and web apps in PHP, JavaScript and jQuery.", False),
    ("2008 → 2016", "University of Tabriz", "BSc Electrical Eng. (Control) · MSc Nanotechnology",
     "Control systems, robotics and RoboCup.", None),
]

LINKS = [
    {"slug": "web", "label": "babazadeh.dev", "icon": "globe"},
    {"slug": "linkedin", "label": "LinkedIn", "icon": "linkedin"},
    {"slug": "email", "label": "moe@babazadeh.dev", "icon": "mail"},
]

STORES = [
    {"slug": "attendum-appstore", "store": "App Store", "app": "Attendum", "icon": "appstore"},
    {"slug": "attendum-play", "store": "Google Play", "app": "Attendum", "icon": "play"},
    {"slug": "education-guide-appstore", "store": "App Store", "app": "Education Guide", "icon": "appstore"},
    {"slug": "education-guide-play", "store": "Google Play", "app": "Education Guide", "icon": "play"},
]


# ---------------------------------------------------------------- primitives


def svg(width, height, body, title, style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">\n'
        f"<title>{escape(title)}</title>\n"
        f"<style>{style}</style>\n{body}\n</svg>\n"
    )


def text(x, y, content, *, size, fill, font=SANS, weight=400, anchor="start", spacing=0, cls="", style=""):
    attrs = f'x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}"'
    if anchor != "start":
        attrs += f' text-anchor="{anchor}"'
    if spacing:
        attrs += f' letter-spacing="{spacing}"'
    if cls:
        attrs += f' class="{cls}"'
    if style:
        attrs += f' style="{style}"'
    return f"<text {attrs}>{escape(content)}</text>"


def chip_width(label, size):
    return len(label) * size * MONO_ADVANCE + size * 1.6


def chips(x, y, labels, t, size=11, gap=6, accent=0):
    """A row of monospace pills with its top-left corner at (x, y); the first `accent` are highlighted."""
    out, h = [], size + 13
    for n, label in enumerate(labels):
        w = chip_width(label, size)
        if n < accent:
            fill, stroke, color = f'fill="{t["accent"]}" fill-opacity="0.12"', f'stroke="{t["accent"]}" stroke-opacity="0.6"', t["accent_text"]
        else:
            fill, stroke, color = f'fill="{t["chip_bg"]}"', f'stroke="{t["border"]}"', t["chip_text"]
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" {fill} {stroke}/>')
        out.append(text(f"{x + w / 2:.1f}", y + h / 2 + size * 0.36, label, size=size,
                        fill=color, font=MONO, anchor="middle"))
        x += w + gap
    return "\n".join(out)


def points(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def surface(W, H, t, glow=(0.88, 0.2, 0.5), opacity=0.12, rx=14):
    """Card background: themed surface, border and a soft accent glow."""
    cx, cy, r = glow
    return f"""
<defs>
  <radialGradient id="glow" cx="{cx}" cy="{cy}" r="{r}">
    <stop offset="0" stop-color="{t['accent']}" stop-opacity="{opacity}"/>
    <stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="{rx}" fill="{t['surface']}" stroke="{t['border']}"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="{rx}" fill="url(#glow)"/>"""


def scaled(content, cx, cy, s):
    return f'<g transform="translate({cx * (1 - s):.1f} {cy * (1 - s):.1f}) scale({s})">{content}</g>'


# ---------------------------------------------------------------- isometric blocks

COS30 = math.cos(math.radians(30))


def iso(x, y, z, s, ox, oy):
    return ox + (x - y) * COS30 * s, oy + (x + y) * 0.5 * s - z * s


def iso_city(blocks, t, *, s, ox, oy, size, animate=True):
    """Wireframe blocks on an isometric drafting grid, drawn back to front."""
    P = lambda x, y, z: iso(x, y, z, s, ox, oy)
    out = []
    for i in range(size + 1):
        out.append(f'<line x1="{P(i, 0, 0)[0]:.1f}" y1="{P(i, 0, 0)[1]:.1f}" '
                   f'x2="{P(i, size, 0)[0]:.1f}" y2="{P(i, size, 0)[1]:.1f}" stroke="{t["grid"]}"/>')
        out.append(f'<line x1="{P(0, i, 0)[0]:.1f}" y1="{P(0, i, 0)[1]:.1f}" '
                   f'x2="{P(size, i, 0)[0]:.1f}" y2="{P(size, i, 0)[1]:.1f}" stroke="{t["grid"]}"/>')
    for n, (x, y, w, d, h) in enumerate(sorted(blocks, key=lambda b: b[0] + b[1] + (b[2] + b[3]) / 2)):
        top = [P(x, y, h), P(x + w, y, h), P(x + w, y + d, h), P(x, y + d, h)]
        left = [P(x, y + d, 0), P(x + w, y + d, 0), P(x + w, y + d, h), P(x, y + d, h)]
        right = [P(x + w, y, 0), P(x + w, y + d, 0), P(x + w, y + d, h), P(x + w, y, h)]
        delay = f' style="animation-delay:{0.25 + n * 0.09:.2f}s"' if animate else ""
        out.append(f'<g class="block"{delay} stroke="{t["accent"]}" stroke-width="1" stroke-linejoin="round">')
        out.append(f'<polygon points="{points(left)}" fill="{t["accent"]}" fill-opacity="0.10"/>')
        out.append(f'<polygon points="{points(right)}" fill="{t["accent"]}" fill-opacity="0.04"/>')
        out.append(f'<polygon points="{points(top)}" fill="{t["accent"]}" fill-opacity="0.22"/>')
        out.append("</g>")
    return "\n".join(out)


def roof(block, s, ox, oy):
    x, y, w, d, h = block
    return iso(x + w / 2, y + d / 2, h, s, ox, oy)


def data_links(pairs, t, *, s, ox, oy):
    """Arcs between rooftops with a dot travelling along each one."""
    out = []
    for n, (a, b) in enumerate(pairs):
        (x1, y1), (x2, y2) = roof(a, s, ox, oy), roof(b, s, ox, oy)
        cx, cy = (x1 + x2) / 2, min(y1, y2) - 34
        path = f"M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}"
        out.append(f'<path class="link" d="{path}" fill="none" stroke="{t["accent"]}" '
                   f'stroke-opacity="0.45" stroke-dasharray="3 4"/>')
        out.append(
            f'<circle class="pulse" r="2.6" fill="{t["accent"]}">'
            f'<animateMotion dur="{3.2 + n * 0.7:.1f}s" begin="{1.6 + n * 0.5:.1f}s" '
            f'repeatCount="indefinite" path="{path}"/></circle>'
        )
        for px, py in ((x1, y1), (x2, y2)):
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="{t["accent"]}" class="node"/>')
    return "\n".join(out)


MOTION_CSS = """
.block { animation: drop .7s cubic-bezier(.2,.8,.2,1) both; }
@keyframes drop { from { opacity: 0; transform: translateY(-16px); } to { opacity: 1; transform: none; } }
.link, .node { animation: fade .8s ease-out 1.4s both; }
.pulse { animation: fade .4s ease-out 1.6s both; }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
.rise { animation: rise .7s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { transform: translateY(10px); } to { transform: none; } }
.cursor { animation: blink 1.1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
@media (prefers-reduced-motion: reduce) {
  .block, .link, .node, .cursor, .rise { animation: none; }
  .pulse { display: none; }
}
"""


# ---------------------------------------------------------------- glyphs


def sparkle_path(x, y, r):
    return f"M{x},{y-r} Q{x},{y} {x+r},{y} Q{x},{y} {x},{y+r} Q{x},{y} {x-r},{y} Q{x},{y} {x},{y-r} z"


def glyph(kind, cx, cy, t):
    a = t["accent"]
    stroke = f'stroke="{a}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "pulse":
        line = f"M{cx-30},{cy} h12 l5,-14 7,28 6,-22 4,8 h26"
        return "\n".join([
            f'<rect x="{cx-34}" y="{cy-26}" width="68" height="52" rx="10" fill="{a}" fill-opacity="0.08" {stroke} stroke-opacity="0.5"/>',
            f'<path class="trace" d="{line}" fill="none" {stroke} pathLength="100" stroke-dasharray="100"/>',
        ])
    if kind == "photos":
        return "\n".join([
            f'<rect x="{cx-26}" y="{cy-24}" width="38" height="32" rx="5" fill="{a}" fill-opacity="0.06" {stroke} stroke-opacity="0.55" transform="rotate(-8 {cx-7} {cy-8})"/>',
            f'<rect x="{cx-12}" y="{cy-12}" width="38" height="32" rx="5" fill="{a}" fill-opacity="0.12" {stroke}/>',
            f'<path d="M{cx-8},{cy+16} l9,-10 6,6 5,-5 10,9" fill="none" {stroke}/>',
            f'<circle cx="{cx+16}" cy="{cy-4}" r="3" fill="{a}"/>',
        ])
    if kind == "keypad":
        keys = []
        for r in range(4):
            for c in range(4):
                lit = (r, c) == (1, 2)
                cls = ' class="key"' if lit else ""
                keys.append(
                    f'<rect x="{cx-27+c*14}" y="{cy-27+r*14}" width="11" height="11" rx="2.5" '
                    f'fill="{a}" fill-opacity="{0.9 if lit else 0.10}" stroke="{a}" stroke-opacity="{1 if lit else 0.55}"{cls}/>'
                )
        return "\n".join(keys)
    if kind == "beacon":
        waves = (
            f'<path class="wave" style="animation-delay:{i * 0.35:.2f}s" '
            f'd="M{cx+2+i*7},{cy-9-i*6} A{13+i*9},{13+i*9} 0 0 1 {cx+2+i*7},{cy+9+i*6}" fill="none" {stroke}/>'
            for i in range(3)
        )
        return "\n".join([
            f'<rect x="{cx-30}" y="{cy-22}" width="26" height="44" rx="7" fill="{a}" fill-opacity="0.12" {stroke}/>',
            f'<circle class="led" cx="{cx-17}" cy="{cy-9}" r="3" fill="{a}"/>',
            f'<line x1="{cx-22}" y1="{cy+10}" x2="{cx-12}" y2="{cy+10}" {stroke} stroke-opacity="0.6"/>',
            *waves,
        ])
    if kind == "slides":
        bars = ((-20, 12, 0.55), (-6, 22, 0.9), (8, 16, 0.7))
        return "\n".join([
            f'<rect x="{cx-32}" y="{cy-26}" width="64" height="42" rx="5" fill="{a}" fill-opacity="0.10" {stroke}/>',
            f'<path d="M{cx},{cy+16} v10 M{cx-12},{cy+26} h24" fill="none" {stroke}/>',
            *(f'<rect x="{cx+dx}" y="{cy+8-h}" width="10" height="{h}" rx="1.5" fill="{a}" fill-opacity="{o}"/>'
              for dx, h, o in bars),
        ])
    if kind == "phone":
        return "\n".join([
            f'<rect x="{cx-18}" y="{cy-29}" width="36" height="58" rx="8" fill="{a}" fill-opacity="0.10" {stroke}/>',
            f'<line x1="{cx-5}" y1="{cy-22}" x2="{cx+5}" y2="{cy-22}" {stroke}/>',
            *(f'<rect x="{cx-11}" y="{cy-14+i*11}" width="22" height="7" rx="2" fill="{a}" fill-opacity="{0.85 if i == 0 else 0.35}"/>'
              for i in range(3)),
            f'<circle cx="{cx}" cy="{cy+22}" r="2" fill="{a}"/>',
        ])
    if kind == "video":
        return "\n".join([
            f'<rect x="{cx-32}" y="{cy-24}" width="64" height="44" rx="6" fill="{a}" fill-opacity="0.10" {stroke}/>',
            f'<circle cx="{cx-8}" cy="{cy-6}" r="6" fill="none" {stroke}/>',
            f'<path d="M{cx-20},{cy+14} a12,10 0 0 1 24,0" fill="none" {stroke}/>',
            f'<circle class="led" cx="{cx+22}" cy="{cy-15}" r="3" fill="{a}"/>',
            f'<circle cx="{cx+18}" cy="{cy+10}" r="8" fill="{a}" fill-opacity="0.9"/>',
            f'<path d="M{cx+14},{cy+10} l3,3 6,-6" fill="none" stroke="{t["surface"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        ])
    if kind == "gauge":
        r, ticks = 24, []
        for k in range(9):
            ang = math.radians(-120 + k * 30)
            x1, y1 = cx + math.sin(ang) * (r - 6), cy - math.cos(ang) * (r - 6)
            x2, y2 = cx + math.sin(ang) * (r - 2), cy - math.cos(ang) * (r - 2)
            ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {stroke} stroke-opacity="0.6"/>')
        return "\n".join([
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{a}" fill-opacity="0.10" {stroke}/>',
            *ticks,
            f'<line class="needle" style="transform-origin:{cx}px {cy}px" x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-17}" stroke="{a}" stroke-width="2.2" stroke-linecap="round"/>',
            f'<circle cx="{cx}" cy="{cy}" r="3" fill="{a}"/>',
            f'<path d="M{cx-14},{cy+32} h28 m-5,-4 l5,4 -5,4" fill="none" {stroke} stroke-opacity="0.7"/>',
        ])
    if kind == "plc":
        return "\n".join([
            f'<line x1="{cx-38}" y1="{cy+28}" x2="{cx+38}" y2="{cy+28}" {stroke} stroke-opacity="0.45"/>',
            f'<rect x="{cx-30}" y="{cy-24}" width="60" height="46" rx="4" fill="{a}" fill-opacity="0.10" {stroke}/>',
            *(f'<rect x="{cx-26+i*9}" y="{y}" width="6" height="5" rx="1" fill="none" {stroke} stroke-opacity="0.6"/>'
              for i in range(6) for y in (cy - 20, cy + 13)),
            *(f'<circle class="led" style="animation-delay:{i * 0.3:.1f}s" cx="{cx-14+i*9}" cy="{cy}" r="2.4" fill="{a}"/>'
              for i in range(4)),
        ])
    if kind == "station":
        hub = (cx, cy - 20)
        arms = []
        for k in range(3):
            ang = math.radians(90 + k * 120)
            ex, ey = hub[0] + math.cos(ang) * 13, hub[1] + math.sin(ang) * 13
            arms.append(f'<line x1="{hub[0]}" y1="{hub[1]}" x2="{ex:.1f}" y2="{ey:.1f}" {stroke}/>')
            arms.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.4" fill="{a}" fill-opacity="0.35" {stroke}/>')
        waves = (
            f'<path class="wave" style="animation-delay:{i * 0.35:.2f}s" '
            f'd="M{cx+15+i*6},{cy+2-i*4} A{9+i*7},{9+i*7} 0 0 1 {cx+15+i*6},{cy+14+i*4}" fill="none" {stroke}/>'
            for i in range(2)
        )
        return "\n".join([
            f'<path d="M{cx},{cy+36} V{cy-20} M{cx-14},{cy+36} L{cx},{cy+20} L{cx+14},{cy+36}" fill="none" {stroke}/>',
            f'<g class="spin" style="transform-origin:{hub[0]}px {hub[1]}px">{"".join(arms)}</g>',
            f'<circle cx="{hub[0]}" cy="{hub[1]}" r="2.6" fill="{a}"/>',
            f'<rect x="{cx-10}" y="{cy+1}" width="20" height="14" rx="2" fill="{a}" fill-opacity="0.18" {stroke}/>',
            f'<circle class="led" cx="{cx-4}" cy="{cy+8}" r="2" fill="{a}"/>',
            *waves,
        ])
    raise ValueError(kind)


def claim_visual(cx, cy, t):
    """A stack of claim documents with AI-highlighted lines."""
    a = t["accent"]
    stroke = f'stroke="{a}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
    doc = f"M{cx-42},{cy-52} h56 l16,16 v84 h-72 z"
    out = [
        f'<rect x="{cx-34}" y="{cy-56}" width="76" height="100" rx="7" fill="{a}" fill-opacity="0.05" {stroke} stroke-opacity="0.3" transform="rotate(9 {cx} {cy})"/>',
        f'<rect x="{cx-38}" y="{cy-54}" width="76" height="100" rx="7" fill="{a}" fill-opacity="0.08" {stroke} stroke-opacity="0.55" transform="rotate(-5 {cx} {cy})"/>',
        f'<path d="{doc}" fill="{t["surface"]}"/>',
        f'<path d="{doc}" fill="{a}" fill-opacity="0.10" {stroke}/>',
        f'<path d="M{cx+14},{cy-52} v16 h16" fill="none" {stroke}/>',
    ]
    for i in range(5):
        y, end = cy - 22 + i * 13, cx + (18 if i % 2 == 0 else 6)
        if i in (1, 3):
            out.append(f'<rect class="hl" style="animation-delay:{i * 0.5:.1f}s" x="{cx-34}" y="{y-5}" width="{end-cx+38}" height="10" rx="3" fill="{a}" fill-opacity="0.2"/>')
        out.append(f'<line x1="{cx-30}" y1="{y}" x2="{end}" y2="{y}" {stroke} stroke-opacity="0.7"/>')
    out.append(f'<path class="sparkle" d="{sparkle_path(cx + 36, cy + 38, 11)}" fill="{a}"/>')
    out.append(f'<path class="sparkle" style="animation-delay:.9s" d="{sparkle_path(cx + 52, cy + 14, 6)}" fill="{a}"/>')
    return "\n".join(out)


GLYPH_CSS = """
.trace { animation: trace 2.6s ease-in-out infinite; }
@keyframes trace { 0% { stroke-dashoffset: 100; } 55%, 100% { stroke-dashoffset: 0; } }
.key { animation: press 2.4s ease-in-out infinite; }
@keyframes press { 0%, 100% { fill-opacity: .9; } 50% { fill-opacity: .2; } }
.wave { animation: wave 2.4s ease-out infinite; }
@keyframes wave { 0%, 100% { opacity: .15; } 30% { opacity: 1; } }
.led { animation: led 1.6s ease-in-out infinite; }
@keyframes led { 50% { opacity: .25; } }
.sparkle { transform-box: fill-box; transform-origin: center; animation: twinkle 2.8s ease-in-out infinite; }
@keyframes twinkle { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(.6); opacity: .5; } }
.hl { animation: hl 3.2s ease-in-out infinite; }
@keyframes hl { 0%, 100% { fill-opacity: .12; } 50% { fill-opacity: .35; } }
.needle { animation: needle 3.2s ease-in-out infinite; }
@keyframes needle { 0%, 100% { transform: rotate(-55deg); } 50% { transform: rotate(40deg); } }
.spin { animation: spin 2.4s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.ping { transform-box: fill-box; transform-origin: center; animation: ping 2.2s ease-out infinite; }
@keyframes ping { 0% { transform: scale(1); opacity: .8; } 100% { transform: scale(2.6); opacity: 0; } }
@media (prefers-reduced-motion: reduce) {
  .trace, .key, .wave, .led, .sparkle, .hl, .needle, .spin { animation: none; }
  .ping { display: none; }
  .trace { stroke-dasharray: none; }
}
"""


def icon(kind, cx, cy, t):
    """Small line icons for pills and tiles, about 16px across."""
    a = t["accent"]
    stroke = f'fill="none" stroke="{a}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "globe":
        return (f'<circle cx="{cx}" cy="{cy}" r="7.5" {stroke}/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="3.2" ry="7.5" {stroke}/>'
                f'<line x1="{cx-7.5}" y1="{cy}" x2="{cx+7.5}" y2="{cy}" {stroke}/>')
    if kind == "linkedin":
        return (f'<rect x="{cx-8}" y="{cy-8}" width="16" height="16" rx="3" fill="{a}"/>'
                f'<text x="{cx}" y="{cy+4.5}" font-family="{SANS}" font-size="11" font-weight="700" '
                f'fill="{t["surface"]}" text-anchor="middle">in</text>')
    if kind == "mail":
        return (f'<rect x="{cx-8}" y="{cy-6}" width="16" height="12" rx="2" {stroke}/>'
                f'<path d="M{cx-7},{cy-4.5} l7,5 7,-5" {stroke}/>')
    if kind == "appstore":
        return f'<path d="M{cx-6},{cy+7} L{cx},{cy-7} L{cx+6},{cy+7} M{cx-3.5},{cy+2} h7" {stroke}/>'
    if kind == "play":
        return f'<path d="M{cx-4},{cy-7.5} L{cx+7},{cy} L{cx-4},{cy+7.5} z" {stroke}/>'
    if kind == "chip":
        pins = "".join(f"M{cx+d},{cy-9} v3 M{cx+d},{cy+6} v3 M{cx-9},{cy+d} h3 M{cx+6},{cy+d} h3 " for d in (-3, 3))
        return f'<rect x="{cx-6}" y="{cy-6}" width="12" height="12" rx="2" {stroke}/><path d="{pins}" {stroke}/>'
    if kind == "clock":
        return f'<circle cx="{cx}" cy="{cy}" r="7.5" {stroke}/><path d="M{cx},{cy-4.5} V{cy} L{cx+3.5},{cy+2}" {stroke}/>'
    if kind == "database":
        return (f'<ellipse cx="{cx}" cy="{cy-5}" rx="7" ry="2.5" {stroke}/>'
                f'<path d="M{cx-7},{cy-5} v10 a7,2.5 0 0 0 14,0 v-10 M{cx-7},{cy} a7,2.5 0 0 0 14,0" {stroke}/>')
    if kind == "tower":
        return (f'<path d="M{cx-5},{cy+8} L{cx},{cy-3} L{cx+5},{cy+8} M{cx},{cy-3} V{cy+8}" {stroke}/>'
                f'<path d="M{cx-4.5},{cy-8.5} a6,6 0 0 0 0,8 M{cx+4.5},{cy-8.5} a6,6 0 0 1 0,8" {stroke}/>')
    if kind == "signal":
        return "".join(f'<rect x="{cx-7+i*4}" y="{cy+6-3*(i+1)}" width="2.6" height="{3*(i+1)}" rx="0.8" fill="{a}"/>'
                       for i in range(4))
    if kind == "school":
        return (f'<path d="M{cx-8.5},{cy-2} L{cx},{cy-8} L{cx+8.5},{cy-2} z" {stroke}/>'
                f'<path d="M{cx-6.5},{cy-2} v9 h13 v-9 M{cx-1.8},{cy+7} v-4.5 h3.6 v4.5 M{cx-4},{cy+1} v1 M{cx+4},{cy+1} v1" {stroke}/>')
    if kind == "calendar":
        return (f'<rect x="{cx-7.5}" y="{cy-5.5}" width="15" height="13" rx="2" {stroke}/>'
                f'<path d="M{cx-7.5},{cy-1.5} h15 M{cx-3.5},{cy-8} v4 M{cx+3.5},{cy-8} v4" {stroke}/>'
                + "".join(f'<rect x="{cx-4.5+c*3.6:.1f}" y="{cy+1+r*3}" width="1.8" height="1.8" rx="0.4" fill="{a}"/>'
                          for r in range(2) for c in range(3)))
    raise ValueError(kind)


# ---------------------------------------------------------------- artwork

HEADER_CITY = [  # x, y, w, d, h in grid units
    (0.4, 0.5, 1.6, 1.5, 3.0),
    (2.6, 0.4, 1.3, 1.3, 2.0),
    (4.4, 0.6, 1.2, 1.2, 1.2),
    (0.6, 2.7, 1.3, 1.4, 1.6),
    (2.5, 2.4, 1.7, 1.7, 4.0),
    (4.7, 2.6, 0.9, 1.1, 0.9),
    (0.9, 4.7, 1.0, 0.9, 1.0),
    (2.7, 4.6, 1.3, 1.0, 1.5),
    (4.5, 4.4, 1.2, 1.3, 2.4),
]

FEATURED_CITY = [
    (0.3, 0.3, 1.4, 1.4, 1.4),
    (2.0, 0.3, 1.6, 1.6, 3.4),
    (0.3, 2.1, 1.4, 1.5, 2.2),
    (2.1, 2.2, 1.5, 1.4, 1.0),
]


def header(t):
    W, H = 900, 280
    s, ox, oy = 23, 712, 94
    c = HEADER_CITY
    links = [(c[0], c[4]), (c[4], c[8]), (c[3], c[4]), (c[1], c[2])]
    prompt_w = len(HEADER["prompt"]) * 14 * MONO_ADVANCE
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{t['bg']}"/><stop offset="1" stop-color="{t['bg2']}"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.79" cy="0.45" r="0.42">
    <stop offset="0" stop-color="{t['accent']}" stop-opacity="0.16"/>
    <stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="url(#bg)" stroke="{t['border']}"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="url(#glow)"/>
{text(48, 74, HEADER['prompt'], size=14, fill=t['accent_text'], font=MONO)}
<rect class="cursor" x="{48 + prompt_w + 6:.1f}" y="62" width="8" height="15" fill="{t['accent']}"/>
{text(46, 136, HEADER['name'], size=50, fill=t['heading'], weight=700, spacing=-1)}
{text(48, 174, HEADER['role'], size=20, fill=t['heading'], weight=500)}
{text(48, 202, HEADER['tagline'], size=15, fill=t['muted'])}
{chips(48, 226, HEADER['chips'], t)}
{iso_city(c, t, s=s, ox=ox, oy=oy, size=6)}
{data_links(links, t, s=s, ox=ox, oy=oy)}
"""
    return svg(W, H, body, f"{HEADER['name']}: {HEADER['role']}", MOTION_CSS)


def stats(t):
    W, H = 900, 108
    cw = W / len(STATS)
    parts = [surface(W, H, t, glow=(0.5, 0.0, 0.7), opacity=0.10)]
    for i, (value, label) in enumerate(STATS):
        cx = cw * i + cw / 2
        delay = f"animation-delay:{0.15 + i * 0.12:.2f}s"
        if i:
            parts.append(f'<line x1="{cw * i:.1f}" y1="26" x2="{cw * i:.1f}" y2="{H - 26}" stroke="{t["border"]}"/>')
        parts.append(text(f"{cx:.1f}", 56, value, size=30, fill=t["accent_text"], weight=700, anchor="middle",
                          spacing=-0.5, cls="rise", style=delay))
        parts.append(text(f"{cx:.1f}", 80, label.upper(), size=10.5, fill=t["muted"], font=MONO, anchor="middle",
                          spacing=1, cls="rise", style=delay))
    summary = "; ".join(f"{v} {l}" for v, l in STATS)
    return svg(W, H, "\n".join(parts), summary, MOTION_CSS)


def wide(c, t):
    W, H, vx = 900, 240, 772
    if c["visual"] == "city":
        s, oy, city = 26, 92, FEATURED_CITY
        visual = (iso_city(city, t, s=s, ox=vx, oy=oy, size=4) + "\n"
                  + data_links([(city[0], city[1]), (city[2], city[1])], t, s=s, ox=vx, oy=oy))
    else:
        visual = claim_visual(vx, 108, t)
    body = f"""{surface(W, H, t, glow=(0.86, 0.4, 0.36), opacity=0.14)}
{text(32, 44, c['label'].upper(), size=11, fill=t['accent_text'], font=MONO, spacing=1.2)}
{text(31, 84, c['title'], size=32, fill=t['heading'], weight=700, spacing=-0.5)}
{chr(10).join(text(32, 118 + i * 22, line, size=15, fill=t['body']) for i, line in enumerate(c['lines']))}
{chips(32, 190, c['chips'], t)}
{visual}
{text(vx, 210, c['stat'], size=11, fill=t['muted'], font=MONO, anchor="middle")}
"""
    return svg(W, H, body, f"{c['title']}: {' '.join(c['lines'])}", MOTION_CSS + GLYPH_CSS)


def tiles_card(c, t):
    """Wide card with a row of icon tiles; the top-right corner holds a stat or a glyph."""
    W, H = 900, 272
    tiles = []
    x, y, tw, th = 32, 134, 199, 60
    for kind, name, sub in c["tiles"]:
        tiles += [
            f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="12" fill="{t["chip_bg"]}" stroke="{t["border"]}"/>',
            f'<circle cx="{x + 30}" cy="{y + 30}" r="17" fill="{t["accent"]}" fill-opacity="0.14"/>',
            icon(kind, x + 30, y + 30, t),
            text(x + 56, y + 27, name, size=15, fill=t["heading"], weight=600),
            text(x + 56, y + 45, sub, size=10.5, fill=t["muted"], font=MONO),
        ]
        x += tw + 12
    if "glyph" in c:
        corner = scaled(glyph(c["glyph"], W - 80, 64, t), W - 80, 64, 1.35)
    else:
        corner = text(W - 32, 44, c["stat"], size=11, fill=t["muted"], font=MONO, anchor="end")
    platforms = c.get("platforms", [])
    body = f"""{surface(W, H, t, glow=(0.9, 0.1, 0.45))}
{text(32, 44, c['label'].upper(), size=11, fill=t['accent_text'], font=MONO, spacing=1.2)}
{corner}
{text(31, 84, c['title'], size=32, fill=t['heading'], weight=700, spacing=-0.5)}
{text(32, 112, c['tagline'], size=15, fill=t['body'])}
{chr(10).join(tiles)}
{chips(32, 224, platforms + c['chips'], t, accent=len(platforms))}
"""
    summary = ", ".join(f"{name}: {sub}" for _, name, sub in c["tiles"])
    return svg(W, H, body, f"{c['title']}: {c['tagline']} {summary}", GLYPH_CSS)


def card(c, t):
    W, H = 440, 214
    body = f"""{surface(W, H, t)}
{text(26, 40, c['label'].upper(), size=11, fill=t['accent_text'], font=MONO, spacing=1.2)}
{text(25, 74, c['title'], size=23, fill=t['heading'], weight=700, spacing=-0.3)}
{chr(10).join(text(26, 104 + i * 20, line, size=14, fill=t['body']) for i, line in enumerate(c['lines']))}
{chips(26, 168, c['platforms'] + c['chips'], t, accent=len(c['platforms']))}
{glyph(c['glyph'], 384, 56, t)}
"""
    return svg(W, H, body, f"{c['title']}: {' '.join(c['lines'])}", GLYPH_CSS)


def small(c, t):
    """Narrow card, three to a row: four lines of text, then platforms (highlighted) and chips."""
    W, H = 272, 236
    platforms = c.get("platforms", [])
    body = f"""{surface(W, H, t, glow=(0.85, 0.15, 0.55))}
{text(20, 34, c['label'].upper(), size=10, fill=t['accent_text'], font=MONO, spacing=1)}
{scaled(glyph(c['glyph'], W - 48, 48, t), W - 48, 48, 0.8)}
{text(19, 92, c['title'], size=18, fill=t['heading'], weight=700, spacing=-0.3)}
{chr(10).join(text(20, 118 + i * 18, line, size=12.5, fill=t['body']) for i, line in enumerate(c['lines']))}
{chips(20, H - 40, platforms + c['chips'], t, size=10, accent=len(platforms))}
"""
    return svg(W, H, body, f"{c['title']}: {' '.join(c['lines'])}", GLYPH_CSS)


def journey(t):
    """Vertical career timeline: dates, a rail with markers, and organisation · role over a note."""
    W, top, rh, rail = 900, 70, 56, 176
    H = top + rh * len(JOURNEY) + 6
    sep = " · "
    parts = [
        surface(W, H, t, glow=(0.12, 0.0, 0.6), opacity=0.10),
        text(32, 42, "JOURNEY · 2007 → NOW", size=11, fill=t["accent_text"], font=MONO, spacing=1.2),
        text(W - 32, 42, "19 years", size=11, fill=t["muted"], font=MONO, anchor="end"),
        f'<line x1="{rail}" y1="{top + 15}" x2="{rail}" y2="{top + rh * (len(JOURNEY) - 1) + 15}" stroke="{t["border"]}" stroke-width="2"/>',
    ]
    for i, (when, org, role, note, marker) in enumerate(JOURNEY):
        cy = top + i * rh + 15
        parts.append(text(32, cy + 4, when, size=12, fill=t["muted"], font=MONO))
        if marker is True:
            parts.append(f'<circle class="ping" cx="{rail}" cy="{cy}" r="6" fill="none" stroke="{t["accent"]}"/>')
            parts.append(f'<circle cx="{rail}" cy="{cy}" r="6" fill="{t["accent"]}"/>')
        elif marker is False:
            parts.append(f'<circle cx="{rail}" cy="{cy}" r="5" fill="{t["surface"]}" stroke="{t["accent"]}" stroke-width="2"/>')
        else:
            parts.append(f'<rect x="{rail - 5}" y="{cy - 5}" width="10" height="10" fill="{t["surface"]}" stroke="{t["accent"]}" '
                         f'stroke-width="2" transform="rotate(45 {rail} {cy})"/>')
        parts.append(
            f'<text x="200" y="{cy + 5}" font-family="{SANS}" font-size="16">'
            f'<tspan font-weight="700" fill="{t["heading"]}">{escape(org)}</tspan>'
            f'<tspan fill="{t["accent_text"]}">{sep}{escape(role)}</tspan></text>'
        )
        if note:
            parts.append(text(200, cy + 26, note, size=13, fill=t["body"]))
    summary = "; ".join(f"{when}: {org}, {role}" for when, org, role, _, _ in JOURNEY)
    return svg(W, H, "\n".join(parts), summary, GLYPH_CSS)


def link_pill(link, t):
    size, H = 13, 36
    W = round(len(link["label"]) * size * MONO_ADVANCE + 58)
    body = f"""
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="{H/2 - 0.5}" fill="{t['surface']}" stroke="{t['border']}"/>
{icon(link['icon'], 24, H / 2, t)}
{text(42, H / 2 + size * 0.36, link['label'], size=size, fill=t['heading'], font=MONO)}
"""
    return svg(W, H, body, link["label"])


def store_pill(s, t):
    H = 44
    store_w = len(s["store"]) * 9.5 * MONO_ADVANCE + len(s["store"]) * 0.8
    app_w = len(s["app"]) * 14 * SANS_ADVANCE
    W = round(max(store_w, app_w) + 64)
    body = f"""
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="{H/2 - 0.5}" fill="{t['surface']}" stroke="{t['border']}"/>
<circle cx="24" cy="{H / 2}" r="14" fill="{t['accent']}" fill-opacity="0.14"/>
{icon(s['icon'], 24, H / 2, t)}
{text(48, 18, s['store'].upper(), size=9.5, fill=t['muted'], font=MONO, spacing=0.8)}
{text(48, 34, s['app'], size=14, fill=t['heading'], weight=600)}
"""
    return svg(W, H, body, f"{s['app']} on {s['store']}")


def main():
    ASSETS.mkdir(exist_ok=True)
    written = set()
    for name, t in THEMES.items():
        files = {
            "header": header(t),
            "stats": stats(t),
            **{f"card-{c['slug']}": wide(c, t) for c in WIDE},
            f"card-{COMPANY['slug']}": tiles_card(COMPANY, t),
            f"card-{ATTENDUM['slug']}": tiles_card(ATTENDUM, t),
            **{f"card-{c['slug']}": small(c, t) for c in PRODUCTS},
            f"card-{LOGGER['slug']}": tiles_card(LOGGER, t),
            **{f"card-{c['slug']}": card(c, t) for c in HARDWARE},
            **{f"hobby-{c['slug']}": small(c, t) for c in HOBBIES},
            "journey": journey(t),
            **{f"link-{l['slug']}": link_pill(l, t) for l in LINKS},
            **{f"store-{s['slug']}": store_pill(s, t) for s in STORES},
        }
        for stem, content in files.items():
            path = ASSETS / f"{stem}-{name}.svg"
            path.write_text(content)
            written.add(path)
    stale = [p for p in ASSETS.glob("*.svg") if p not in written]
    for p in stale:
        p.unlink()
    print(f"wrote {len(written)} files to {ASSETS.relative_to(ROOT)}/" + (f", removed {len(stale)} stale" if stale else ""))


if __name__ == "__main__":
    main()
