# stdlib-only post generator
import os, csv, re, datetime, pathlib

POSTS_DIR = "content/posts"
KEYWORDS = "content/keywords/keywords.csv"

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9ㄱ-힣\s-]', '', s)
    s = re.sub(r'\s+', '-', s).strip('-')
    return s[:60] if s else "post"

def ensure_dirs():
    os.makedirs(POSTS_DIR, exist_ok=True)

def load_keywords():
    if not os.path.exists(KEYWORDS):
        return [
            ("시험 공부 플래너", "중학생용", "informational"),
            ("수학 공식 정리 프린트", "중학 수학", "informational"),
            ("영어 단어 암기표", "주 100단어", "transactional"),
        ]
    out=[]
    with open(KEYWORDS, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            out.append((r.get("keyword","").strip(),
                        r.get("subtopic","").strip(),
                        r.get("intent","informational").strip()))
    return out

POST_HTML = """<!doctype html><meta charset="utf-8">
<title>{title}</title><link rel="stylesheet" href="../style.css">
<article><h1>{title}</h1>
<p><small>{date} · tags: {tags}</small></p>
<p>이 글은 자동으로 생성된 예시입니다. 주제: <b>{title}</b></p>
<ul>
  <li>서브토픽: {sub}</li>
  <li>의도: {intent}</li>
</ul>
<p>간단 체크리스트:
<ol>
  <li>핵심 개념 한 줄 요약</li>
  <li>오늘 적용할 액션 1개</li>
  <li>관련 자료 링크 추후 추가</li>
</ol>
</p>
</article>
"""

def main():
    ensure_dirs()
    today = datetime.date.today().strftime("%Y-%m-%d")
    for kw, sub, intent in load_keywords()[:10]:
        title = f"{kw} — {sub}" if sub else kw
        slug = slugify(title)
        html = POST_HTML.format(title=title, date=today, tags="auto", sub=sub, intent=intent)
        out = os.path.join(POSTS_DIR, f"{today}-{slug}.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
    print("OK: posts generated")

if __name__ == "__main__":
    main()
