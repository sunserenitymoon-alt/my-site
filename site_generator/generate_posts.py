import os, csv, re, datetime
POSTS_DIR="content/posts"; KEYWORDS="content/keywords/keywords.csv"
def slugify(s):
    s=s.lower(); s=re.sub(r'[^a-z0-9ㄱ-힣\\s-]','',s); s=re.sub(r'\\s+','-',s).strip('-'); return s[:60] or "post"
def ensure(): os.makedirs(POSTS_DIR, exist_ok=True)
def load():
    if not os.path.exists(KEYWORDS):
        return [("시험 공부 플래너","중학생용","informational"),
                ("수학 공식 정리 프린트","중학 수학","informational"),
                ("영어 단어 암기표","주 100단어","transactional")]
    out=[]; 
    with open(KEYWORDS, encoding="utf-8") as f:
        r=csv.DictReader(f)
        for x in r: out.append((x.get("keyword","").strip(), x.get("subtopic","").strip(), x.get("intent","informational").strip()))
    return out
POST_HTML = """<!doctype html><meta charset="utf-8">
<title>{title}</title><link rel="stylesheet" href="../style.css">
<article><h1>{title}</h1><p><small>{date} · tags: auto</small></p>
<ul><li>서브토픽: {sub}</li><li>의도: {intent}</li></ul>
<ol><li>핵심 한 줄</li><li>오늘 액션 1개</li><li>관련 자료 추후 추가</li></ol></article>"""
def main():
    ensure(); today=datetime.date.today().strftime("%Y-%m-%d")
    for kw,sub,intent in load()[:10]:
        title=f"{kw} — {sub}" if sub else kw
        slug=slugify(title)
        html=POST_HTML.format(title=title,date=today,sub=sub,intent=intent)
        with open(os.path.join(POSTS_DIR,f"{today}-{slug}.html"),"w",encoding="utf-8") as f: f.write(html)
    print("OK: posts generated")
if __name__=="__main__": main()
