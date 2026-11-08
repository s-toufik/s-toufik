"""Render the profile cards (project pins, languages, contribution streak) as static SVGs.

Usage: cards.py <login> <output-dir> <repo> [<repo> ...]

The streak card needs a token (GitHub's GraphQL API refuses anonymous calls);
without one it is skipped and the previously committed card is kept.
"""

import os
import sys
from datetime import UTC, date, datetime
from html import escape
from pathlib import Path

from github_api import get, graphql, owned_repositories

FONT = '-apple-system, "Segoe UI", Helvetica, Arial, sans-serif'
BG, BORDER, TEXT, MUTED, ACCENT = "#0d1117", "#30363d", "#e6edf3", "#8b949e", "#60a5fa"
TRACK = "#1f2937"

# Colours from github/linguist, so the cards match the language bar on each repository.
LANGUAGE_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Shell": "#89e051",
    "Rust": "#dea584", "C++": "#f34b7d", "C": "#555555", "Go": "#00ADD8", "Go Template": "#00ADD8",
    "Makefile": "#427819", "CMake": "#DA3434", "Dockerfile": "#384d54", "HTML": "#e34c26",
    "CSS": "#663399", "SCSS": "#c6538c", "Jupyter Notebook": "#DA5B0B", "Java": "#b07219",
    "Kotlin": "#A97BFF", "Mako": "#7e858d", "Smarty": "#f0c040", "PLpgSQL": "#336790",
    "HCL": "#844FBA", "Jinja": "#a52a22", "Lua": "#000080", "Nix": "#7e7eff", "Batchfile": "#C1F12E",
}
OTHER = "#8b949e"

REPO_ICON = (
    '<path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 '
    '0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 '
    '0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"/>'
)
STAR_ICON = (
    '<path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 '
    '12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>'
)
FORK_ICON = (
    '<path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 '
    '2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 '
    '0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"/>'
)


