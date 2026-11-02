"""Draws the profile's Telemetry card from the GitHub GraphQL API.

Runs in GitHub Actions with the built-in GITHUB_TOKEN, so it never depends on an
outside stats service. Writes dist/telemetry.svg; `--demo` draws it from sample data."""
import base64
import datetime as dt
import json
import os
import pathlib
import random
import sys
import urllib.request

USER = os.environ.get("GH_USER", "differentiatorX")
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "dist" / "telemetry.svg"
GOLD, INK, SOFT, CREAM = "#F4D35E", "#E8EEF9", "#A9B9DB", "#F4E9C8"
HEAT = ["#0F1A3A", "#1B3A7A", "#2E5FB0", "#5A8DD6", "#F4D35E"]

QUERY = """query($login:String!){ user(login:$login){
  followers{ totalCount }
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false, first:100){ totalCount
    nodes{ stargazerCount languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } } }
  contributionsCollection{ totalCommitContributions totalPullRequestContributions
    contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } } } }"""


def fetch():
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GitHub API error: {data['errors']}")
    return data["data"]["user"]


def demo():
    rnd = random.Random(1)
    today = dt.date.today()
    days = [{"date": (today - dt.timedelta(days=i)).isoformat(), "contributionCount": max(0, int(rnd.gauss(1.2, 2)))} for i in range(364, -1, -1)]
    weeks = [{"contributionDays": days[i:i + 7]} for i in range(0, len(days), 7)]
    langs = [("JavaScript", 520000), ("Python", 310000), ("TypeScript", 120000), ("C++", 90000), ("CSS", 60000)]
    return {"followers": {"totalCount": 1},
            "repositories": {"totalCount": 6, "nodes": [{"stargazerCount": 1, "languages": {"edges": [{"size": s, "node": {"name": n}} for n, s in langs]}}]},
            "contributionsCollection": {"totalCommitContributions": 120, "totalPullRequestContributions": 9,
                                        "contributionCalendar": {"totalContributions": sum(d["contributionCount"] for d in days), "weeks": weeks}}}


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c > 0 else 0
        longest = max(longest, cur)
    i = len(counts) - 1
    if counts[i] == 0:
        i -= 1                      # today isn't over yet
    current = 0
    while i >= 0 and counts[i] > 0:
        current += 1
        i -= 1
    return current, longest


def font(name):
    p = ROOT / "assets" / "fonts" / name
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


