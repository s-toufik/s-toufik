"""Render every profile card.

Usage: render.py <login> <config.json> <output-dir>

Each step is timed and logged. A step that fails keeps the card committed by the
previous run instead of failing the whole job.
"""

import io
import json
import math
import os
import re
import sys
import tarfile
import time
import traceback
from contextlib import contextmanager
from datetime import UTC, datetime
from html import escape
from pathlib import Path

import achievements
import cards
from github_api import get_file, get_tarball, owned_repositories

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
INK, BOX, RAISE, LINE, SOFT = "#0a0f1a", "#0d1117", "#111827", "#243044", "#1a2333"
FG, MUTED, FAINT = "#e6edf3", "#8b98ab", "#5b6779"
BLUE, DEEP, SKY, OK, WARN = "#60a5fa", "#1d4ed8", "#38bdf8", "#3fb950", "#d29922"

SPANS: list[dict] = []
T0 = time.perf_counter()


@contextmanager
def span(name: str, count: int | None = None):
    start = time.perf_counter()
    record = {"name": name, "start": start - T0, "count": count, "ok": True}
    try:
        yield record
    except Exception:
        record["ok"] = False
        traceback.print_exc()
    finally:
        record["duration"] = time.perf_counter() - start
        SPANS.append(record)


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def ago(value: str) -> int:
    return (datetime.now(UTC) - datetime.fromisoformat(value.replace("Z", "+00:00"))).days


# --- hero: a terminal session -----------------------------------------------------------------


def about_line(line: str) -> str:
    """One line of about.md, coloured like a terminal markdown viewer."""
    if line.startswith("# "):
        return f'<tspan fill="{SKY}" font-weight="600">{escape(line)}</tspan>'
    if line.startswith("- "):
        return f'<tspan fill="{BLUE}">  ▸ </tspan><tspan fill="{FG}">{escape(line[2:])}</tspan>'
    return f'<tspan fill="{MUTED}">{escape(line)}</tspan>'


