# build_site.py — cards + article styling, and CSS path fix
import os, glob, datetime, re

DOCS  = "docs"
POSTS = "content/posts"

STYLE = """
/* ===== Base (Medium-ish + pastel + dark) ===== */
*{box-sizing:border-box}
:root{
  --bg:#fafafa; --card:#fff; --text:#111; --muted:#666; --line:#e5e7eb; --brand:#0a58ca;
  --shadow:0 1px 3px rgba(0,0,0,.08);
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0e1116; --card:#151922; --text:#e9eef7; --muted:#9db0c9; --line:#263043; --brand:#8ab4ff;
    --shadow:0 1px 3px rgba(0,0,0,.35);
  }
}
html,body{height:100%}
body{
  font-family:system-ui,-apple-system,Segoe UI,Roboto,Apple SD Gothic Neo,Noto Sans KR,sans-serif;
  background:var(--bg); color:var(--text); line-height:1.75;
  max-width:960px; margin:28px auto; padding:0 16px;
}
header{margin:8px 0 18px}
header h1{margin:0;font-size:30px;font-weight:800;letter-spacing:-.2px}
header p{margin:4px 0 0;color:var(--muted);font-size:14px}
footer{opacity:.8;margin:28px 0 12px;text-align:center;font-size:13px}

/* chips / nav */
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 0}
.chip{font-size:12px;color:var(--brand);border:1px solid var(--brand);
  padding:2px 8px;border-radius:999px;background:transparent;opacity:.9}

/* ===== Cards (index) ===== */
ul.posts{list-style:none;padding:0;display:grid;grid-template-columns:1fr;gap:16px;margin:18px 0}
@media(min-width:760px){ul.posts{grid-template-columns:1fr 1fr}}
.card{
  border:1px solid var(--line); border-radius:16px; padding:18px; background:var(--card);
  box-shadow:var(--shadow); transition:transform .12s ease, border-color .12s ease;
}
.card:hover{ transform:translateY(-2px); border-color:rgba(10,88,202,.25) }
.card a.title{display:block;color:var(--brand);text-decoration:none;font-weight:800;font-size:18px;margin:2px 0 6px}
.card a.title:hover{text-decoration:underline}
.meta{font-size:12px;color:var(--muted);margin:0 0 8px;display:block}
.excerpt{font-size:15px;color:var(--text);margin:0}

/* ===== Article page ===== */
article{
  border:1px solid var(--line); border-radius:16px; padding:28px; background:var(--card);
  box-shadow:var(--shadow); margin:24px 0; line-height:1.8; font-size:16px;
}
article h1{font-size:26px;margin:0 0 12px;font-weight:800}
article h3{
  font-size:18px;margin:22px 0 8px;padding-left:10px;border-left:4px solid var(--brand);font-weight:700
}
/* styled lists */
article ul{padding-left:22px;margin-bottom:12px}
article ul li{margin:6px 0;list-style:none;position:relative}
article ul li::before{content:"✔";color:var(--brand);font-weight:bold;position:absolute;left:-18px}
article ol{padding-left:26px;margin-bottom:12px}
article ol li{margin:8px 0}
/* CTA box */
article hr{margin:24px 0;border:none;border-top:1px solid var(--line)}
article .cta{
  background:#f3f8ff;border:1px solid #d0e4ff;padding:14px;border-radius:12px;margin-top:18px
}
article .cta a{
  display:inline-block;margin-right:10px;padding:6px 14px;background:var(--brand);color:#fff;border-radius:8px;
  font-size:14px;text-decoration:none
}
article .cta a:hover{opacity:.9}
"""

HTML_LAYOUT = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="style.css?v=3">
<header>
  <h1>Auto Niche Site</h1>
  <p>{subtitle}</p>
</header>
<main>
{content}
</main>
<footer><small>© {year}</small></footer>
"""

def ensure_docs():
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "style.css"), "w", encoding="utf-8") as f:
        f.write(STYLE)

def extract_title_date_excerpt(path):
    title = os.path.basename(path); date = ""; excerpt = ""
    try:
        with open(path, encoding="utf-8") as f:
            html = f.read()
        m = re.search(r"<title>(.*?)</title>", html, re.I|re.S)
        if m: title = m.group(1).strip()
        base = os.path.basename(path)
        dm = re.match(r"(\\d{4}-\\d{2}-\\d{2})-", base)
        if dm: date = dm.group(1)
        text = re.sub(r"<[^>]+>", " ", html); text = re.sub(r"\\s+", " ", text).strip()
        excerpt = (text[:120] + "…") if len(text) > 120 else text
    except Exception:
        pass
    return title, date, excerpt

def main():
    ensure_docs()
    cards=[]
    for src in sorted(glob.glob(os.path.join(POSTS, "*.html")), reverse=True):
        name = os.path.basename(src)
        # read → fix css path → write to docs
        with open(src, encoding="utf-8") as f:
            html = f.read()
        # ❗ 포스트 내부의 ../style.css 를 style.css 로 치환 (복사 후 경로 맞추기)
        html = html.replace('href="../style.css?v=2"', 'href="style.css?v=3"') \
                   .replace('href="../style.css"', 'href="style.css?v=3"')
        with open(os.path.join(DOCS, name), "w", encoding="utf-8") as out:
            out.write(html)

        title, date, _ = extract_title_date_excerpt(src)
        cards.append(
            f'<li class="card"><a class="title" href="{name}">{title}</a>'
            + (f'<span class="meta">{date}</span>' if date else "")
            + "</li>"
        )

    grid = "<ul class='posts'>" + ("\n".join(cards) or "<li class='card'>첫 게시물을 준비 중…</li>") + "</ul>"
    index = HTML_LAYOUT.format(
        title="Home",
        subtitle="자동 발행 테스트 사이트",
        content=grid,
        year=datetime.date.today().year,
    )
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    print("OK: site built (cards + article styling + css fix)")

if __name__ == "__main__":
    main()
