"""Render every profile card and a trace of the run that drew them.

Usage: render.py <login> <config.json> <output-dir>

Each step is timed as a span; the spans become cards/trace.svg, so the README shows
the telemetry of the pipeline that rendered it. A step that fails keeps the card
committed by the previous run instead of failing the whole job.
"""

import json
import os
import re
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import UTC, datetime
from html import escape
from pathlib import Path

import achievements
import cards
from github_api import get_file, owned_repositories

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


def hero(config: dict, repositories: list[dict]) -> str:
    by_name = {repo["name"].lower(): repo for repo in repositories}
    rows = [(item, by_name[item["repo"].lower()]) for item in config["featured"] if item["repo"].lower() in by_name]
    width, top = 840, 186
    height = top + len(rows) * 22 + 46
    prompt = f'<tspan fill="{BLUE}">toufik@homelab</tspan><tspan fill="{FAINT}">:~$ </tspan>'
    lines, delay = [], 1.35
    for index, (item, repo) in enumerate(rows):
        y = top + index * 22
        days = ago(repo["pushed_at"])
        state, color = ("ready", OK) if days <= 14 else ("idle", WARN) if days <= 90 else ("dormant", FAINT)
        led = (f'<circle class="led" style="animation-delay:{index * .3:.1f}s" cx="30" cy="{y - 5}" r="4" fill="{color}"/>'
               if state == "ready" else f'<circle cx="30" cy="{y - 5}" r="4" fill="none" stroke="{color}" stroke-width="1.6"/>')
        when = "today" if days == 0 else f"{days}d ago"
        lines.append(
            f'<g class="typed" style="animation-delay:{delay + index * .1:.2f}s">{led}<text x="44" y="{y}">'
            f'<tspan fill="{FG}">{escape(repo["name"])}</tspan>'
            f'<tspan x="234" fill="{MUTED}">{escape(item.get("lang") or repo["language"] or "—")}</tspan>'
            f'<tspan x="354" fill="{color}">{state}</tspan><tspan x="434" fill="{MUTED}">{when}</tspan>'
            f'<tspan x="534" fill="{FAINT}">{escape(item["role"])}</tspan></text></g>'
        )
    end = delay + len(rows) * .1 + .25
    last = height - 22
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Terminal: {escape(config['name'])}. {escape(config['tagline'])} Project status: {escape(', '.join(item['repo'] for item, _ in rows))}">
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
    <text x="24" y="68" class="typed" style="animation-delay:.1s">{prompt}<tspan fill="{FG}">whoami</tspan></text>
    <text x="24" y="90" class="typed" style="animation-delay:.4s" fill="{FG}">{escape(config["name"])}</text>
    <text x="24" y="110" class="typed" style="animation-delay:.5s" fill="{MUTED}">{escape(config["tagline"])}</text>
    <text x="24" y="142" class="typed" style="animation-delay:.9s">{prompt}<tspan fill="{FG}">homelab status --apps</tspan></text>
    <text x="24" y="166" class="typed" style="animation-delay:1.2s" fill="{FAINT}" font-size="12" letter-spacing=".08em"><tspan x="44">SERVICE</tspan><tspan x="234">LANG</tspan><tspan x="354">STATE</tspan><tspan x="434">LAST PUSH</tspan><tspan x="534">ROLE</tspan></text>
    {"".join(lines)}
    <text x="24" y="{last}" class="typed" style="animation-delay:{end:.2f}s">{prompt}<tspan class="cursor" fill="{BLUE}">█</tspan></text>
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


# --- trace: the waterfall of this run --------------------------------------------------------