def hero(config: dict, repositories: list[dict]) -> str:
    by_name = {repo["name"].lower(): repo for repo in repositories}
    rows = [(item, by_name[item["repo"].lower()]) for item in config["featured"] if item["repo"].lower() in by_name]
    width = 840
    prompt = f'<tspan fill="{BLUE}">toufik@homelab</tspan><tspan fill="{FAINT}">:~$ </tspan>'
    out: list[str] = []
    y, delay = 68, .1

    def emit(content: str, gap: int = 22, pause: float = .1, attrs: str = "") -> None:
        nonlocal y, delay
        out.append(f'<text x="24" y="{y}" class="typed" style="animation-delay:{delay:.2f}s"{attrs}>{content}</text>')
        y += gap
        delay += pause

    emit(f'{prompt}<tspan fill="{FG}">whoami</tspan>', pause=.3)
    emit(f'<tspan fill="{FG}">{escape(config["name"])}</tspan>', gap=20)
    emit(f'<tspan fill="{MUTED}">{escape(config["tagline"])}</tspan>', gap=32, pause=.4)

    emit(f'{prompt}<tspan fill="{FG}">cat about.md</tspan>', pause=.3)
    for line in config.get("about", []):
        emit(about_line(line) if line else "", gap=20 if line else 10, pause=.08)
    y += 12

    emit(f'{prompt}<tspan fill="{FG}">homelab status --apps</tspan>', gap=24, pause=.3)
    emit('<tspan x="44">SERVICE</tspan><tspan x="234">LANG</tspan><tspan x="354">STATE</tspan><tspan x="484">LAST PUSH</tspan><tspan x="584">ROLE</tspan>',
         gap=20, pause=.15, attrs=f' fill="{FAINT}" font-size="12" letter-spacing=".08em"')
    for index, (item, repo) in enumerate(rows):
        days = ago(repo["pushed_at"])
        # a state set in profile.json wins; otherwise it comes from the last push
        state = item.get("state") or ("ready" if days <= 14 else "idle" if days <= 90 else "dormant")
        color = {"ready": OK, "idle": WARN}.get(state, FAINT)
        if state == "ready":
            led = f'<circle class="led" style="animation-delay:{index * .3:.1f}s" cx="30" cy="{y - 5}" r="4" fill="{color}"/>'
        elif state == "decommissioned":
            led = f'<path d="M26.5 {y - 8.5}l7 7m0-7l-7 7" stroke="{FAINT}" stroke-width="1.6" stroke-linecap="round"/>'
        else:
            led = f'<circle cx="30" cy="{y - 5}" r="4" fill="none" stroke="{color}" stroke-width="1.6"/>'
        name_style = f' fill="{FAINT}" text-decoration="line-through"' if state == "decommissioned" else f' fill="{FG}"'
        when = "today" if days == 0 else f"{days}d ago"
        out.append(
            f'<g class="typed" style="animation-delay:{delay:.2f}s">{led}<text x="44" y="{y}">'
            f'<tspan{name_style}>{escape(repo["name"])}</tspan>'
            f'<tspan x="234" fill="{MUTED}">{escape(item.get("lang") or repo["language"] or "—")}</tspan>'
            f'<tspan x="354" fill="{color}">{state}</tspan><tspan x="484" fill="{MUTED}">{when}</tspan>'
            f'<tspan x="584" fill="{FAINT}">{escape(item["role"])}</tspan></text></g>'
        )
        y += 22
        delay += .1
    y += 10
    emit(f'{prompt}<tspan class="cursor" fill="{BLUE}">█</tspan>', gap=0)
    height = y + 24

    about = " ".join(line.lstrip("#- ") for line in config.get("about", []) if line)
    label = f"Terminal: {config['name']}. {config['tagline']} {about} Project status: {', '.join(item['repo'] for item, _ in rows)}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
  <style>
    .typed {{ animation: reveal .01s steps(1) backwards; }}
    @keyframes reveal {{ from {{ opacity: 0; }} }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ fill-opacity: 0; }} }}
    .led {{ animation: pulse 2.4s ease-in-out infinite; }}
    @keyframes pulse {{ 50% {{ opacity: .35; }} }}
    @media (prefers-reduced-motion: reduce) {{ .typed, .cursor, .led {{ animation: none; }} }}
  </style>
  <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="{INK}" stroke="{LINE}"/>
  <path d="M.5 36.5V12.5A12 12 0 0 1 12.5 .5h815a12 12 0 0 1 12 12v24z" fill="{RAISE}"/>
  <circle cx="22" cy="18" r="6" fill="#f87171" fill-opacity=".8"/><circle cx="42" cy="18" r="6" fill="#fbbf24" fill-opacity=".8"/><circle cx="62" cy="18" r="6" fill="#34d399" fill-opacity=".8"/>
  <text x="{width // 2}" y="23" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{FAINT}">toufik@homelab: ~ — ssh over tailscale</text>
  <g font-family="{MONO}" font-size="14">
    {"".join(out)}
  </g>
