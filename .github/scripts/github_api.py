import json
import urllib.parse
import urllib.request

API = "https://api.github.com"
USER_AGENT = "profile-cards"


def _request(url: str, token: str | None, body: bytes | None = None) -> dict | list:
    request = urllib.request.Request(
        url, data=body, headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def get(path: str, token: str | None) -> dict | list:
    return _request(f"{API}{path}", token)


def get_file(repo: str, path: str, token: str | None) -> str:
    request = urllib.request.Request(
        f"{API}/repos/{repo}/contents/{urllib.parse.quote(path)}",
        headers={"Accept": "application/vnd.github.raw", "User-Agent": USER_AGENT},
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode()


def graphql(query: str, variables: dict, token: str) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode()
    result = _request(f"{API}/graphql", token, payload)
    if result.get("errors"):
        raise RuntimeError(result["errors"])
    return result["data"]


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
