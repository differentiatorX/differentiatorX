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
INK, INK2, INK3, ACC = "#eceef0", "#a3a9b0", "#6b7178", "#ffb36b"
HEAT = ["#15171b", "#3b2b1c", "#6e4624", "#b46d31", "#ffb36b"]

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
    active = sum(1 for d in days if d["contributionCount"] > 0)
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    langs = {}
    for n in u["repositories"]["nodes"]:
        for e in n["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    total = sum(v for _, v in top) or 1
    W, H = 1280, 520
    # only numbers worth showing: zeros are left out instead of advertised
    candidates = [("contributions, past year", cc["contributionCalendar"]["totalContributions"]),
                  ("commits", cc["totalCommitContributions"]), ("active days", active),
                  ("public repos", u["repositories"]["totalCount"]), ("longest streak, days", longest),
                  ("pull requests", cc["totalPullRequestContributions"]), ("stars", stars), ("followers", u["followers"]["totalCount"])]
    tiles = [t for t in candidates if t[1] > 0][:4]
    parts = ['<text class="h" x="48" y="70" font-size="40">Telemetry</text>',
             f'<text class="m" x="48" y="100" font-size="14" fill="{INK3}">numbers the black hole has not reached yet</text>']
    for i, (label, val) in enumerate(tiles):
        x, y = 48 + (i % 2) * 228, 132 + (i // 2) * 116
        parts.append(f'<g class="up" style="animation-delay:{.1 + i * .08:.2f}s"><rect x="{x}" y="{y}" width="214" height="100" rx="14" fill="#0d0e11" stroke="rgba(236,238,240,.10)"/>'
                     f'<text class="h" x="{x + 18}" y="{y + 54}" font-size="40">{val}</text>'
                     f'<text class="m" x="{x + 18}" y="{y + 80}" font-size="13" fill="{INK3}">{label}</text></g>')
    # languages
    parts.append(f'<g class="up" style="animation-delay:.4s"><rect x="520" y="132" width="712" height="216" rx="14" fill="#0d0e11" stroke="rgba(236,238,240,.10)"/>'
                 f'<text class="m" x="544" y="166" font-size="13" fill="{ACC}">top languages, by bytes</text>')
    bx, palette = 544, [ACC, "#d6dade", "#9aa0a6", "#6b7178", "#45494f"]
    for i, (name, size) in enumerate(top):
        w = 664 * size / total
        parts.append(f'<rect x="{bx:.1f}" y="184" width="{max(w - 3, 2):.1f}" height="10" rx="3" fill="{palette[i]}"/>')
        bx += w
        col, row = i % 3, i // 3
        lx, ly = 544 + col * 226, 238 + row * 56
        parts.append(f'<circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{palette[i]}"/>'
                     f'<text class="b" x="{lx + 18}" y="{ly}" font-size="17" fill="{INK}">{name}</text>'
                     f'<text class="m" x="{lx + 18}" y="{ly + 22}" font-size="13" fill="{INK3}">{100 * size / total:.0f}%</text>')
    parts.append('</g>')
    # heat strip: last 52 weeks, revealed week by week
    recent = cc["contributionCalendar"]["weeks"][-52:]
    mx = max([d["contributionCount"] for w in recent for d in w["contributionDays"]] + [1])
    parts.append(f'<text class="m" x="48" y="384" font-size="13" fill="{INK3}">the last 52 weeks</text>')
    for wi, w in enumerate(recent):
        parts.append(f'<g class="wk" style="animation-delay:{.5 + wi * .025:.3f}s">')
        for d in w["contributionDays"]:
            wd = dt.date.fromisoformat(d["date"]).weekday()
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / mx))
            parts.append(f'<rect x="{48 + wi * 22.2:.1f}" y="{396 + ((wd + 1) % 7) * 13}" width="18" height="10" rx="2.5" fill="{HEAT[lvl]}"/>')
        parts.append('</g>')
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    parts.append(f'<text class="m" x="{W - 48}" y="{H - 12}" font-size="12" fill="{INK3}" text-anchor="end">read at {stamp}. refreshed twice a day.</text>')
    css = (f"@font-face{{font-family:HG;src:url(data:font/woff2;base64,{font('hanken.woff2')}) format('woff2');font-weight:400 800}}"
           f"@font-face{{font-family:PM;src:url(data:font/woff2;base64,{font('plexmono-400.woff2')}) format('woff2')}}"
           ".h{font-family:HG,system-ui,sans-serif;font-weight:700;letter-spacing:-.035em;fill:url(#metal)}"
           ".b{font-family:HG,system-ui,sans-serif}.m{font-family:PM,ui-monospace,monospace}"
                      "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub telemetry for {USER}">'
            f'<defs><linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset=".25" stop-color="#ffffff"/><stop offset="1" stop-color="#a3a9b0"/></linearGradient>'
            f'<radialGradient id="glow" cx=".85" cy="0" r=".9"><stop offset="0" stop-color="{ACC}" stop-opacity=".07"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient></defs>'
            f'<style>{css}</style><rect width="{W}" height="{H}" rx="20" fill="#060607"/><rect width="{W}" height="{H}" rx="20" fill="url(#glow)"/>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="rgba(236,238,240,.10)"/>'
            f'{"".join(parts)}</svg>')


if __name__ == "__main__":
    user = demo() if "--demo" in sys.argv else fetch()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(user), "utf-8")
    print(f"wrote {OUT}")
