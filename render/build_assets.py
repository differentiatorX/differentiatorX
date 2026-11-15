"""Builds every profile panel in assets/ as an animated SVG.

Each panel is a dark, self-contained card, so it reads the same on GitHub's light
and dark themes. Fonts are embedded (Hanken Grotesk, IBM Plex Mono, both OFL), all
motion is CSS or SMIL inside the SVG, and `prefers-reduced-motion` shows the
finished state. Run: python render/build_assets.py
"""
import base64
import math
import pathlib
import random
from html import escape

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
W = 1280
INK, INK2, INK3, ACC = "#eceef0", "#a3a9b0", "#6b7178", "#ffb36b"
BG, LINE = "#060607", "rgba(236,238,240,.10)"
FW500, FW650 = ' font-weight="500"', ' font-weight="650"'
NBSP = " "
END, MID, CHK = ' text-anchor="end"', ' text-anchor="middle"', "✓"


def b64(path):
    return base64.b64encode((ROOT / path).read_bytes()).decode()


FONTS = (
    f"@font-face{{font-family:HG;src:url(data:font/woff2;base64,{b64('assets/fonts/hanken.woff2')}) format('woff2');font-weight:400 800}}"
    f"@font-face{{font-family:PM;src:url(data:font/woff2;base64,{b64('assets/fonts/plexmono-400.woff2')}) format('woff2');font-weight:400}}"
    f"@font-face{{font-family:PM;src:url(data:font/woff2;base64,{b64('assets/fonts/plexmono-500.woff2')}) format('woff2');font-weight:500}}"
)
BASE_CSS = (
    ".h{font-family:HG,system-ui,sans-serif;font-weight:700;letter-spacing:-.035em;fill:url(#metal)}"
    ".b{font-family:HG,system-ui,sans-serif;fill:" + INK2 + "}"
    ".m{font-family:PM,ui-monospace,monospace;fill:" + INK3 + "}"
    ".ink{fill:" + INK + "}.acc{fill:" + ACC + "}"
        # no entrance fades: a static render (GitHub mobile, link previews) must show everything
    ".tw{animation:tw 4s ease-in-out infinite}@keyframes tw{50%{opacity:.15}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def stars(w, h, n, seed, twinkle=6):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([.6, .7, .8, 1, 1.2])
        o = rnd.uniform(.12, .5)
        cls = ' class="tw"' if i < twinkle else ""
        delay = f' style="animation-delay:-{rnd.uniform(0, 4):.1f}s"' if i < twinkle else ""
        out.append(f'<circle{cls}{delay} cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" opacity="{o:.2f}"/>')
    return "".join(out)


def svg(h, body, label, css="", seed=1, nstars=70):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{escape(label)}">'
        f'<defs><linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset=".25" stop-color="#ffffff"/><stop offset="1" stop-color="#a3a9b0"/></linearGradient>'
        f'<radialGradient id="glow" cx=".85" cy="0" r=".9"><stop offset="0" stop-color="{ACC}" stop-opacity=".07"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="pc"><rect width="{W}" height="{h}" rx="20"/></clipPath></defs>'
        f'<style>{FONTS}{BASE_CSS}{css}</style>'
        f'<g clip-path="url(#pc)"><rect width="{W}" height="{h}" fill="{BG}"/><rect width="{W}" height="{h}" fill="url(#glow)"/>{stars(W, h, nstars, seed)}{body}</g>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="20" fill="none" stroke="{LINE}"/></svg>'
    )


def text(x, y, s, cls, size, extra=""):
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}"{extra}>{escape(s)}</text>'


def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur]


def write(name, content):
    (ASSETS / name).write_text(content, "utf-8")
    print(f"{name:22s} {len(content.encode()) // 1024:4d} KB")


