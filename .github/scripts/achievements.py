import json
import os
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape

API = "https://api.github.com"
TIERS = ("Bronze", "Silver", "Gold", "Platinum", "Diamond")
TIER_COLORS = ("#cd7f32", "#c0c7d1", "#f5c542", "#7dd3fc", "#a78bfa")
LOCKED = "#30363d"

ICONS = {
    "commit": '<circle cx="12" cy="12" r="4" fill="none" stroke="{c}" stroke-width="2"/>'
    '<path d="M2 12h6M16 12h6" stroke="{c}" stroke-width="2" stroke-linecap="round"/>',
    "pull": '<circle cx="6" cy="5" r="2.5" fill="none" stroke="{c}" stroke-width="2"/>'
    '<circle cx="6" cy="19" r="2.5" fill="none" stroke="{c}" stroke-width="2"/>'
    '<circle cx="18" cy="19" r="2.5" fill="none" stroke="{c}" stroke-width="2"/>'
    '<path d="M6 8v8M18 16V9a3 3 0 0 0-3-3h-4" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"/>',
    "issue": '<circle cx="12" cy="12" r="9" fill="none" stroke="{c}" stroke-width="2"/>'
    '<circle cx="12" cy="12" r="2" fill="{c}"/>',
    "repo": '<path d="M5 4h12a2 2 0 0 1 2 2v14H7a2 2 0 0 1-2-2z" fill="none" stroke="{c}" stroke-width="2"/>'
    '<path d="M5 16a2 2 0 0 1 2-2h12" fill="none" stroke="{c}" stroke-width="2"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z" '
    'fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16" fill="none" stroke="{c}" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"/>',
    "clock": '<circle cx="12" cy="12" r="9" fill="none" stroke="{c}" stroke-width="2"/>'
    '<path d="M12 7v5l3 3" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"/>',
    "people": '<circle cx="9" cy="8" r="3.5" fill="none" stroke="{c}" stroke-width="2"/>'
    '<path d="M2.5 20a6.5 6.5 0 0 1 13 0" fill="none" stroke="{c}" stroke-width="2"/>'
    '<path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14.5a6.5 6.5 0 0 1 3.5 5.5" fill="none" stroke="{c}" '
    'stroke-width="2" stroke-linecap="round"/>',
}


@dataclass(frozen=True)
class Achievement:
    title: str
    icon: str
    unit: str
    value: int
    thresholds: tuple[int, ...]

    @property
    def tier(self) -> int:
        return sum(1 for threshold in self.thresholds if self.value >= threshold) - 1

    @property
    def next_threshold(self) -> int | None:
        tier = self.tier
        return self.thresholds[tier + 1] if tier + 1 < len(self.thresholds) else None

    @property
    def progress(self) -> float:
        nxt = self.next_threshold
        if nxt is None:
            return 1.0
        start = self.thresholds[self.tier] if self.tier >= 0 else 0
        return max(0.0, min(1.0, (self.value - start) / (nxt - start)))


def get(path: str, token: str | None, accept: str = "application/vnd.github+json") -> dict | list:
    request = urllib.request.Request(f"{API}{path}", headers={"Accept": accept, "User-Agent": "profile-achievements"})
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def search_count(kind: str, query: str, token: str | None) -> int:
    return int(get(f"/search/{kind}?q={urllib.parse.quote(query)}&per_page=1", token)["total_count"])


def owned_repositories(login: str, token: str | None) -> list[dict]:
    repositories: list[dict] = []
    page = 1
    while True:
        batch = get(f"/users/{login}/repos?type=owner&per_page=100&page={page}", token)
        repositories += [repo for repo in batch if not repo["fork"]]
        if len(batch) < 100:
            return repositories
        page += 1


