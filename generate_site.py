#!/usr/bin/env python3
"""Builds site/index.html from data/week-*.json files.

Usage:
    python generate_site.py

Add a new week by dropping a data/week-<N>-<YYYY>.json file (see existing
files for the shape) and re-running this script.
"""
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
SITE_DIR = ROOT / "docs"
FONT_DIR = ROOT / "assets" / "fonts"


def font_b64(name):
    return base64.b64encode((FONT_DIR / name).read_bytes()).decode("ascii")


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Monologue Ledger</title>
<style>
  @font-face {{
    font-family: 'Anton';
    src: url(data:font/woff2;base64,{anton_b64}) format('woff2');
    font-weight: 400; font-style: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'Courier Prime';
    src: url(data:font/woff2;base64,{courier_reg_b64}) format('woff2');
    font-weight: 400; font-style: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'Courier Prime';
    src: url(data:font/woff2;base64,{courier_bold_b64}) format('woff2');
    font-weight: 700; font-style: normal; font-display: swap;
  }}

  :root {{
    color-scheme: light dark;
    --bg: #efe9db;
    --fg: #201c16;
    --muted: #6b6255;
    --card: #fffdf8;
    --border: #ddd3bd;
    --accent: #c53324;
    --accent-soft: rgba(197, 51, 36, 0.08);
    --rule: #201c16;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #131110;
      --fg: #f2ecdf;
      --muted: #a89e8d;
      --card: #1d1a16;
      --border: #383129;
      --accent: #ff5b45;
      --accent-soft: rgba(255, 91, 69, 0.14);
      --rule: #f2ecdf;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #131110; --fg: #f2ecdf; --muted: #a89e8d; --card: #1d1a16;
    --border: #383129; --accent: #ff5b45; --accent-soft: rgba(255, 91, 69, 0.14); --rule: #f2ecdf;
  }}
  :root[data-theme="light"] {{
    --bg: #efe9db; --fg: #201c16; --muted: #6b6255; --card: #fffdf8;
    --border: #ddd3bd; --accent: #c53324; --accent-soft: rgba(197, 51, 36, 0.08); --rule: #201c16;
  }}

  * {{ box-sizing: border-box; }}
  html {{ overflow-x: hidden; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
  }}

  main {{ max-width: 700px; margin: 0 auto; padding: 3.5rem 1.25rem 6rem; }}

  header.masthead {{
    text-align: center;
    margin-bottom: 3rem;
  }}
  .on-air {{
    display: inline-flex; align-items: center; gap: 0.45rem;
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.14em;
    color: var(--muted); text-transform: uppercase;
    margin-bottom: 1.1rem;
  }}
  .on-air .dot {{
    width: 7px; height: 7px; border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 0 0 var(--accent-soft);
    animation: pulse 2.4s ease-in-out infinite;
  }}
  @media (prefers-reduced-motion: reduce) {{ .on-air .dot {{ animation: none; }} }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.35; }}
  }}
  h1.title {{
    font-family: 'Anton', sans-serif;
    font-weight: 400;
    font-size: clamp(2.2rem, 7vw, 3.4rem);
    letter-spacing: 0.01em;
    text-transform: uppercase;
    margin: 0 0 0.5rem;
    text-wrap: balance;
  }}
  p.deck {{
    color: var(--muted);
    font-size: 1rem;
    max-width: 46ch;
    margin: 0 auto;
  }}

  section.week {{ margin-bottom: 4rem; }}

  .marquee {{
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 1rem; flex-wrap: wrap;
    border-top: 3px solid var(--rule);
    border-bottom: 1px solid var(--border);
    padding: 0.6rem 0;
    margin-bottom: 1.4rem;
  }}
  .marquee .week-num {{
    font-family: 'Anton', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }}
  .marquee .week-num em {{
    font-style: normal;
    color: var(--accent);
  }}
  .marquee .range {{
    font-family: 'Courier Prime', monospace;
    font-size: 0.85rem;
    color: var(--muted);
  }}

  .note {{
    font-size: 0.88rem;
    color: var(--muted);
    border-left: 2px solid var(--border);
    padding-left: 0.9rem;
    margin-bottom: 1.8rem;
  }}

  .section-label {{
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--muted);
    margin: 0 0 0.9rem;
  }}

  .videos {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    gap: 1rem;
    margin-bottom: 2.2rem;
  }}
  .video-card {{
    display: block;
    color: inherit;
    text-decoration: none;
    border: 1px solid var(--border);
    background: var(--card);
    border-radius: 3px;
    overflow: hidden;
  }}
  .video-card .thumb {{
    position: relative;
    aspect-ratio: 16 / 9;
    background: var(--border);
    overflow: hidden;
  }}
  .video-card .thumb img {{
    width: 100%; height: 100%; object-fit: cover; display: block;
    filter: saturate(0.85) contrast(1.02);
    transition: filter 0.15s ease, transform 0.2s ease;
  }}
  .video-card:hover .thumb img {{ filter: saturate(1.05); transform: scale(1.03); }}
  .video-card .thumb::after {{
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(0deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 45%);
  }}
  .video-card .play {{
    position: absolute; left: 0.6rem; bottom: 0.5rem; z-index: 1;
    width: 0; height: 0;
    border-style: solid;
    border-width: 7px 0 7px 12px;
    border-color: transparent transparent transparent #fff;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.6));
  }}
  .video-card .vbody {{ padding: 0.6rem 0.75rem 0.8rem; }}
  .video-card .vhost {{
    font-family: 'Courier Prime', monospace;
    font-size: 0.68rem; color: var(--accent);
    text-transform: uppercase; letter-spacing: 0.06em;
    margin-bottom: 0.25rem;
  }}
  .video-card .vtitle {{
    font-size: 0.82rem; line-height: 1.32;
  }}

  .joke {{ margin-bottom: 1.75rem; }}
  .joke .byline {{
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--fg);
    margin-bottom: 0.3rem;
  }}
  .joke .byline .show {{ color: var(--muted); font-weight: 400; }}
  .joke .topic {{
    font-family: 'Courier Prime', monospace;
    font-size: 0.82rem;
    font-style: italic;
    color: var(--muted);
    margin-bottom: 0.45rem;
  }}
  .joke .topic::before {{ content: "INT. MONOLOGUE — "; opacity: 0.6; }}
  .joke .line {{
    font-family: 'Courier Prime', monospace;
    font-size: 1.02rem;
    line-height: 1.6;
    border-left: 3px solid var(--accent);
    padding: 0.15rem 0 0.15rem 1rem;
    margin: 0;
  }}
  .joke .context {{
    font-size: 0.82rem;
    color: var(--muted);
    margin-top: 0.4rem;
    padding-left: 1rem;
  }}

  .sources {{
    font-family: 'Courier Prime', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 1.6rem;
    word-break: break-all;
    line-height: 1.9;
  }}
  .sources a {{ color: inherit; }}

  footer {{
    text-align: center;
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 3.5rem;
  }}

  a {{ color: var(--accent); text-decoration-thickness: 1px; }}
