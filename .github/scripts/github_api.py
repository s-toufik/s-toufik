import json
import urllib.parse
import urllib.request

API = "https://api.github.com"
USER_AGENT = "profile-cards"


def get(path: str, token: str | None) -> dict | list:
    request = urllib.request.Request(
        f"{API}{path}", headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def graphql(query: str, variables: dict, token: str) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(
        f"{API}/graphql",
        data=body,
        headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]


def search_count(kind: str, query: str, token: str | None) -> int:
    return int(get(f"/search/{kind}?q={urllib.parse.quote(query)}&per_page=1", token)["total_count"])


def page(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode()
