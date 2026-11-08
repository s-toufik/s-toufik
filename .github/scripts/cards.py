"""Shared SVG helpers plus the languages and contribution streak cards. render.py drives them."""

from datetime import UTC, date, datetime
from html import escape

from github_api import get, graphql

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


# --- languages -------------------------------------------------------------------------------


def counts_for_languages(repo: dict, login: str) -> bool:
    return not (repo["archived"] or repo["name"].startswith("_") or repo["name"].lower() == login.lower())


def language_totals(repositories: list[dict], login: str, token: str | None) -> dict[str, int]:
    totals: dict[str, int] = {}
    for repo in repositories:
        if not counts_for_languages(repo, login):
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