</svg>
"""


# --- nexus: the knowledge hub as a graph ----------------------------------------------------

NEXUS_COLORS = {"Projects": BLUE, "Knowledge": "#a78bfa", "Paths": "#34d399", "Sources": "#fbbf24",
                "Log": "#f472b6", "System": MUTED}
GRAPH_HEIGHT = 560
WIKILINK = re.compile(r"\[\[([^\]|#]+)")


def vault(archive: bytes) -> dict[str, str]:
    """Markdown notes of an Obsidian vault tarball, keyed by path inside the vault."""
    notes = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            path = member.name.split("/", 1)[-1]  # drop the "<owner>-<repo>-<sha>/" prefix
            if not member.isfile() or not path.endswith(".md") or any(part.startswith(".") for part in path.split("/")):
                continue
            notes[path] = tar.extractfile(member).read().decode("utf-8", "replace")
    return notes


def nexus(config: dict, notes: dict[str, str], repo: dict | None) -> str:
    settings = config["nexus"]
    groups = settings["groups"]
    hidden = tuple(settings.get("hide_from_graph", []))
    by_title = {path.rsplit("/", 1)[-1][:-3].lower(): path for path in notes}

    # the graph: every note but the repository README and the templates, linked by [[wikilinks]]
    nodes = [path for path in notes if path != "README.md" and not path.startswith(hidden)]
    edges = set()
    for path in nodes:
        for target in WIKILINK.findall(notes[path]):
            other = by_title.get(target.strip().rsplit("/", 1)[-1].lower())
            if other in nodes and other != path:
                edges.add(tuple(sorted((path, other))))
    degree = {path: 0 for path in nodes}
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1

    # the tree: every folder and its subfolders with their note counts
    def count(prefix: str) -> int:
        return sum(1 for path in notes if path.startswith(prefix))
    tree = [f'<tspan fill="{FG}">nexus</tspan>']
    top = [g for g in groups if count(g + "/")]
    for i, group in enumerate(top):
        last = i == len(top) - 1
        tree.append(f'<tspan fill="{FAINT}">{"└──" if last else "├──"} </tspan><tspan fill="{NEXUS_COLORS.get(group, MUTED)}">{escape(group)}</tspan>'
                    f'<tspan x="270" text-anchor="end" fill="{MUTED}">{count(group + "/")}</tspan>')
        subs = sorted({p.split("/")[1] for p in notes if p.startswith(group + "/") and p.count("/") >= 2})
        for j, sub in enumerate(subs):
            branch = "    " if last else "│   "
            tree.append(f'<tspan fill="{FAINT}">{branch}{"└──" if j == len(subs) - 1 else "├──"} </tspan><tspan fill="{MUTED}">{escape(sub if len(sub) <= 20 else sub[:19] + "…")}</tspan>'
                        f'<tspan x="270" text-anchor="end" fill="{FAINT}">{count(f"{group}/{sub}/")}</tspan>')
    height = max(GRAPH_HEIGHT, 100 + len(tree) * 19 + 56)

    # A tall layout: the two biggest folders above and below Home, the small ones left and right.
    # Every cluster is a sunflower whose spacing shrinks as the vault grows, so it always fits the card.
    top_y, bottom_y, gx = 58, height - 50, 568
    gy = (top_y + bottom_y) / 2
    sizes = {g: sum(1 for p in nodes if p.startswith(g + "/")) for g in groups}
    present = sorted((g for g in groups if sizes[g]), key=lambda g: -sizes[g])
    half = (bottom_y - top_y) / 2 - 30 - 20          # room for one big cluster: minus Home's gap and a label
    radius = half / 2                            # the cluster's radius, its centre half-way out
    step = min(10.5, radius / math.sqrt(max(1, max(sizes.values()) - 1)))
    scale = max(.45, step / 10.5)                # dots shrink with the spacing
    centres = {}
    for group, slot in zip(present, ["top", "bottom", "left", "right", "top-left", "bottom-right", "bottom-left", "top-right"]):
        spread = step * math.sqrt(max(0, sizes[group] - 1))
        side_x = {"left": -1, "right": 1, "top-left": -1, "bottom-left": -1, "top-right": 1, "bottom-right": 1}.get(slot, 0)
        side_y = {"top": -1, "bottom": 1, "top-left": -.55, "top-right": -.55, "bottom-left": .55, "bottom-right": .55}.get(slot, 0)
        cx = gx + side_x * 168
        cy = gy + side_y * (30 + radius) if slot in ("top", "bottom") else gy + side_y * (half + 30) * .75
        centres[group] = (cx, cy, spread, slot)
    position, group_label = {}, []
    for group, (cx, cy, spread, slot) in centres.items():
        members = sorted((p for p in nodes if p.startswith(group + "/")),
                         key=lambda p: (p != f"{group}/{group}.md", -degree[p], p))
        for i, path in enumerate(members):  # sunflower around the folder's own index note
            r, a = step * math.sqrt(i), i * 2.39996
            position[path] = (cx + r * math.cos(a), cy + r * math.sin(a))
        label_y = cy + spread + 18 if slot.startswith("bottom") else cy - spread - 9
        group_label.append(f'<text x="{cx:.0f}" y="{label_y:.0f}" text-anchor="middle" font-size="11.5" stroke="{INK}" stroke-width="4" paint-order="stroke" '
                           f'fill="{NEXUS_COLORS.get(group, MUTED)}">{escape(group)}</text>')
    for path in nodes:
        position.setdefault(path, (gx, gy))  # Home.md and other top-level notes sit in the middle

    def color(path: str) -> str:
        return NEXUS_COLORS.get(path.split("/", 1)[0], FG) if "/" in path else FG

    def curve(a: str, b: str) -> str:
        (x1, y1), (x2, y2) = position[a], position[b]
        mx, my, dx, dy = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        bend = (sum(map(ord, a + b)) % 41 - 20) / 20 * min(46, length * .22)  # stable per edge, fans a bundle out
        cx, cy = mx - dy / length * bend, my + dx / length * bend
        return (f'<path d="M{x1:.1f} {y1:.1f} Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}" fill="none" '
                f'stroke="{color(a) if "/" in a else color(b)}" stroke-opacity="{edge_opacity:.2f}" stroke-width="1"/>')

    edge_opacity = max(.05, .2 * min(1.0, 150 / max(1, len(edges))))  # a dense vault stays readable
    lines = "".join(curve(a, b) for a, b in sorted(edges))
    dots = []
    for index, path in enumerate(sorted(nodes, key=lambda p: degree[p])):
        x, y = position[path]
        r = (2.6 + min(5.0, degree[path] * .45)) * scale
        hub = degree[path] >= 6
        cls = "node hub" if hub else "node"
        dots.append(f'<circle class="{cls}" style="animation-delay:{.3 + index * .025:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color(path)}"/>')
    home = next((p for p in nodes if "/" not in p), None)
    home_label = (f'<text x="{gx}" y="{gy + 22:.0f}" text-anchor="middle" font-size="11.5" fill="{FG}" stroke="{INK}" stroke-width="4" paint-order="stroke">{escape(home[:-3])}</text>' if home else "")

    tree_svg = "".join(
        f'<text x="24" y="{100 + i * 19}" xml:space="preserve" class="row" style="animation-delay:{.15 + i * .05:.2f}s">{line}</text>'
        for i, line in enumerate(tree)
    )
    total_notes = len(notes) - (1 if "README.md" in notes else 0)
    updated = f" · updated {ago(repo['pushed_at'])}d ago" if repo and ago(repo["pushed_at"]) else " · updated today" if repo else ""
    width = 840
    footer_y = height - 22
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Nexus, my knowledge hub: {total_notes} notes and {len(edges)} links across {', '.join(top)}, drawn as a graph of linked notes">
  <style>
    .row {{ animation: reveal .01s steps(1) backwards; }}
    @keyframes reveal {{ from {{ opacity: 0; }} }}
    .node {{ transform-box: fill-box; transform-origin: center; animation: pop .5s cubic-bezier(.2,.9,.3,1.4) backwards; }}
    @keyframes pop {{ from {{ transform: scale(0); }} }}
    .hub {{ animation: pop .5s cubic-bezier(.2,.9,.3,1.4) backwards, glow 3s ease-in-out 1.5s infinite; }}
    @keyframes glow {{ 50% {{ opacity: .55; }} }}
    .edges {{ animation: fade 1.2s ease-out .6s backwards; }}
    @keyframes fade {{ from {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .row, .node, .hub, .edges {{ animation: none; }} }}
  </style>
  <g font-family="{MONO}">
    <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="{INK}" stroke="{LINE}"/>
    <path d="M.5 36.5V12.5A12 12 0 0 1 12.5 .5h815a12 12 0 0 1 12 12v24z" fill="{RAISE}"/>
    <circle cx="22" cy="18" r="6" fill="#f87171" fill-opacity=".8"/><circle cx="42" cy="18" r="6" fill="#fbbf24" fill-opacity=".8"/><circle cx="62" cy="18" r="6" fill="#34d399" fill-opacity=".8"/>
    <text x="{width // 2}" y="23" text-anchor="middle" font-size="12" fill="{FAINT}">nexus — knowledge hub · obsidian vault</text>
    <text x="24" y="70" font-size="14"><tspan fill="{BLUE}">toufik@homelab</tspan><tspan fill="{FAINT}">:~$ </tspan><tspan fill="{FG}">tree nexus -d</tspan></text>
    <g font-size="13">{tree_svg}</g>
    <line x1="300" y1="52" x2="300" y2="{height - 44}" stroke="{SOFT}"/>
    <g class="edges">{lines}</g>
    {"".join(dots)}
    {home_label}
    {"".join(group_label)}
    <text x="24" y="{footer_y}" font-size="11.5" fill="{FAINT}">{total_notes} notes · {len(edges)} links{updated}</text>
    <text x="{width - 20}" y="{footer_y}" text-anchor="end" font-size="11.5" fill="{FAINT}">one dot per note · sized by its links</text>
  </g>
</svg>
"""