def svg(width: int, height: int, label: str, body: str, extra_style: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
  <style>
    text {{ font-family: {FONT}; }}
    .heading {{ font-size: 16px; font-weight: 700; fill: {TEXT}; }}
    .muted {{ font-size: 12px; fill: {MUTED}; }}{extra_style}
  </style>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>{body}
</svg>
"""


def wrap(text: str, width: int, lines: int) -> list[str]:
    words, out, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= width:
            current = candidate
            continue
        out.append(current)
        current = word
        if len(out) == lines:
            break
    else:
        if current:
            out.append(current)
        return out
    last = out[-1]
    return out[:-1] + [(last[: width - 1].rstrip() + "…") if len(last) >= width - 1 else last + "…"]


def human_date(value: str) -> str:
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return f"{moment:%b} {moment.day}, {moment.year}"


# --- project pin -----------------------------------------------------------------------------


def pin_card(repo: dict) -> str:
    width, height = 440, 140
    description = repo["description"] or "No description yet."
    lines = wrap(description, 62, 2)
    language = repo["language"]
    footer, x = [], 20
    if language:
        color = LANGUAGE_COLORS.get(language, OTHER)
        footer.append(f'<circle cx="{x + 6}" cy="114" r="6" fill="{color}"/>'
                      f'<text x="{x + 18}" y="118" class="muted">{escape(language)}</text>')
        x += 30 + int(len(language) * 7)
    footer.append(f'<g transform="translate({x} 106)" fill="{MUTED}">{STAR_ICON}</g>'
                  f'<text x="{x + 21}" y="118" class="muted">{repo["stargazers_count"]:,}</text>')
    x += 34 + len(f"{repo['stargazers_count']:,}") * 7
    footer.append(f'<g transform="translate({x} 106)" fill="{MUTED}">{FORK_ICON}</g>'
                  f'<text x="{x + 20}" y="118" class="muted">{repo["forks_count"]:,}</text>')
    description_text = "".join(
        f'<text x="20" y="{70 + index * 19}" class="desc">{escape(line)}</text>' for index, line in enumerate(lines)
    )
    body = f"""
  <g transform="translate(20 22)" fill="{MUTED}">{REPO_ICON}</g>
  <text x="44" y="35" class="name">{escape(repo["name"])}</text>
  <text x="{width - 20}" y="35" text-anchor="end" class="pill">{"archived" if repo.get("archived") else "public"}</text>
  {description_text}
  {"".join(footer)}
  <text x="{width - 20}" y="118" text-anchor="end" class="muted">updated {human_date(repo["pushed_at"])}</text>"""
    style = f"""
    .name {{ font-size: 16px; font-weight: 700; fill: {ACCENT}; }}
    .desc {{ font-size: 13px; fill: {MUTED}; }}
    .pill {{ font-size: 11px; fill: {MUTED}; letter-spacing: .5px; }}"""
    return svg(width, height, f"{repo['name']}: {description}", body, style)


# --- languages -------------------------------------------------------------------------------


def language_totals(repositories: list[dict], login: str, token: str | None) -> dict[str, int]:
    totals: dict[str, int] = {}
    for repo in repositories:
        if repo["archived"] or repo["name"].startswith("_") or repo["name"].lower() == login.lower():
            continue
        for language, size in get(f"/repos/{repo['full_name']}/languages", token).items():
            totals[language] = totals.get(language, 0) + size
    return totals


def languages_card(totals: dict[str, int], width: int = 440, height: int = 200) -> str:
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    top, rest = ranked[:7], sum(size for _, size in ranked[7:])
    if rest:
        top.append(("Other", rest))
    total = sum(size for _, size in top) or 1
    bar_width, x, segments = width - 40, 20.0, []
    for language, size in top:
        share = size / total * bar_width
        color = LANGUAGE_COLORS.get(language, OTHER)
        segments.append(f'<rect x="{x:.2f}" y="56" width="{max(share, 0.5):.2f}" height="10" fill="{color}"/>')
        x += share
    legend = []
    for index, (language, size) in enumerate(top):
        column, row = index % 2, index // 2
        lx, ly = 20 + column * (width - 40) // 2, 98 + row * 26
        color = LANGUAGE_COLORS.get(language, OTHER)
        legend.append(f'<circle cx="{lx + 6}" cy="{ly - 4}" r="6" fill="{color}"/>'
                      f'<text x="{lx + 20}" y="{ly}" class="lang">{escape(language)}</text>'
                      f'<text x="{lx + (width - 40) // 2 - 24}" y="{ly}" text-anchor="end" class="muted">{size / total:.1%}</text>')
    body = f"""
  <text x="20" y="34" class="heading">Most used languages</text>
  <clipPath id="bar"><rect x="20" y="56" width="{bar_width}" height="10" rx="5"/></clipPath>
  <g clip-path="url(#bar)">{"".join(segments)}</g>
  {"".join(legend)}"""
    style = f"\n    .lang {{ font-size: 13px; fill: {TEXT}; }}"
    return svg(width, height, "Most used languages: " + ", ".join(lang for lang, _ in top), body, style)


# --- contribution streak ---------------------------------------------------------------------

CALENDAR = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def contribution_days(login: str, token: str) -> list[tuple[date, int]]:
    calendar = graphql(CALENDAR, {"login": login}, token)["user"]["contributionsCollection"]["contributionCalendar"]
    return [
        (date.fromisoformat(day["date"]), day["contributionCount"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]


def streaks(days: list[tuple[date, int]], today: date) -> tuple[int, int, int]:
    days = [(day, count) for day, count in days if day <= today]
    longest = run = 0
    for _, count in days:
        run = run + 1 if count else 0
        longest = max(longest, run)
    current = 0
    for index, (day, count) in enumerate(reversed(days)):
        if count:
            current += 1
        elif index == 0 and day == today:
            continue  # today isn't over yet; a streak survives until midnight
        else:
            break
    return sum(count for _, count in days), current, longest


def streak_card(days: list[tuple[date, int]], width: int = 440, height: int = 200) -> str:
    total, current, longest = streaks(days, datetime.now(UTC).date())
    recent = days[-30:]
    peak = max((count for _, count in recent), default=0) or 1
    bars = "".join(
        f'<rect x="{20 + index * 13.4:.1f}" y="{180 - max(2, count / peak * 30):.1f}" width="9" '
        f'height="{max(2, count / peak * 30):.1f}" rx="2" fill="{ACCENT if count else TRACK}"/>'
        for index, (_, count) in enumerate(recent)
    )

    def stat(x: int, value: int, label: str, highlight: bool = False, unit: str = "") -> str:
        cls = "big hl" if highlight else "big"
        suffix = f'<tspan class="unit"> {unit}</tspan>' if unit else ""
        return (f'<text x="{x}" y="96" text-anchor="middle" class="{cls}">{value:,}{suffix}</text>'
                f'<text x="{x}" y="120" text-anchor="middle" class="muted">{label}</text>')

    third = width // 3
    body = f"""
  <text x="20" y="34" class="heading">Contributions</text>
  <text x="{width - 20}" y="34" text-anchor="end" class="muted">last 12 months</text>
  {stat(third // 2, total, "contributions")}
  {stat(third + third // 2, current, "current streak", True, "days")}
  {stat(2 * third + third // 2, longest, "longest streak", unit="days")}
  <line x1="{third}" y1="70" x2="{third}" y2="124" stroke="{TRACK}"/>
  <line x1="{2 * third}" y1="70" x2="{2 * third}" y2="124" stroke="{TRACK}"/>
  <text x="20" y="144" class="muted">last 30 days</text>
  {bars}"""
    style = f"""
    .big {{ font-size: 28px; font-weight: 700; fill: {TEXT}; }}
    .hl {{ fill: {ACCENT}; }}
    .unit {{ font-size: 13px; font-weight: 400; fill: {MUTED}; }}"""
    label = f"{total} contributions in the last year, current streak {current} days, longest {longest} days"
    return svg(width, height, label, body, style)


def main() -> None:
    login, output, featured = sys.argv[1], Path(sys.argv[2]), sys.argv[3:]
    token = os.environ.get("GITHUB_TOKEN") or None
    output.mkdir(parents=True, exist_ok=True)

    repositories = owned_repositories(login, token)
    by_name = {repo["name"].lower(): repo for repo in repositories}
    for name in featured:
        repo = by_name.get(name.lower())
        if repo is None:
            print(f"skip pin {name}: repository not found or not public", file=sys.stderr)
            continue
        (output / f"repo-{repo['name']}.svg").write_text(pin_card(repo), encoding="utf-8")
        print(f"pin       {repo['name']}")

    (output / "languages.svg").write_text(languages_card(language_totals(repositories, login, token)), encoding="utf-8")
    print("languages ok")

    if token:
        (output / "streak.svg").write_text(streak_card(contribution_days(login, token)), encoding="utf-8")
        print("streak    ok")
    else:
        print("streak    skipped: set GITHUB_TOKEN to render it", file=sys.stderr)


if __name__ == "__main__":
    main()
