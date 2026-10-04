import os
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from html import escape

from github_api import graphql, page

LEVEL_COLORS = ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353")
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""


@dataclass(frozen=True)
class Day:
    day: date
    count: int
    level: int


def from_api(login: str, token: str) -> tuple[list[Day], int]:
    calendar = graphql(QUERY, {"login": login}, token)["user"]["contributionsCollection"]["contributionCalendar"]
    days = [
        Day(date.fromisoformat(d["date"]), d["contributionCount"], LEVELS[d["contributionLevel"]])
        for week in calendar["weeks"]
        for d in week["contributionDays"]
    ]
    return days, calendar["totalContributions"]


def from_page(login: str) -> tuple[list[Day], int]:
    html = page(f"https://github.com/users/{login}/contributions")
    cells = re.findall(r'<td[^>]*data-date="([^"]+)"[^>]*id="([^"]+)"[^>]*data-level="(\d)"', html)
    counts = {
        target: int(number.replace(",", "")) if number else 0
        for target, number in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>\s*(?:No|([\d,]+)) contributions?', html)
    }
    days = sorted(
        (Day(date.fromisoformat(d), counts.get(cell_id, 0), int(level)) for d, cell_id, level in cells),
        key=lambda d: d.day,
    )
    return days, sum(d.count for d in days)


def render(days: list[Day], total: int) -> str:
    cell, step, left, top = 11, 14, 36, 52
    first_sunday = days[0].day - timedelta(days=(days[0].day.weekday() + 1) % 7)
    weeks = (days[-1].day - first_sunday).days // 7 + 1
    width = left + weeks * step + 16
    height = top + 7 * step + 40

    squares = []
    for d in days:
        column = (d.day - first_sunday).days // 7
        row = (d.day.weekday() + 1) % 7
        label = f"{d.count} contribution{'s' if d.count != 1 else ''} on {d.day:%b %-d, %Y}"
        squares.append(
            f'<rect x="{left + column * step}" y="{top + row * step}" width="{cell}" height="{cell}" rx="2" '
            f'fill="{LEVEL_COLORS[d.level]}" stroke="#ffffff" stroke-opacity="0.05"><title>{label}</title></rect>'
        )

    months, last_column = [], -3
    for column in range(weeks):
        week_start = first_sunday + timedelta(weeks=column)
        if week_start.day <= 7 and column - last_column >= 3 and week_start >= days[0].day - timedelta(days=6):
            months.append(f'<text x="{left + column * step}" y="{top - 8}" class="axis">{MONTHS[week_start.month - 1]}</text>')
            last_column = column

    weekdays = "".join(
        f'<text x="{left - 8}" y="{top + row * step + 9}" text-anchor="end" class="axis">{name}</text>'
        for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    legend_y = top + 7 * step + 18
    legend_x = width - 16 - 5 * step - 34
    legend = "".join(
        f'<rect x="{legend_x + i * step}" y="{legend_y - 9}" width="{cell}" height="{cell}" rx="2" '
        f'fill="{color}" stroke="#ffffff" stroke-opacity="0.05"/>'
        for i, color in enumerate(LEVEL_COLORS)
    )
    span = f"{days[0].day:%b %-d, %Y} – {days[-1].day:%b %-d, %Y}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} contributions in the last year">
  <style>
    text {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
    .heading {{ font-size: 15px; font-weight: 600; fill: #e6edf3; }}
    .axis {{ font-size: 10px; fill: #8b949e; }}
    .meta {{ font-size: 11px; fill: #8b949e; }}
  </style>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
  <text x="16" y="24" class="heading">{total:,} contributions in the last year</text>
  {''.join(months)}
  {weekdays}
  {''.join(squares)}
  <text x="16" y="{legend_y}" class="meta">{escape(span)}</text>
  <text x="{legend_x - 6}" y="{legend_y}" text-anchor="end" class="meta">Less</text>
  {legend}
  <text x="{legend_x + 5 * step + 2}" y="{legend_y}" class="meta">More</text>
</svg>
"""


def main() -> None:
    login, output = sys.argv[1], sys.argv[2]
    token = os.environ.get("GITHUB_TOKEN")
    try:
        if not token:
            raise RuntimeError("no token")
        days, total = from_api(login, token)
    except Exception as error:
        print(f"API unavailable ({error}); reading the public contributions page")
        days, total = from_page(login)
    with open(output, "w", encoding="utf-8") as file:
        file.write(render(days, total))
    print(f"{total} contributions, {len(days)} days, {days[0].day} to {days[-1].day}")


if __name__ == "__main__":
    main()