def trace(spans: list[dict], total: float) -> str:
    width, left, right, row = 840, 250, 818, 24
    height = 76 + len(spans) * row + 30
    scale = (right - left) / total
    ticks = [total * i / 4 for i in range(5)]
    grid = "".join(f'<line x1="{left + t * scale:.1f}" y1="44" x2="{left + t * scale:.1f}" y2="{height - 30}" stroke="{SOFT}"/>' for t in ticks)
    labels = "".join(
        f'<text x="{left + t * scale:.1f}" y="{height - 14}" text-anchor="{"start" if i == 0 else "end" if i == 4 else "middle"}">{t:.1f} s</text>'
        for i, t in enumerate(ticks)
    )
    bars = []
    for index, item in enumerate(spans):
        y = 58 + index * row
        root = index == 0
        color = DEEP if root else (SKY if item["name"].startswith(("github", "graphql")) else BLUE)
        if not item["ok"]:
            color = WARN
        name = item["name"] + (f" ×{item['count']}" if item["count"] else "")
        x, w = left + item["start"] * scale, max(2.0, item["duration"] * scale)
        ms = f"{item['duration'] * 1000:,.0f} ms"
        # the duration goes after the bar, or inside its end when the bar reaches the right edge
        text_w = len(ms) * 6.5
        if x + w + 6 + text_w < right:    # after the bar
            label = f'<text x="{x + w + 6:.1f}" y="{y + 10}" font-size="10.5" fill="{FAINT}">{ms}</text>'
        elif w > text_w + 12:             # inside the end of a long bar
            label = f'<text x="{x + w - 6:.1f}" y="{y + 10}" font-size="10.5" fill="{INK}" text-anchor="end">{ms}</text>'
        else:                             # before a short bar at the right edge
            label = f'<text x="{x - 6:.1f}" y="{y + 10}" font-size="10.5" fill="{FAINT}" text-anchor="end">{ms}</text>'
        bars.append(
            f'<text x="{20 if root else 34}" y="{y + 10}" fill="{FG if root else MUTED}">{escape(name)}</text>'
            f'<rect class="grow" style="animation-delay:{index * .08:.2f}s" x="{x:.1f}" y="{y}" width="{w:.1f}" height="12" rx="3" fill="{color}"/>'
            + label
        )
    failed = sum(1 for item in spans if not item["ok"])
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    status = f"{failed} failed" if failed else "all ok"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Trace of the run that rendered this profile on {stamp}: {len(spans)} spans in {total:.1f} seconds, {status}">
  <style>
    .grow {{ transform-box: fill-box; transform-origin: left; animation: grow .7s cubic-bezier(.2,.7,.2,1) backwards; }}
    @keyframes grow {{ from {{ transform: scaleX(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .grow {{ animation: none; }} }}
  </style>
  <g font-family="{MONO}" font-size="12">
    <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="{INK}" stroke="{LINE}"/>
    <text x="20" y="30" fill="{FG}" font-size="13">trace render-profile</text>
    <text x="820" y="30" text-anchor="end" fill="{FAINT}">{stamp} · {len(spans)} spans · {total:.1f} s · {status}</text>
    {grid}
    <g fill="{FAINT}" font-size="10.5">{labels}</g>
    {"".join(bars)}
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
        with span("github.languages", sum(1 for repo in repositories if cards.counts_for_languages(repo, login))):
            write(output / "languages.svg", cards.languages_card(cards.language_totals(repositories, login, token)))
        if token:
            with span("graphql.contributions"):
                write(output / "streak.svg", cards.streak_card(cards.contribution_days(login, token)))
            found: list[tuple[str, str]] = []
        with span("github.helmfile"):
            settings = config["cluster"]
            found = releases(get_file(f"{login}/{settings['repo']}", settings["helmfile"], token))
        with span("render.hero"):
            write(output / "hero.svg", hero(config, repositories))
        if found:
            with span("render.cluster", len(found)):
                write(output / "cluster.svg", cluster(config, found))
    
    # SPANS holds children before their parent; show the root first, then children by start time.
    root_span = SPANS[-1]
    ordered = [root_span] + sorted(SPANS[:-1], key=lambda item: item["start"])
    write(output / "trace.svg", trace(ordered, root_span["duration"]))
    for item in ordered:
        print(f"{'ok ' if item['ok'] else 'ERR'} {item['duration'] * 1000:7.0f} ms  {item['name']}")
    # A failed step keeps last run's card and shows up in amber on the trace; the job still commits the rest.
    failed = [item["name"] for item in ordered if not item["ok"]]
    if failed:
        print(f"::warning::steps failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