</style>
</head>
<body>
<main>
  <header class="masthead">
    <div class="on-air"><span class="dot"></span>Updated manually, week by week</div>
    <h1 class="title">The Monologue Ledger</h1>
    <p class="deck">The sharpest lines from this week's late-night monologues — Kimmel, the Daily Show rotation, and whoever else was on the air.</p>
  </header>
  {weeks_html}
  <footer>Compiled from public monologue coverage &middot; regenerate with <code>python generate_site.py</code></footer>
</main>
</body>
</html>
"""

WEEK_TEMPLATE = """<section class="week">
  <div class="marquee">
    <span class="week-num">Week <em>{week}</em>, {year}</span>
    <span class="range">{date_range}</span>
  </div>
  {note_html}
  {videos_html}
  {jokes_html}
</section>"""

JOKE_TEMPLATE = """<div class="joke">
    <div class="byline">{host} <span class="show">&middot; {show}</span></div>
    {topic_html}
    <p class="line">&ldquo;{joke}&rdquo;</p>
    {context_html}
  </div>"""

VIDEO_TEMPLATE = """<a class="video-card" href="{url}" target="_blank" rel="noopener">
      <div class="thumb"><span class="play"></span><img src="{thumb}" alt="" loading="lazy"></div>
      <div class="vbody">
        <div class="vhost">{host}</div>
        <div class="vtitle">{title}</div>
      </div>
    </a>"""


def esc(s):
    return html.escape(s or "", quote=False)


def render_week(data):
    videos = data.get("videos") or []
    videos_html = ""
    if videos:
        cards = "\n    ".join(
            VIDEO_TEMPLATE.format(
                url=esc(v["url"]),
                thumb=f'https://i.ytimg.com/vi/{esc(v["id"])}/hqdefault.jpg',
                host=esc(v.get("host", "")),
                title=esc(v.get("title", "")),
            )
            for v in videos
        )
        videos_html = f'<div class="section-label">Watch This Week\'s Monologues</div>\n  <div class="videos">\n    {cards}\n  </div>'

    jokes_html = "\n  ".join(
        JOKE_TEMPLATE.format(
            host=esc(j.get("host", "")),
            show=esc(j.get("show", "")),
            topic_html=f'<div class="topic">{esc(j["topic"])}</div>' if j.get("topic") else "",
            joke=esc(j.get("joke", "")),
            context_html=f'<div class="context">{esc(j["context"])}</div>' if j.get("context") else "",
        )
        for j in data.get("jokes", [])
    )
    note_html = f'<div class="note">{esc(data["note"])}</div>' if data.get("note") else ""
    sources = data.get("sources") or []
    if sources:
        links = " &nbsp;/&nbsp; ".join(f'<a href="{esc(s)}">[{i + 1}]</a>' for i, s in enumerate(sources))
        jokes_html += f'\n  <div class="sources">Sources: {links}</div>'
    return WEEK_TEMPLATE.format(
        week=data["week"],
        year=data["year"],
        date_range=esc(data.get("date_range", "")),
        note_html=note_html,
        videos_html=videos_html,
        jokes_html=jokes_html,
    )


def main():
    week_files = sorted(DATA_DIR.glob("week-*.json"))
    weeks = [json.loads(f.read_text(encoding="utf-8")) for f in week_files]
    weeks.sort(key=lambda w: (w["year"], w["week"]), reverse=True)

    weeks_html = "\n  ".join(render_week(w) for w in weeks)

    SITE_DIR.mkdir(exist_ok=True)
    out_path = SITE_DIR / "index.html"
    out_path.write_text(
        PAGE_TEMPLATE.format(
            weeks_html=weeks_html,
            anton_b64=font_b64("anton-latin.woff2"),
            courier_reg_b64=font_b64("courierprime-reg.woff2"),
            courier_bold_b64=font_b64("courierprime-bold.woff2"),
        ),
        encoding="utf-8",
    )
    print(f"Wrote {out_path} ({len(weeks)} week(s))")


if __name__ == "__main__":
    main()