def render(u):
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    current, longest = streaks(days)
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    langs = {}
    for n in u["repositories"]["nodes"]:
        for e in n["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    total = sum(v for _, v in top) or 1
    W, H = 1280, 470
    tiles = [("contributions this year", cc["contributionCalendar"]["totalContributions"]),
             ("commits", cc["totalCommitContributions"]), ("pull requests", cc["totalPullRequestContributions"]),
             ("public repos", u["repositories"]["totalCount"]), ("stars", stars), ("followers", u["followers"]["totalCount"])]
    parts = []
    for i, (label, val) in enumerate(tiles):
        x, y = 40 + (i % 3) * 190, 40 + (i // 3) * 120
        parts.append(f'<rect x="{x}" y="{y}" width="176" height="104" rx="16" fill="#0A1638" stroke="#1B3A7A"/>'
                     f'<text class="t" x="{x + 18}" y="{y + 56}" font-size="44" fill="url(#cream)">{val}</text>'
                     f'<text class="s" x="{x + 18}" y="{y + 84}" font-size="14" fill="{SOFT}">{label}</text>')
    # streak block
    parts.append(f'<rect x="630" y="40" width="270" height="224" rx="16" fill="#0A1638" stroke="#1B3A7A"/>'
                 f'<circle cx="765" cy="122" r="56" fill="none" stroke="#1B3A7A" stroke-width="8"/>'
                 f'<circle cx="765" cy="122" r="56" fill="none" stroke="{GOLD}" stroke-width="8" stroke-linecap="round" '
                 f'stroke-dasharray="{min(1, current / max(longest, 1)) * 351.9:.1f} 400" transform="rotate(-90 765 122)"/>'
                 f'<text class="t" x="765" y="138" font-size="46" fill="url(#cream)" text-anchor="middle">{current}</text>'
                 f'<text class="s" x="765" y="208" font-size="15" fill="{INK}" text-anchor="middle">day streak, best {longest}</text>'
                 f'<text class="s" x="765" y="236" font-size="13" fill="{SOFT}" text-anchor="middle">{"keep it alive, future me" if current else "the streak fell into the hole"}</text>')
    # languages
    parts.append(f'<rect x="920" y="40" width="320" height="224" rx="16" fill="#0A1638" stroke="#1B3A7A"/>'
                 f'<text class="s" x="942" y="72" font-size="14" fill="{SOFT}" letter-spacing="2">TOP LANGUAGES</text>')
    bx, palette = 942, ["#F4D35E", "#5A8DD6", "#9FC3E8", "#E8A33D", "#2E5FB0"]
    for i, (name, size) in enumerate(top):
        w = 276 * size / total
        parts.append(f'<rect x="{bx:.1f}" y="88" width="{max(w - 2, 2):.1f}" height="12" rx="4" fill="{palette[i]}"/>')
        bx += w
        parts.append(f'<circle cx="950" cy="{126 + i * 27}" r="5" fill="{palette[i]}"/>'
                     f'<text class="s" x="964" y="{131 + i * 27}" font-size="15" fill="{INK}">{name}</text>'
                     f'<text class="s" x="1218" y="{131 + i * 27}" font-size="15" fill="{SOFT}" text-anchor="end">{100 * size / total:.0f}%</text>')
    # heat strip: last 52 weeks
    recent = cc["contributionCalendar"]["weeks"][-52:]
    mx = max([d["contributionCount"] for w in recent for d in w["contributionDays"]] + [1])
    parts.append(f'<text class="s" x="40" y="306" font-size="14" fill="{SOFT}" letter-spacing="2">THE LAST 52 WEEKS</text>')
    for wi, w in enumerate(recent):
        for d in w["contributionDays"]:
            wd = dt.date.fromisoformat(d["date"]).weekday()
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / mx))
            parts.append(f'<rect x="{40 + wi * 23.1:.1f}" y="{318 + ((wd + 1) % 7) * 18}" width="18" height="14" rx="3" fill="{HEAT[lvl]}"/>')
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    parts.append(f'<text class="s" x="{W - 40}" y="{H - 14}" font-size="12" fill="{SOFT}" text-anchor="end">read at {stamp}. refreshed twice a day, before the black hole eats them.</text>')
    css = (f"@font-face{{font-family:IS;src:url(data:font/woff2;base64,{font('serif.woff2')}) format('woff2')}}"
           f"@font-face{{font-family:GS;src:url(data:font/woff2;base64,{font('geist.woff2')}) format('woff2');font-weight:100 900}}"
           ".t{font-family:IS,Georgia,serif}.s{font-family:GS,system-ui,sans-serif}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub telemetry for {USER}">'
            f'<defs><linearGradient id="cream" x1="0" x2="1"><stop offset="0" stop-color="#FFF6D8"/><stop offset=".5" stop-color="#F4D35E"/><stop offset="1" stop-color="#FFF6D8"/></linearGradient>'
            f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#071230"/><stop offset="1" stop-color="#040916"/></linearGradient></defs>'
            f'<style>{css}</style><rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/>'
            f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="24" fill="none" stroke="#2E5FB0" stroke-opacity=".5"/>'
            f'{"".join(parts)}</svg>')


if __name__ == "__main__":
    user = demo() if "--demo" in sys.argv else fetch()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(user), "utf-8")
    print(f"wrote {OUT}")
