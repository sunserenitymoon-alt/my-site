import os, glob, datetime, shutil
DOCS="docs"; POSTS="content/posts"
STYLE="body{font-family:system-ui,sans-serif;max-width:840px;margin:24px auto;padding:0 12px;line-height:1.6}header,footer{opacity:.75}article{border:1px solid #eee;border-radius:12px;padding:16px;margin:18px 0}"
def ensure():
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS,"style.css"),"w",encoding="utf-8") as f: f.write(STYLE)
LAYOUT="""<!doctype html><meta charset="utf-8"><title>{title}</title><link rel="stylesheet" href="style.css"><header><h1>Auto Niche Site</h1></header><main>{content}</main><footer><small>© {y}</small></footer>"""
def main():
    ensure(); items=[]
    for p in sorted(glob.glob(os.path.join(POSTS,"*.html")), reverse=True):
        name=os.path.basename(p); shutil.copyfile(p, os.path.join(DOCS,name)); items.append(f'<li><a href="{name}">{name}</a></li>')
    index=LAYOUT.format(title="Home", content="<h2>Latest</h2><ul>"+("\n".join(items) or "<li>첫 게시물을 기다리는 중…</li>")+"</ul>", y=datetime.date.today().year)
    with open(os.path.join(DOCS,"index.html"),"w",encoding="utf-8") as f: f.write(index)
    print("OK: site built")
if __name__=="__main__": main()