# ---------------------------------------------------------------- about
def about():
    rows = [
        ("name", "Madhur Mittal, differentiatorX"),
        ("studying", "B.Tech Mathematics and Computing, DTU, class of 2029"),
        ("builds", "full-stack apps, real-time systems, payments, AI tooling"),
        ("now", "Echo, an open-source clipper that coding agents drive"),
        ("shipped", "Onyx, Echo, MERN Chat, CodeSync"),
        ("off-screen", "photography, @madhurdrishti"),
        ("known issue", 'says "quick fix", returns four hours later'),
        ("policy", "if it can fail, it gets a test"),
    ]
    h = 440
    body = [text(48, 70, "~ $ whoami", "m acc", 16, ' font-weight="500"')]
    for i, (k, v) in enumerate(rows):
        y = 118 + i * 37
        d = .25 + i * .12
        body.append(f'<g class="up" style="animation-delay:{d:.2f}s">{text(48, y, k, "m", 15)}{text(200, y, v, "b ink" if i == 0 else "b", 19)}</g>')
    body.append(f'<rect class="caret" x="48" y="{118 + 8 * 37 - 14}" width="9" height="18" fill="{ACC}"/>')
    img = b64("render/faceon.webp")
    body.append(
        '<defs><clipPath id="hole"><circle cx="1030" cy="210" r="170"/></clipPath>'
        '<radialGradient id="edge" cx=".5" cy=".5" r=".5"><stop offset=".72" stop-color="#060607" stop-opacity="0"/><stop offset="1" stop-color="#060607"/></radialGradient></defs>'
        f'<g clip-path="url(#hole)"><g class="spin"><image href="data:image/webp;base64,{img}" x="860" y="40" width="340" height="340"/></g>'
        '<circle cx="1030" cy="210" r="170" fill="url(#edge)"/></g>'
    )
    body.append(text(1030, 412, "face-on view, rendered. rotation period: about a minute", "m", 12.5, ' text-anchor="middle"'))
    css = (".caret{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
           ".spin{transform-origin:1030px 210px;animation:spin 60s linear infinite}@keyframes spin{to{transform:rotate(-360deg)}}")
    write("about.svg", svg(h, "".join(body), "whoami: " + "; ".join(f"{k}: {v}" for k, v in rows), css, seed=2))


# ---------------------------------------------------------------- section headers
def header(name, title, sub, seed):
    h = 150
    body = (
        '<g transform="translate(66 75)"><circle r="22" fill="none" stroke="rgba(236,238,240,.18)"/>'
        f'<circle r="5" fill="#000" stroke="{ACC}" stroke-width="1.2"/>'
        f'<g class="orb"><circle cx="22" r="3" fill="{ACC}"/></g></g>'
        + text(112, 82, title, "h", 40)
        + text(112, 112, sub, "m", 14)
    )
    css = ".orb{animation:orb 3.2s linear infinite}@keyframes orb{to{transform:rotate(360deg)}}"
    write(name, svg(h, body, f"{title}. {sub}", css, seed=seed, nstars=40))


# ---------------------------------------------------------------- pulls
def pulls():
    h = 400
    cols = [
        ("Full-stack", "MERN, Next.js 14 and FastAPI, from schema to pixels. Four apps shipped end to end.", 34),
        ("Real-time", "Socket.io presence, live video rooms, and queues that retry until the message lands.", 24),
        ("Payments", "Idempotency keys, double-entry ledgers, an outbox and signed webhooks. 46 tests on the money.", 44),
        ("AI tooling", "MCP servers, Whisper and FFmpeg pipelines, and agents that pick and cut video on their own.", 54),
        ("Graphics & maths", "GLSL ray tracing. The header above integrates light through curved spacetime.", 40),
    ]
    body = [text(48, 70, "What I build, end to end", "h", 40),
            text(48, 100, "five orbits, periods to Kepler's law. each one has broken at least once, under supervision.", "m", 14)]
    css = []
    for i, (t, d, r) in enumerate(cols):
        x = 48 + i * 238
        cx, cy = x + 58, 180
        period = 2.4 * (r / 24) ** 1.5
        body.append(f'<g transform="translate({cx} {cy})"><circle r="{r}" fill="none" stroke="rgba(236,238,240,.14)"/>'
                    f'<circle r="6" fill="#000" stroke="{ACC}" stroke-width="1.2"/>'
                    f'<g class="o{i}"><circle cx="{r}" r="3.5" fill="{ACC}"/></g></g>')
        body.append(text(x + 126, cy - 6, f"r = {r / 12:.1f}", "m", 12.5))
        body.append(text(x + 126, cy + 14, f"T = {period:.1f} s", "m", 12.5))
        body.append(text(x, 270, t, "b ink", 23, FW650))
        for j, line in enumerate(wrap(d, 25)):
            body.append(text(x, 300 + j * 23, line, "b", 16.5))
        css.append(f".o{i}{{animation:orb {period:.2f}s linear infinite}}")
    css.append("@keyframes orb{to{transform:rotate(360deg)}}")
    write("pulls.svg", svg(h, "".join(body), "What I build, end to end: " + "; ".join(f"{c[0]}: {c[1]}" for c in cols), "".join(css), seed=3))


