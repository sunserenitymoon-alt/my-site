# stdlib-only site builder (pretty index)
import os, glob, datetime, shutil, re

DOCS = "docs"
POSTS = "content/posts"

STYLE = """
body{font-family:system-ui,sans-serif;max-width:900px;margin:24px auto;padding:0 12px;line-height:1.65}
header,footer{opacity:.75}
ul.posts{list-style:none;padding:0;display:grid;grid-template-columns:1fr;gap:14px}
@media(min-width:720px){ul.posts{grid-template-columns:1fr 1fr}}
.card{border:1px solid #eee;border-radius:14px;padding:14px}
.card a{font-weight:600;text-decoration:none}
small.meta{display:block;opacity:.7;margin-top:6px}
"""

def ensure_docs():
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS,"style.css"),"w",encoding="utf-8") as f:
        f.write(STYLE)

LAYOUT = """<!doctype html><meta charset="utf-8">
<title>{title}</title><link rel="stylesheet" href="style.css">
<header><h1>Auto Niche Site</h1><p>{subtitle}</p></header>
<main>{content}</main>
<footer><small>© {year}</small></footer>
"""

def extract_title_and_date(path):
    # <title>...</title> 에서 제목 추출
    title = os.path.basename(path)
    date = ""
    try:
        with open(path, encoding="utf-8") as f:
            html = f.read()
        m = re.search(r"<title>(.*?)</title>", html, re.I|re.S)
        if m: title = m.group(1).strip()
        # 파일명 앞의 YYYY-MM-DD- 패턴에서 날짜 추출
        base = os.path.basename(path)
        dm = re.match(r"(\d{4}-\d{2}-\d{2})-", base)
        if dm: date = dm.group(1)
    except Exception:
        pass
    return title, date

def main():
    ensure_docs()
    cards=[]
    for p in sorted(glob.glob(os.path.join(POSTS,"*.html")), reverse=True):
        name = os.path.basename(p)
        dst = os.path.join(DOCS, name)
        # 게시물 파일을 docs로 복사
        shutil.copyfile(p, dst)
        title, date = extract_title_and_date(p)
        cards.append(f'<li class="card"><a href="{name}">{title}</a>'
                     + (f'<small class="meta">{date}</small>' if date else "")
                     + '</li>')
    grid = "<ul class='posts'>" + ("\n".join(cards) or "<li>첫 게시물을 준비 중…</li>") + "</ul>"
    index = LAYOUT.format(
        title="Home",
        subtitle="자동 발행 테스트 사이트",
        content=grid,
        year=datetime.date.today().year
    )
    with open(os.path.join(DOCS,"index.html"),"w",encoding="utf-8") as f:
        f.write(index)
    print("OK: site built (pretty)")

if __name__ == "__main__":
    main()
