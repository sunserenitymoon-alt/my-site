# build_site.py — Brand header/footer + nav + pretty cards + article CSS + css-path fix
import os, glob, datetime, re

DOCS  = "docs"
POSTS = "content/posts"

# --- Brand config (여기만 너 링크/이름으로 바꾸면 됨) ---
BRAND_NAME    = "Serenimoon Study Tools"
TAGLINE       = "Simple printables & routines for students"
GUMROAD_URL   = "https://serenimoon.gumroad.com/l/dceyg"
YOUTUBE_URL   = "https://www.youtube.com/@yourchannel"  # ← 네 채널로 바꿔

STYLE = """
/* ===== Base: brand look (light/dark) ===== */
*{box-sizing:border-box}
:root{
  --bg:#fbfbfe; --card:#fff; --text:#0e1320; --muted:#5f6b85; --line:#e6ebf5;
  --brand:#4f46e5; --brand-2:#7c3aed; --brand-3:#22d3ee;
  --shadow:0 6px 16px rgba(28,35,71,.06);
}
@media(prefers-color-scheme:dark){
  :root{
    --bg:#0e1116; --card:#151922; --text:#e9eef7; --muted:#9db0c9; --line:#263043;
    --brand:#8ab4ff; --brand-2:#a78bfa; --brand-3:#22d3ee;
    --shadow:0 6px 18px rgba(0,0,0,.35);
  }
}
html,body{height:100%}
body{
  font-family:system-ui,-apple-system,Segoe UI,Roboto,Apple SD Gothic Neo,Noto Sans KR,sans-serif;
  background:var(--bg); color:var(--text); line-height:1.75;
  max-width:1000px; margin:28px auto; padding:0 16px;
}

/* ===== Header / brand bar ===== */
.brand{
  border-radius:20px; padding:18px 18px 16px; margin:0 0 18px;
  background:linear-gradient(135deg,var(--card),rgba(127,127,255,.08));
  border:1px solid var(--line); box-shadow:var(--shadow);
}
.brand h1{margin:0; font-size:28px; font-weight:900; letter-spacing:-.2px}
.brand p{margin:4px 0 10px; color:var(--muted); font-size:14px}
.nav{display:flex; gap:10px; flex-wrap:wrap}
.btn{
  display:inline-flex; align-items:center; gap:8px;
  padding:8px 14px; border-radius:999px; font-size:13px;
  text-decoration:none; color:#fff; background:var(--brand);
  box-shadow:0 2px 8px rgba(79,70,229,.25)
}
.btn.alt{background:var(--brand-2)}
.btn:hover{opacity:.95}

/* ===== Cards (index) ===== */
ul.posts{list-style:none; padding:0; display:grid; grid-template-columns:1fr; gap:16px; margin:18px 0}
@media(min-width:760px){ul.posts{grid-template-columns:1fr 1fr}}

.card{
  position:relative; border:1px solid var(--line); border-radius:16px; padding:18px; background:var(--card);
  box-shadow:var(--shadow); transition:transform .12s ease, border-color .12s ease;
}
.card:hover{ transform:translateY(-2px); border-color:rgba(79,70,229,.35) }
.card a.title{display:block; color:var(--brand); text-decoration:none; font-weight:800; font-size:18px; margin:2px 0 6px}
.card a.title:hover{text-decoration:underline}
.meta{font-size:12px; color:var(--muted); margin:0 0 8px; display:block}

/* thumbnail badge */
.thumb{
  position:absolute; right:12px; top:12px; width:36px; height:36px; border-radius:50%;
  display:flex; align-items:center; justify-content:center; font-size:18px; color:#fff;
  background:linear-gradient(135deg,var(--brand-2),var(--brand-3));
  box-shadow:0 6px 14px rgba(0,0,0,.15)
}

/* ===== Article page ===== */
article{
  border:1px solid var(--line); border-radius:16px; padding:28px; background:var(--card);
  box-shadow:var(--shadow); margin:24px 0; line-height:1.85; font-size:16px;
}
article h1{font-size:26px; margin:0 0 12px; font-weight:900}
article h3{
  font-size:18px; margin:22px 0 8px; padding-left:10px; border-left:4px solid var(--brand); font-weight:700
}
article ul{padding-left:22px; margin-bottom:12px}
article ul li{margin:6px 0; list-style:none; position:relative}
article ul li::before{content:"✔"; color:var(--brand); font-weight:800; position:absolute; left:-18px}
article ol{padding-left:26px; margin-bottom:12px}
article ol li{margin:8px 0}
article hr{margin:24px 0; border:none; border-top:1px solid var(--line)}
.cta{
  background:#eef5ff20; border:1px solid var(--line); padding:14px; border-radius:12px; margin-top:18px
}
.cta a{
  display:inline-block; margin-right:10px; padding:8px 14px; background:var(--brand); color:#fff; border-radius:10px;
  font-size:14px; text-decoration:none
}
.cta a:hover{opacity:.92}

/* ===== Footer ===== */
footer{opacity:.85; margin:28px 0 12px; text-align:center; font-size:13px}
"""

