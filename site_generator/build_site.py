# build_site.py — pretty card grid index (stdlib only)
import os, glob, datetime, shutil, re

DOCS  = "docs"
POSTS = "content/posts"

STYLE = """
/* base */
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Apple SD Gothic Neo,Noto Sans KR,sans-serif;
     max-width:980px;margin:28px auto;padding:0 14px;line-height:1.7;color:#111;background:#fafafa}
header{margin:10px 0 18px}
header h1{margin:0 0 4px;font-size:28px}
header p{margin:0;color:#666}
footer{opacity:.7;margin:24px 0 12px;text-align:center}

/* cards */
ul.posts{list-style:none;padding:0;display:grid;grid-template-columns:1fr;gap:14px;margin:18px 0}
@media(min-width:760px){ul.posts{grid-template-columns:1fr 1fr}}
.card{border:1px solid #eee;border-radius:14px;padding:16px;background:#fff;
      box-shadow:0 1px 3px rgba(0,0,0,.08);transition:transform .1s ease}
.card:hover{transform:translateY(-2px)}
.card a.title{display:block;font-weight:700;text-decoration:none;color:#0a58ca;margin-bottom:6px;font-size:17px}
.card a.title:hover{text-decoration:underline}
.meta{font-size:12px;color:#777;margin-bottom:8px;display:block}
.excerpt{font-size:14px;color:#333;margin:0}
"""

HTML_LAYOUT = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="style.css?v=2">
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
