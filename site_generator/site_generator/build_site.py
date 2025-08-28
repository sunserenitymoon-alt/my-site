# stdlib-only site builder
import os, glob, datetime, shutil

DOCS = "docs"
POSTS = "content/posts"

STYLE = "body{font-family:system-ui,sans-serif;max-width:840px;margin:24px auto;padding:0 12px;line-height:1.6}header,footer{opacity:.75}article{border:1px solid #eee;border-radius:12px;padding:16px;margin:18px 0}"

def ensure_docs():
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS,"style.css"),"w",encoding="utf-8") as f:
        f.write(STYLE)

LAYOUT = """<!doctype html><meta charset="utf-8">
<title>{title}</title><link rel="stylesheet" href="style.css">
<header><h1>Auto Niche Site</h1></header>
<main>{content}</main>
<footer><small>© {year}</small></footer>
"""

def main():
    ensure_docs()
    items=[]
    for p in sorted(glob.glob(os.path.join(POSTS,"*.html")), reverse=True):
        name = os.path.basename(p)
        dst = os.path.join(DOCS, name)
        shutil.copyfile(p, dst)
        with open(p,encoding="utf-8") as f:
            first_line = f.readline()
        items.append(f'<li><a href="{name}">{name}</a></li>')
    index = LAYOUT.format(title="Home", content="<h2>Latest</h2><ul>"+ "\n".join(items)+"</ul>", year=datetime.date.today().year)
    with open(os.path.join(DOCS,"index.html"),"w",encoding="utf-8") as f:
        f.write(index)
    print("OK: site built")

if __name__ == "__main__":
    main()