HTML_LAYOUT = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="style.css?v=5">
<header class="brand">
  <h1>{brand}</h1>
  <p>{tagline}</p>
  <nav class="nav">
    <a class="btn" href="{gumroad}" target="_blank">📘 Get PDF</a>
    <a class="btn alt" href="{youtube}" target="_blank">▶️ YouTube</a>
  </nav>
</header>
<main>
{content}
</main>
<footer><small>© {year} · {brand}</small></footer>
"""

# 간단한 이모지 썸네일 매핑
ICON_MAP = [
    (r"planner|timetable|schedule|time\-?block", "🗂"),
    (r"habit|tracker|checklist", "✅"),
    (r"meditation|sleep|anxiety|focus", "🧘"),
    (r"math|algebra|geometry|probability|formula", "➗"),
    (r"vocab|vocabulary|flashcard|english", "🔤"),
    (r"reading|log|book", "📚"),
    (r"pomodoro", "⏱"),
    (r"minecraft|build|redstone|farm", "🧱"),
    (r"pokemon|card|deck", "🃏"),
]
def pick_icon(title:str)->str:
    t = title.lower()
    for pat, ico in ICON_MAP:
        if re.search(pat, t):
            return ico
    return "✨"

def ensure_docs():
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "style.css"), "w", encoding="utf-8") as f:
        f.write(STYLE)

def extract_title_date(path):
    title = os.path.basename(path); date = ""
    try:
        with open(path, encoding="utf-8") as f:
            html = f.read()
        m = re.search(r"<title>(.*?)</title>", html, re.I|re.S)
        if m: title = m.group(1).strip()
        base = os.path.basename(path)
        dm = re.match(r"(\\d{4}-\\d{2}-\\d{2})-", base)
        if dm: date = dm.group(1)
    except Exception:
        pass
    return title, date

def fix_css_path(html:str)->str:
    # ../style.css[?...] → style.css?v=5 로 통일
    return re.sub(r'href=["\'](\.\./)?style\.css(\?[^"\']*)?["\']', 'href="style.css?v=5"', html)

def main():
    ensure_docs()
    cards = []

    # 포스트 복사 + css 경로 치환
    for src in sorted(glob.glob(os.path.join(POSTS, "*.html")), reverse=True):
        with open(src, encoding="utf-8") as f:
            html = fix_css_path(f.read())
        name = os.path.basename(src)
        with open(os.path.join(DOCS, name), "w", encoding="utf-8") as out:
            out.write(html)

        title, date = extract_title_date(src)
        icon = pick_icon(title)
        cards.append(
            f'<li class="card">'
            f'  <div class="thumb">{icon}</div>'
            f'  <a class="title" href="{name}">{title}</a>'
            f'  <span class="meta">{date}</span>'
            f'</li>'
        )

    grid = "<ul class='posts'>" + ("\n".join(cards) or "<li class='card'>Getting things ready…</li>") + "</ul>"
    index = HTML_LAYOUT.format(
        title=BRAND_NAME,
        brand=BRAND_NAME,
        tagline=TAGLINE,
        gumroad=GUMROAD_URL,
        youtube=YOUTUBE_URL,
        content=grid,
        year=datetime.date.today().year,
    )
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    print("OK: site built (brand header/footer, nav, icons, css v5)")

if __name__ == "__main__":
    main()