# ---------------------------------------------------------------- real project marks (52 x 52)
IG_PATH = "M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"
GH_PATH = "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
LOGOS = {
    # Echo's own logo (echo/docs/logo.svg); one ring keeps rippling out
    "echo": ('<g transform="scale(.8125)"><circle cx="32" cy="32" r="30.5" fill="#0b0b0b" stroke="#f4f3ef" stroke-opacity=".16"/>'
             '<circle cx="32" cy="32" r="22" fill="none" stroke="#f4f3ef" stroke-opacity=".22" stroke-width="1.5"/>'
             '<circle cx="32" cy="32" r="15" fill="none" stroke="#f4f3ef" stroke-opacity=".45" stroke-width="1.5"/>'
             '<circle class="rip" cx="32" cy="32" r="15" fill="none" stroke="#ff4f3a" stroke-width="1.5"/>'
             '<path d="M28 24.5v15l12-7.5z" fill="#ff4f3a"/></g>',
             ".rip{transform-box:fill-box;transform-origin:center;animation:rip 2.4s cubic-bezier(.22,1,.36,1) infinite}"
             "@keyframes rip{from{transform:scale(1);opacity:.9}to{transform:scale(2);opacity:0}}"),
    # Onyx's mark (onyx/docs/brand/onyx-mark.svg)
    "onyx": ('<defs><linearGradient id="og" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#9aa0a6"/></linearGradient></defs>'
             '<g transform="scale(1.857)"><rect width="28" height="28" rx="7" fill="url(#og)"/><rect x="7" y="9.5" width="14" height="3" rx="1.5" fill="#07080a"/>'
             '<rect x="7" y="15.5" width="14" height="3" rx="1.5" fill="#07080a"/></g>', ""),
    # MERN Chat has no logo in its repo; this mark uses its README colours
    "chat": ('<defs><linearGradient id="cg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0EA5E9"/><stop offset="1" stop-color="#6366F1"/></linearGradient></defs>'
             '<rect width="52" height="52" rx="13" fill="url(#cg)"/>'
             '<path d="M14 16h24a4 4 0 0 1 4 4v12a4 4 0 0 1-4 4H24l-7 6v-6h-3a4 4 0 0 1-4-4V20a4 4 0 0 1 4-4z" fill="#fff"/>'
             '<circle cx="19" cy="26" r="2.2" fill="#6366F1"/><circle cx="26" cy="26" r="2.2" fill="#6366F1"/><circle cx="33" cy="26" r="2.2" fill="#6366F1"/>', ""),
    # CodeSync's navbar mark: lucide "code" in emerald-500
    "codesync": ('<rect width="52" height="52" rx="13" fill="#0b0c0e" stroke="rgba(16,185,129,.45)"/>'
                 '<g transform="translate(6 6) scale(1.667)" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                 '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></g>', ""),
    "photo": ('<defs><radialGradient id="ig" cx=".3" cy="1.07" r="1.3"><stop offset="0" stop-color="#feda75"/><stop offset=".25" stop-color="#fa7e1e"/>'
              '<stop offset=".5" stop-color="#d62976"/><stop offset=".75" stop-color="#962fbf"/><stop offset="1" stop-color="#4f5bd5"/></radialGradient></defs>'
              '<rect width="52" height="52" rx="13" fill="url(#ig)"/><g transform="translate(12 12) scale(1.1667)"><path d="' + IG_PATH + '" fill="#fff"/></g>', ""),
    "more": ('<rect width="52" height="52" rx="13" fill="#0b0c0e" stroke="rgba(236,238,240,.18)"/>'
             '<g transform="translate(12 12) scale(1.1667)"><path d="' + GH_PATH + '" fill="#eceef0"/></g>', ""),
}

# ---------------------------------------------------------------- project cards
def card(name, title, tagline, desc, tags, visual, css, label, seed, logo=None):
    h = 300
    body = [f'<g transform="translate(32 32)"><rect width="400" height="236" rx="14" fill="#0b0c0e" stroke="rgba(236,238,240,.08)"/>{visual}</g>']
    mark, mcss = LOGOS[logo] if logo else ("", "")
    if mark:
        body.append(f'<g transform="translate(480 50)">{mark}</g>')
    body.append(text(548 if mark else 480, 92, title, "h", 46))
    css += mcss
    body.append(text(480, 128, tagline, "b ink", 21, ' font-weight="500"'))
    for j, line in enumerate(wrap(desc, 74)):
        body.append(text(480, 168 + j * 26, line, "b", 18))
    x = 480
    for t in tags:
        w = 18 + len(t) * 7.9
        body.append(f'<rect x="{x}" y="244" width="{w:.0f}" height="28" rx="14" fill="none" stroke="rgba(236,238,240,.16)"/>'
                    + text(x + 9, 263, t, "m", 13))
        x += w + 8
    write(name, svg(h, "".join(body), label, css, seed=seed, nstars=45))


def echo_visual():
    rnd = random.Random(7)
    bars, hl = [], [(8, 16, "0:42"), (29, 36, "18:07"), (49, 57, "51:30")]
    css = [".pl{animation:pl 7s linear infinite}@keyframes pl{from{transform:translateX(0)}to{transform:translateX(352px)}}"]
    for i in range(64):
        env = .35 + .65 * abs(math.sin(i * .37) * math.cos(i * .11)) * rnd.uniform(.5, 1)
        hgt = 12 + 70 * env
        hi = next((k for k, (a, b, _) in enumerate(hl) if a <= i <= b), None)
        cls = f' class="hb{hi}"' if hi is not None else ""
        bars.append(f'<rect{cls} x="{24 + i * 5.5:.1f}" y="{136 - hgt / 2:.1f}" width="3.2" height="{hgt:.1f}" rx="1.6" fill="#3a3d43"/>')
    wins = []
    for k, (a, b, t) in enumerate(hl):
        x0, x1 = 24 + a * 5.5 - 4, 24 + b * 5.5 + 7
        wins.append(f'<g class="w{k}"><rect x="{x0:.1f}" y="80" width="{x1 - x0:.1f}" height="112" rx="6" fill="{ACC}" fill-opacity=".10" stroke="{ACC}" stroke-opacity=".6"/>'
                    + text((x0 + x1) / 2, 212, t, "m acc", 12, ' text-anchor="middle"') + "</g>")
        start = 1.0 + k * 1.3
        css.append(f".w{k},.hb{k}{{animation:win{k} 7s ease infinite}}"
                   f"@keyframes win{k}{{0%,{start / 7 * 100:.1f}%{{opacity:0}}{(start + .4) / 7 * 100:.1f}%,88%{{opacity:1}}96%,100%{{opacity:0}}}}")
        css.append(f".hb{k}{{fill:{ACC}}}")
    vis = (text(24, 40, "1h 04m in", "m ink", 13) + text(376, 40, "3 reels out", "m acc", 13, ' text-anchor="end"')
           + "".join(bars) + "".join(wins)
           + f'<g class="pl"><line x1="22" y1="70" x2="22" y2="200" stroke="{INK}" stroke-opacity=".7"/></g>')
    css.append(".w0,.w1,.w2,.hb0,.hb1,.hb2,.pl{animation-delay:-4.6s}")
    return vis, "".join(css)


def onyx_visual():
    rows = [("Due from provider", "4,590.00", ""), ("Owed to merchant", "", "4,498.20"), ("Fee revenue", "", "91.80")]
    out = [text(24, 40, "je_01  payment.captured", "m acc", 12.5), text(266, 66, "debit", "m", 11.5, ' text-anchor="end"'), text(376, 66, "credit", "m", 11.5, ' text-anchor="end"'),
           '<line x1="24" y1="78" x2="376" y2="78" stroke="rgba(236,238,240,.1)"/>']
    css = []
    for i, (a, d, c) in enumerate(rows):
        y = 108 + i * 30
        out.append(f'<g class="r{i}">{text(24 if not c else 40, y, a, "b ink" if not c else "b", 15.5)}'
                   f'{text(266, y, d, "m ink", 14, END)}{text(376, y, c, "m ink", 14, END)}</g>')
        css.append(f".r{i}{{animation:row 7s ease infinite;animation-delay:0s}}"
                   f".r{i}{{animation-name:r{i}}}@keyframes r{i}{{0%,{(0.3 + i * .5) / 7 * 100:.1f}%{{opacity:0;transform:translateY(6px)}}{(0.8 + i * .5) / 7 * 100:.1f}%,88%{{opacity:1;transform:none}}96%,100%{{opacity:0}}}}")
    out.append('<g class="tot"><line x1="24" y1="186" x2="376" y2="186" stroke="rgba(236,238,240,.1)"/>'
               + text(24, 212, "Totals", "b ink", 15.5, ' font-weight="650"')
               + text(266, 212, "4,590.00", "m ink", 14.5, ' text-anchor="end" font-weight="500"')
               + text(376, 212, "4,590.00", "m ink", 14.5, ' text-anchor="end" font-weight="500"') + "</g>")
    out.append(f'<g class="dr"><line x1="196" y1="220" x2="266" y2="220" stroke="{ACC}"/><line x1="196" y1="224" x2="266" y2="224" stroke="{ACC}"/>'
               f'<line x1="306" y1="220" x2="376" y2="220" stroke="{ACC}"/><line x1="306" y1="224" x2="376" y2="224" stroke="{ACC}"/></g>')
    out.append(f'<g class="ok">{text(376, 40, "balanced " + CHK, "m acc", 12.5, END)}</g>')
    css.append(".tot{animation:tot 7s ease infinite}@keyframes tot{0%,25%{opacity:0}32%,88%{opacity:1}96%,100%{opacity:0}}"
               ".dr{transform-origin:376px 222px;animation:dr 7s cubic-bezier(.22,1,.36,1) infinite}@keyframes dr{0%,33%{transform:scaleX(0)}42%,88%{transform:scaleX(1);opacity:1}96%,100%{opacity:0}}"
               ".ok{animation:okk 7s ease infinite}@keyframes okk{0%,42%{opacity:0}48%,88%{opacity:1}96%,100%{opacity:0}}"
               ".r0,.r1,.r2,.tot,.dr,.ok{animation-delay:-4.2s}")
    return "".join(out), "".join(css)


def chat_visual():
    msgs = [("l", "deployed?", 0.4), ("r", "deployed.", 1.6), ("l", "to prod?", 2.9)]
    out = [f'<circle cx="40" cy="118" r="18" fill="#15171b" stroke="rgba(236,238,240,.18)"/>{text(40, 123, "A", "m ink", 13, MID)}',
           f'<circle cx="360" cy="118" r="18" fill="#15171b" stroke="rgba(236,238,240,.18)"/>{text(360, 123, "B", "m ink", 13, MID)}',
           f'<circle class="pres" cx="373" cy="104" r="4.5" fill="{ACC}"/>',
           text(24, 40, "socket.io · 2 online", "m", 12.5)]
    css = [".pres{animation:pres 2s ease-in-out infinite}@keyframes pres{50%{opacity:.35}}"]
    for i, (side, m, t) in enumerate(msgs):
        y = 66 + i * 46
        w = 22 + len(m) * 8.6
        x = 70 if side == "l" else 330 - w
        out.append(f'<g class="m{i}"><rect x="{x}" y="{y}" width="{w:.0f}" height="32" rx="14" fill="{"#1a1c21" if side == "l" else ACC}" fill-opacity="{1 if side == "l" else .16}" stroke="{"rgba(236,238,240,.12)" if side == "l" else ACC}" stroke-opacity="{1 if side == "l" else .5}"/>'
                   + text(x + 11, y + 21, m, "b ink", 15) + "</g>")
        css.append(f".m{i}{{animation:m{i} 8s ease infinite}}@keyframes m{i}{{0%,{t / 8 * 100:.1f}%{{opacity:0;transform:translateY(6px)}}{(t + .35) / 8 * 100:.1f}%,90%{{opacity:1;transform:none}}97%,100%{{opacity:0}}}}")
    out.append('<g class="typ" transform="translate(286 204)"><rect width="44" height="24" rx="12" fill="#1a1c21" stroke="rgba(236,238,240,.12)"/>'
               + "".join(f'<circle class="d{k}" cx="{12 + k * 10}" cy="12" r="2.6" fill="{INK2}"/>' for k in range(3)) + "</g>")
    out.append(f'<circle r="3" fill="{ACC}"><animateMotion dur="8s" repeatCount="indefinite" begin="-5s" keyPoints="0;0;1;1" keyTimes="0;.05;.16;1" calcMode="linear" path="M58 112 Q200 40 342 112"/></circle>')
    css.append(".typ{animation:typ 8s ease infinite}@keyframes typ{0%,47%{opacity:0}52%,90%{opacity:1}97%,100%{opacity:0}}"
               + "".join(f".d{k}{{animation:dot 1.2s ease-in-out infinite;animation-delay:{k * .18:.2f}s}}" for k in range(3))
               + "@keyframes dot{40%{transform:translateY(-3px);opacity:1}0%,80%,100%{opacity:.35}}"
               + ".m0,.m1,.m2,.typ{animation-delay:-5s}")
    return "".join(out), "".join(css)


def codesync_visual():
    code = ["const seen = new Map()", "for (const [i, n] of a.entries()) {", "  if (seen.has(t - n))", "    return [seen.get(t - n), i]", "  seen.set(n, i)", "}"]
    out = ['<rect x="16" y="20" width="268" height="196" rx="10" fill="#0e0f12" stroke="rgba(236,238,240,.08)"/>']
    css = []
    for i, line in enumerate(code):
        y = 50 + i * 26
        w = len(line) * 6.65 + 4
        out.append(text(28, y, str(i + 1), "m", 11.5))
        out.append(f'<clipPath id="cl{i}"><rect class="c{i}" x="48" y="{y - 14}" width="{w:.0f}" height="20"/></clipPath>'
                   f'<g clip-path="url(#cl{i})">{text(48, y, line.replace(" ", NBSP), "m ink", 11)}</g>')
        t0, t1 = .3 + i * .7, .3 + i * .7 + .6
        css.append(f".c{i}{{transform-box:fill-box;transform-origin:left;animation:c{i} 7s steps(16) infinite}}"
                   f"@keyframes c{i}{{0%,{t0 / 7 * 100:.1f}%{{transform:scaleX(0)}}{t1 / 7 * 100:.1f}%,92%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}")
    for k, (y, who) in enumerate([(20, "you"), (120, "them")]):
        out.append(f'<g transform="translate(298 {y})"><rect width="86" height="94" rx="10" fill="#111317" stroke="rgba(236,238,240,.08)"/>'
                   f'<circle cx="43" cy="40" r="14" fill="#23262c"/><path d="M19 84 a24 18 0 0 1 48 0" fill="#23262c"/>'
                   f'<rect class="sp{k}" width="86" height="94" rx="10" fill="none" stroke="{ACC}" stroke-width="1.5"/>'
                   + text(8, 88, who, "m", 10.5) + "</g>")
        css.append(f".sp{k}{{animation:sp 3s ease-in-out infinite;animation-delay:{k * 1.5}s;opacity:0}}")
    css.append("@keyframes sp{0%,10%{opacity:0}20%,45%{opacity:1}55%,100%{opacity:0}}")
    out.append(text(16, 236 - 4, "\"and the complexity?\"  O(n).", "m", 11.5))
    css.append(",".join(f".c{i}" for i in range(6)) + "{animation-delay:-5s}")
    return "".join(out), "".join(css)


def photo_visual():
    cx, cy, R = 200, 112, 86
    blades = []
    for k in range(7):
        a = 2 * math.pi * k / 7
        x, y = math.cos(a) * 30, math.sin(a) * 30
        tx, ty = -math.sin(a), math.cos(a)
        blades.append(f'<line x1="{x - tx * 200:.1f}" y1="{y - ty * 200:.1f}" x2="{x + tx * 200:.1f}" y2="{y + ty * 200:.1f}" stroke="{INK2}" stroke-opacity=".55" stroke-width="1.2"/>')
    hept = " ".join(f"{math.cos(2 * math.pi * k / 7) * 30 / math.cos(math.pi / 7):.1f},{math.sin(2 * math.pi * k / 7 + math.pi / 7) * 0 + math.sin(2 * math.pi * k / 7) * 30 / math.cos(math.pi / 7):.1f}" for k in range(7))
    out = [f'<clipPath id="lens"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>',
           f'<circle cx="{cx}" cy="{cy}" r="{R + 10}" fill="#0e0f12" stroke="rgba(236,238,240,.16)"/>',
           f'<g clip-path="url(#lens)"><circle cx="{cx}" cy="{cy}" r="{R}" fill="#16181c"/>'
           f'<g transform="translate({cx} {cy})"><g class="iris"><polygon points="{hept}" fill="#000" transform="rotate({180 / 7:.2f})"/>{"".join(blades)}</g></g></g>',
           f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="rgba(236,238,240,.3)"/>',
           f'<g class="fa">{text(24, 40, "f/1.8 · 1/250 s · ISO 400", "m acc", 12.5)}</g>',
           f'<g class="fb">{text(24, 40, "f/8 · 1/30 s · ISO 400", "m ink", 12.5)}</g>',
           text(376, 222, "long exposures, mostly", "m", 11.5, ' text-anchor="end"')]
    css = (".iris{animation:iris 6s cubic-bezier(.65,0,.35,1) infinite}@keyframes iris{0%,100%{transform:scale(2.3) rotate(0deg)}45%,55%{transform:scale(.75) rotate(28deg)}}"
           ".fa{animation:fa 6s ease infinite}@keyframes fa{0%,22%,78%,100%{opacity:1}30%,70%{opacity:0}}"
           ".fb{animation:fb 6s ease infinite}@keyframes fb{0%,22%,78%,100%{opacity:0}30%,70%{opacity:1}}")
    return "".join(out), css


def more_visual():
    cx, cy = 200, 118
    out, css = [f'<g transform="translate({cx} {cy}) scale(1 .4)">'], []
    for i, r in enumerate([34, 52, 72, 96, 122]):
        period = 1.8 * (r / 34) ** 1.5
        out.append(f'<circle r="{r}" fill="none" stroke="rgba(236,238,240,.13)" stroke-width="2.4"/>'
                   f'<g class="p{i}" style="animation-delay:-{i * 1.7:.1f}s"><circle cx="{r}" r="{6.5 - i * .6:.1f}" fill="{ACC if i == 0 else INK2}"/></g>')
        css.append(f".p{i}{{animation:orb {period:.2f}s linear infinite}}")
    out.append(f'</g><circle cx="{cx}" cy="{cy}" r="11" fill="#000" stroke="{ACC}" stroke-width="1.2"/>')
    out.append(text(24, 40, "labs · coursework · in progress", "m", 12.5))
    css.append("@keyframes orb{to{transform:rotate(360deg)}}")
    return "".join(out), "".join(css)


def cards():
    v, c = echo_visual()
    card("card-echo.svg", "Echo", "Long video in, the few Reels worth posting out.",
         "Open-source AI clipper. Your coding agent picks the moments, YouTube's Most replayed data and timestamped comments confirm them, and your Instagram results tune the next pick. Runs locally.",
         ["Python", "FFmpeg", "Whisper", "MCP", "FastAPI"], v, c, "Echo: long video in, the few Reels worth posting out.", 11, "echo")
    v, c = onyx_visual()
    card("card-onyx.svg", "Onyx", "The payment gateway that keeps its books.",
         "A MERN payment gateway built for failure: idempotent APIs, a double-entry ledger, a transactional outbox, signed webhooks with retries and hourly reconciliation.",
         ["MERN", "Redis", "BullMQ", "Razorpay", "46 tests"], v, c, "Onyx: the payment gateway that keeps its books.", 12, "onyx")
    v, c = chat_visual()
    card("card-mern-chat.svg", "MERN Chat", "Real-time messaging.",
         "Socket.io chat with JWT cookie auth, live presence and instant delivery. React, Zustand and Tailwind on the front, Express and MongoDB behind.",
         ["Socket.io", "React", "Zustand", "JWT", "MongoDB"], v, c, "MERN Chat: real-time messaging.", 13, "chat")
    v, c = codesync_visual()
    card("card-codesync.svg", "CodeSync", "Interviews with video and code in one room.",
         "HD video calls beside a shared editor, with scheduling, live dashboards, ratings and recordings.",
         ["Next.js 14", "TypeScript", "Convex", "Clerk", "Stream"], v, c, "CodeSync: interviews with video and code in one room.", 14, "codesync")
    v, c = photo_visual()
    card("card-photo.svg", "Through the lens", "Photography by Madhur, @madhurdrishti.",
         "Light, night and everything in between. Same patience as debugging, better-looking results.",
         ["Photography", "Instagram"], v, c, "Through the lens: photography by Madhur, @madhurdrishti.", 15, "photo")
    v, c = more_visual()
    card("card-more.svg", "Everything else", "Labs, coursework, works in progress.",
         "Smaller orbits that are still moving. Some will reach escape velocity.",
         ["All repositories"], v, c, "Everything else: labs, coursework, works in progress.", 16, "more")


# ---------------------------------------------------------------- stack
def stack():
    h = 470
    groups = [("Languages", ["C++", "Python", "TypeScript", "JavaScript", "GLSL"]),
              ("Frontend", ["React", "Next.js 14", "Tailwind", "Zustand", "Vite"]),
              ("Backend", ["Node.js", "Express", "FastAPI", "Socket.io", "BullMQ"]),
              ("Data & infra", ["MongoDB", "Redis", "Convex", "Docker", "GitHub Actions"]),
              ("Auth & money", ["JWT", "Clerk", "Razorpay", "Zod", "Webhooks"]),
              ("Media, AI & GPU", ["FFmpeg", "Whisper", "MCP", "WebGL2", "pytest"])]
    body = [text(48, 70, "Instruments", "h", 40), text(48, 100, "everything here has shipped in a project above", "m", 14)]
    for i, (g, items) in enumerate(groups):
        x = 48 + i * 200
        body.append(text(x, 156, g, "m acc", 13.5, FW500))
        for j, it in enumerate(items):
            y = 176 + j * 52
            w = max(74, 40 + len(it) * 9.6)
            body.append(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="38" rx="10" fill="#0d0e11" stroke="rgba(236,238,240,.12)"/>'
                        f'<circle cx="{x + 16}" cy="{y + 19}" r="3" fill="{ACC}" fill-opacity=".8"/>' + text(x + 28, y + 25, it, "b ink", 16.5))
    write("stack.svg", svg(h, "".join(body), "Instruments: " + "; ".join(f"{g}: {', '.join(i)}" for g, i in groups), seed=4))


# ---------------------------------------------------------------- footer
def footer():
    h = 260
    body = (
        f'<g transform="translate(640 74)"><circle r="26" fill="#000" stroke="rgba(236,238,240,.18)"/><circle r="34" fill="none" stroke="{ACC}" stroke-opacity=".5"/>'
        f'<g class="orb"><circle cx="34" r="3.2" fill="{ACC}"/></g></g>'
        + text(640, 160, "Thanks for falling in.", "h", 44, ' text-anchor="middle"')
        + '<text class="m" x="640" y="196" font-size="14.5" text-anchor="middle">You&#8217;ve reached the bottom. Unlike light at 1.5 r'
        '<tspan font-size="10.5" dy="3">s</tspan><tspan dy="-3">, you can still scroll back up.</tspan></text>'
    )
    css = ".orb{animation:orb 2.6s linear infinite}@keyframes orb{to{transform:rotate(360deg)}}"
    write("footer.svg", svg(h, body, "Thanks for falling in.", css, seed=5))


if __name__ == "__main__":
    about()
    header("title-work.svg", "Things in orbit", "projects that survived contact with production", 21)
    pulls()
    cards()
    stack()
    footer()