def collect(login: str, token: str | None) -> list[Achievement]:
    user = get(f"/users/{login}", token)
    repositories = owned_repositories(login, token)
    created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    years = (datetime.now(UTC) - created).days // 365
    return [
        Achievement("Committer", "commit", "commits", search_count("commits", f"author:{login}", token), (10, 100, 500, 1000, 5000)),
        Achievement("Pull requests", "pull", "opened", search_count("issues", f"author:{login} type:pr", token), (1, 10, 50, 100, 500)),
        Achievement("Issues", "issue", "opened", search_count("issues", f"author:{login} type:issue", token), (1, 10, 50, 100, 250)),
        Achievement("Builder", "repo", "repositories", len(repositories), (1, 5, 10, 25, 50)),
        Achievement("Stargazed", "star", "stars earned", sum(repo["stargazers_count"] for repo in repositories), (1, 10, 50, 100, 500)),
        Achievement("Polyglot", "code", "languages", len({repo["language"] for repo in repositories if repo["language"]}), (1, 2, 3, 5, 8)),
        Achievement("Veteran", "clock", "years on GitHub", years, (1, 2, 3, 5, 10)),
        Achievement("Community", "people", "followers", user["followers"], (1, 10, 50, 100, 500)),
    ]


def tile(achievement: Achievement, x: int, y: int, width: int, height: int) -> str:
    unlocked = achievement.tier >= 0
    color = TIER_COLORS[achievement.tier] if unlocked else LOCKED
    tier = TIERS[achievement.tier] if unlocked else "Locked"
    nxt = achievement.next_threshold
    goal = f"next tier at {nxt:,}" if nxt is not None else "highest tier reached"
    bar = int((width - 36) * achievement.progress)
    icon = ICONS[achievement.icon].format(c=color)
    return f"""
  <g transform="translate({x} {y})">
    <rect width="{width}" height="{height}" rx="12" fill="#111827" stroke="#1f2937"/>
    <circle cx="36" cy="38" r="20" fill="{color}" fill-opacity="0.14" stroke="{color}" stroke-opacity="0.6"/>
    <g transform="translate(24 26)">{icon}</g>
    <text x="68" y="33" class="title">{escape(achievement.title)}</text>
    <text x="68" y="52" class="tier" fill="{color}">{tier}</text>
    <text x="18" y="84" class="value">{achievement.value:,}<tspan class="unit"> {escape(achievement.unit)}</tspan></text>
    <rect x="18" y="96" width="{width - 36}" height="6" rx="3" fill="#1f2937"/>
    <rect x="18" y="96" width="{bar}" height="6" rx="3" fill="{color}"/>
    <text x="18" y="120" class="goal">{goal}</text>
  </g>"""


def render(achievements: list[Achievement]) -> str:
    columns, width, height, gap, top = 4, 210, 132, 12, 52
    rows = (len(achievements) + columns - 1) // columns
    total_width = columns * width + (columns + 1) * gap
    total_height = top + rows * height + (rows + 1) * gap - gap + 8
    unlocked = sum(1 for achievement in achievements if achievement.tier >= 0)
    tiles = "".join(
        tile(achievement, gap + (index % columns) * (width + gap), top + (index // columns) * (height + gap), width, height)
        for index, achievement in enumerate(achievements)
    )
    updated = datetime.now(UTC).strftime("%Y-%m-%d")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height}" viewBox="0 0 {total_width} {total_height}" role="img" aria-label="GitHub achievements">
  <style>
    text {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
    .heading {{ font-size: 16px; font-weight: 700; fill: #e6edf3; }}
    .meta {{ font-size: 12px; fill: #8b949e; }}
    .title {{ font-size: 14px; font-weight: 600; fill: #e6edf3; }}
    .tier {{ font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }}
    .value {{ font-size: 18px; font-weight: 700; fill: #e6edf3; }}
    .unit {{ font-size: 12px; font-weight: 400; fill: #8b949e; }}
    .goal {{ font-size: 11px; fill: #6b7280; }}
  </style>
  <rect x="0.5" y="0.5" width="{total_width - 1}" height="{total_height - 1}" rx="14" fill="#0d1117" stroke="#30363d"/>
  <text x="{gap + 6}" y="32" class="heading">Achievements</text>
  <text x="{total_width - gap - 6}" y="32" text-anchor="end" class="meta">{unlocked} of {len(achievements)} unlocked · updated {updated}</text>{tiles}
</svg>
"""


def main() -> None:
    login, output = sys.argv[1], sys.argv[2]
    achievements = collect(login, os.environ.get("GITHUB_TOKEN") or None)
    with open(output, "w", encoding="utf-8") as file:
        file.write(render(achievements))
    for achievement in achievements:
        tier = TIERS[achievement.tier] if achievement.tier >= 0 else "Locked"
        print(f"{achievement.title:14} {achievement.value:>6} {tier}")


if __name__ == "__main__":
    main()