# --- cluster: every helm release by namespace ------------------------------------------------


def releases(helmfile: str) -> list[tuple[str, str]]:
    found, inside = [], False
    for line in helmfile.splitlines():
        if line.startswith("releases:"):
            inside = True
            continue
        if inside and re.match(r"^\S", line):
            inside = False
        if not inside:
            continue
        if match := re.match(r"^  - name:\s*([\w.-]+)", line):
            found.append([match.group(1), "other"])
        elif found and (match := re.search(r"labels:\s*\{[^}]*group:\s*([\w-]+)", line)):
            found[-1][1] = match.group(1)
    return [(name, group) for name, group in found]


def cluster(config: dict, found: list[tuple[str, str]]) -> str:
    settings = config["cluster"]
    order = settings["groups"] + sorted({group for _, group in found} - set(settings["groups"]))
    groups = [(group, [name for name, g in found if g == group]) for group in order]
    groups = [(group, names) for group, names in groups if names]
    hops, tel, kinds, rename = settings["hops"], settings["telemetry"], settings["kinds"], settings["rename"]

    width, col_w, chip_w, chip_h = 840, 322, 147, 22
    columns = {166: 72, 496: 72}
    out = []
    for group, names in groups:
        x = min(columns, key=lambda c: columns[c])  # masonry: the shorter column takes the next group
        gy = columns[x]
        h = 34 + (len(names) + 1) // 2 * 28 + 4
        out.append(f'<rect x="{x}" y="{gy}" width="{col_w}" height="{h}" rx="9" fill="{BOX}" stroke="{LINE}"/>'
                   f'<text x="{x + 12}" y="{gy + 20}" font-size="11" fill="{FAINT}" letter-spacing=".1em">ns/{escape(group.upper())}</text>'
                   f'<text x="{x + col_w - 12}" y="{gy + 20}" font-size="11" fill="{MUTED}" text-anchor="end">{len(names)} release{"s" if len(names) > 1 else ""}</text>')
        for index, name in enumerate(names):
            cx, cy = x + 10 + index % 2 * (chip_w + 8), gy + 30 + index // 2 * 28
            kind = kinds.get(name, "run")
            step = hops.index(name) + 1 if name in hops else None
            if step:
                attrs, stroke = f' class="hop" style="animation-delay:{(step - 1) * .45:.2f}s"', DEEP
            elif name in tel:
                attrs, stroke = f' class="tel" style="animation-delay:{len(hops) * .45 + tel.index(name) * .3:.2f}s"', LINE
            else:
                attrs, stroke = "", SOFT
            out.append(f'<rect{attrs} x="{cx}" y="{cy}" width="{chip_w}" height="{chip_h}" rx="6" fill="{RAISE}" stroke="{stroke}"/>')
            if kind == "run":
                out.append(f'<circle class="led" style="animation-delay:{index * .37 % 2.4:.2f}s" cx="{cx + 12}" cy="{cy + 11}" r="3.5" fill="{OK}"/>')
            elif kind == "cron":
                out.append(f'<circle cx="{cx + 12}" cy="{cy + 11}" r="4" fill="none" stroke="{SKY}" stroke-width="1.4"/>'
                           f'<path d="M{cx + 12} {cy + 8.5}v2.5h2" stroke="{SKY}" stroke-width="1.2" fill="none"/>')
            else:
                out.append(f'<circle cx="{cx + 12}" cy="{cy + 11}" r="4" fill="none" stroke="{FAINT}" stroke-width="1.4"/>'
                           f'<path d="M{cx + 10} {cy + 11}l1.5 1.5 2.5-3" stroke="{FAINT}" stroke-width="1.2" fill="none"/>')
            label = rename.get(name, name)
            out.append(f'<text x="{cx + 22}" y="{cy + 15}" font-size="11.5" fill="{FG if kind == "run" else MUTED}">{escape(label)}</text>')
            if step:
                out.append(f'<circle cx="{cx + chip_w - 12}" cy="{cy + 11}" r="7.5" fill="{DEEP}"/>'
                           f'<text x="{cx + chip_w - 12}" y="{cy + 14.5}" font-size="10" font-weight="600" fill="#ffffff" text-anchor="middle">{step}</text>')
            elif kind != "run":
                out.append(f'<text x="{cx + chip_w - 8}" y="{cy + 15}" font-size="10" fill="{FAINT}" text-anchor="end">{kind}</text>')
        columns[x] = gy + h + 10
    height = max(columns.values()) + 40
    entry_y = 72 + 30 + 11  # the first chip of the first group
    cycle = (len(hops) + len(tel)) * .45 + 1.2
    names = ", ".join(rename.get(name, name) for name in hops)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="The homelab k3s cluster: {len(found)} Helm releases by namespace. One question passes through {escape(names)}, then its trace lands in Tempo.">
  <style>
    .hop {{ animation: hop {cycle:.1f}s linear infinite backwards; }}
    .tel {{ animation: tel {cycle:.1f}s linear infinite backwards; }}
    @keyframes hop {{ 0%, 7% {{ stroke: {SKY}; fill: #10233f; }} 13%, 100% {{ stroke: {DEEP}; fill: {RAISE}; }} }}
    @keyframes tel {{ 0%, 7% {{ stroke: {BLUE}; }} 13%, 100% {{ stroke: {LINE}; }} }}
    .led {{ animation: pulse 2.4s ease-in-out infinite; }}
    @keyframes pulse {{ 50% {{ opacity: .35; }} }}
    @media (prefers-reduced-motion: reduce) {{ .hop, .tel, .led {{ animation: none; }} .packet {{ display: none; }} }}
  </style>
  <g font-family="{MONO}">
    <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="{INK}" stroke="{LINE}"/>
    <text x="20" y="32" font-size="13" fill="{FG}">helmfile list</text>
    <text x="820" y="32" text-anchor="end" font-size="12" fill="{FAINT}">k3s · one node · {len(found)} releases</text>
    <rect x="150" y="56" width="680" height="{height - 96}" rx="12" fill="none" stroke="{LINE}" stroke-dasharray="4 4"/>
    <text x="164" y="52" font-size="10.5" fill="{FAINT}" letter-spacing=".1em">CLUSTER homelab</text>
    <rect x="12" y="{entry_y - 26}" width="116" height="52" rx="9" fill="{RAISE}" stroke="{LINE}"/>
    <text x="70" y="{entry_y - 4}" text-anchor="middle" font-size="12" fill="{FG}">browser</text>
    <text x="70" y="{entry_y + 13}" text-anchor="middle" font-size="10" fill="{FAINT}">via tailscale</text>
    <path d="M128 {entry_y} H176" stroke="{BLUE}" stroke-width="1.6" stroke-opacity=".6"/>
    {"".join(out)}
    <g class="packet"><circle r="4.5" fill="{SKY}"><animateMotion dur="{cycle:.1f}s" repeatCount="indefinite" path="M128 {entry_y} H176" keyPoints="0;1;1" keyTimes="0;.06;1" calcMode="linear"/></circle></g>
    <g font-size="10.5" fill="{MUTED}">
      <circle cx="26" cy="{height - 20}" r="3.5" fill="{OK}"/><text x="36" y="{height - 16}">deployed</text>
      <circle cx="112" cy="{height - 20}" r="4" fill="none" stroke="{SKY}" stroke-width="1.4"/><text x="122" y="{height - 16}">cron job</text>
      <circle cx="196" cy="{height - 20}" r="4" fill="none" stroke="{FAINT}" stroke-width="1.4"/><text x="206" y="{height - 16}">one-off job</text>
      <circle cx="300" cy="{height - 20}" r="7" fill="{DEEP}"/><text x="300" y="{height - 16.5}" font-size="9.5" fill="#ffffff" text-anchor="middle">1</text><text x="314" y="{height - 16}">hops of one question · then its trace lands in Tempo</text>
    </g>
  </g>
</svg>
"""


def main() -> None:
    login, config_path, output = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    config = json.loads(config_path.read_text())
    token = os.environ.get("GITHUB_TOKEN") or None
    output.mkdir(parents=True, exist_ok=True)
    repositories: list[dict] = []

    with span("render-profile"):
        with span("github.repos"):
            repositories = owned_repositories(login, token)
        with span("github.achievements"):
            write(output / "achievements.svg", achievements.render(achievements.collect(login, token)))
        if repositories:  # without the repo list, keep yesterday's languages and hero cards
            with span("github.languages", sum(1 for repo in repositories if cards.counts_for_languages(repo, login))):
                write(output / "languages.svg", cards.languages_card(cards.language_totals(repositories, login, token)))
        if token:
            with span("graphql.contributions"):
                write(output / "streak.svg", cards.streak_card(cards.contribution_days(login, token)))
        found: list[tuple[str, str]] = []
        with span("github.helmfile"):
            settings = config["cluster"]
            found = releases(get_file(f"{login}/{settings['repo']}", settings["helmfile"], token))
        notes: dict[str, str] = {}
        with span("github.nexus"):
            notes = vault(get_tarball(f"{login}/{config['nexus']['repo']}", token))
        if notes:
            with span("render.nexus", len(notes)):
                repo = next((r for r in repositories if r["name"].lower() == config["nexus"]["repo"].lower()), None)
                write(output / "nexus.svg", nexus(config, notes, repo))
        if repositories:
            with span("render.hero"):
                write(output / "hero.svg", hero(config, repositories))
        if found:
            with span("render.cluster", len(found)):
                write(output / "cluster.svg", cluster(config, found))

    # SPANS holds children before their parent; show the root first, then children by start time.
    root_span = SPANS[-1]
    ordered = [root_span] + sorted(SPANS[:-1], key=lambda item: item["start"])
    for item in ordered:
        print(f"{'ok ' if item['ok'] else 'ERR'} {item['duration'] * 1000:7.0f} ms  {item['name']}")
    # A failed step keeps last run's card; the job still commits the rest.
    failed = [item["name"] for item in ordered if not item["ok"]]
    if failed:
        print(f"::warning::steps failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
