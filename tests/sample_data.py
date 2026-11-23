"""Synthetic GitHub data so the renderers can be tested without a network."""

from datetime import date, timedelta

LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]


def sample_data() -> dict:
    start = date(2025, 11, 23)  # a Sunday
    weeks, day = [], start
    for w in range(53):
        week = []
        for _ in range(7):
            n = (w * 7 + day.toordinal()) % 9
            week.append({"date": day.isoformat(), "count": n, "level": LEVELS[min(n // 2, 4)]})
            day += timedelta(days=1)
        weeks.append(week)
    return {
        "login": "example",
        "contributions_total": 123,
        "commits": 100,
        "pull_requests": 13,
        "issues": 10,
        "reviews": 0,
        "public_repos": 4,
        "pypi_packages": 2,
        "languages": {"Python": 7000, "TypeScript": 2000, "JavaScript": 800, "CSS": 150, "Shell": 50},
        "weeks": weeks,
    }
