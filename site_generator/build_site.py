# build_site.py — pretty card grid index (stdlib only)
import os, glob, datetime, shutil, re

DOCS  = "docs"
POSTS = "content/posts"

STYLE = """
/* --- Base (Medium-ish + pastel) --- */
*{box-sizing:border-box}
:root{
  --bg:#fafafa; --card:#fff; --text:#111; --muted:#666; --line:#eee; --brand:#0a58ca;
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

/* --- Chips (optional tag style) --- */
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 0}
.chip{font-size:12px;color:var(--brand);border:1px solid var(--brand);
  padding:2px 8px;border-radius:999px;background:transparent;opacity:.9}

/* --- Cards Grid --- */
ul.posts{list-style:none;padding:0;display:grid;grid-template-columns:1fr;gap:16px;margin:18px 0}
@media(min-width:760px){ul.posts{grid-template-columns:1fr 1fr}}

.card{
  border:1px solid var(--line); border-radius:16px; padding:18px; background:var(--card);
  box-shadow:var(--shadow); transition:transform .12s ease, box-shadow .12s ease, border-color .12s ease;
}
.card:hover{ transform:translateY(-2px); border-color:rgba(10,88,202,.25); }

.card a.title{
  display:block; color:var(--brand); text-decoration:none; font-weight:800; font-size:18px; margin:2px 0 6px;
}
.card a.title:hover{ text-decoration:underline }

.meta{font-size:12px;color:var(--muted);margin:0 0 8px;display:block}
.excerpt{font-size:15px;color:var(--text);margin:0}

/* --- Article page (copied posts) --- */
article{border:1px solid var(--line); border-radius:16px; padding:22px; background:var(--card); box-shadow:var(--shadow); margin:20px 0}
article h1{margin-top:0}
table{border-collapse:collapse;width:100%}
td,th{border:1px solid var(--line);padding:8px}
code,kbd{background:rgba(127,127,127,.12);padding:.15em .35em;border-radius:6px}
"""


HTML_LAYOUT = HTML_LAYOUT = """<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="style.css?v=2">
<header>
  <h1>Auto Niche Site</h1>
  <p>{subtitle}</p>
  <nav class="chips" style="margin-top:8px">
    <a class="chip" href="https://your-gumroad-or-payhip-link" target="_blank">PDF 다운로드</a>
    <a class="chip" href="www.youtube.com/@AcanthusH" target="_blank">YouTube</a>
  </nav>
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
    """제목, 날짜(파일명), 짧은 요약을 뽑아 카드에 표시"""
    title = os.path.basename(path)
    date  = ""
    excerpt = ""
    try:
        with open(path, encoding="utf-8") as f:
            html = f.read()

        # <title>..</title>에서 제목
        m = re.search(r"<title>(.*?)</title>", html, re.I|re.S)
        if m: title = m.group(1).strip()

        # 파일명 앞 YYYY-MM-DD- 패턴에서 날짜
        base = os.path.basename(path)
        dm = re.match(r"(\d{4}-\d{2}-\d{2})-", base)
        if dm: date = dm.group(1)

        # 태그 제거해서 첫 120자 발췌
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        excerpt = (text[:120] + "…") if len(text) > 120 else text
    except Exception:
        pass
    return title, date, excerpt

def main():
    ensure_docs()

    cards = []
    # 최신 글이 위로 오게 정렬
    for p in sorted(glob.glob(os.path.join(POSTS, "*.html")), reverse=True):
        name = os.path.basename(p)
        # 게시글 원본을 docs로 복사(페이지에서 열리도록)
        shutil.copyfile(p, os.path.join(DOCS, name))

        title, date, excerpt = extract_title_date_excerpt(p)
        meta = f'<span class="meta">{date}</span>' if date else ""
        ex   = f'<p class="excerpt">{excerpt}</p>' if excerpt else ""
        cards.append(
            f'<li class="card">'
            f'  <a class="title" href="{name}">{title}</a>'
            f'  {meta}'
            f'  {ex}'
            f'</li>'
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
    print("OK: site built (pretty cards)")

if __name__ == "__main__":
    main()
