# stdlib-only post generator (Korean blog-style auto content)
import os, csv, re, datetime, random

POSTS_DIR = "content/posts"
KEYWORDS  = "content/keywords/keywords.csv"

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9ㄱ-힣\\s-]', '', s)
    s = re.sub(r'\\s+', '-', s).strip('-')
    return s[:70] if s else "post"

def ensure_dirs():
    os.makedirs(POSTS_DIR, exist_ok=True)

def load_keywords():
    # CSV 없으면 샘플 6개
    if not os.path.exists(KEYWORDS):
        return [
            ("하루 10분 명상", "집중력", "informational"),
            ("영어 단어 암기표", "주 100단어", "transactional"),
            ("수학 공식 정리 프린트", "중학 수학", "informational"),
            ("시험 공부 플래너", "중학생용", "transactional"),
            ("마인크래프트 건축 아이디어", "초보 가이드", "informational"),
            ("포켓몬 카드 보관 팁", "슬리브/바인더", "informational"),
        ]
    out=[]
    with open(KEYWORDS, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            kw   = (r.get("keyword") or "").strip()
            sub  = (r.get("subtopic") or "").strip()
            intent = (r.get("intent") or "informational").strip().lower()
            if kw:
                out.append((kw, sub, intent))
    return out

# ---------- 텍스트 생성 로직 (간단 규칙) ----------
def make_intro(kw, sub, intent):
    base = f"'{kw}' 주제를 아주 간단히 정리해 드립니다."
    if sub: base += f" (서브토픽: {sub})"
    tone = {
        "informational": "핵심 개념을 이해하고 바로 써먹을 수 있게 정리했어요.",
        "transactional": "바로 써먹을 수 있는 자료/템플릿도 함께 안내합니다.",
        "navigational":  "필요한 자료로 빠르게 이동할 수 있게 요점만 모았습니다.",
    }.get(intent, "핵심만 빠르게 훑어봅시다.")
    return f"{base} {tone}"

def make_bullets(kw, intent):
    libs = {
        "informational": [
            "핵심 개념을 한 문장으로 요약해 보세요.",
            "예시 1개를 직접 만들어보면 기억에 오래 남습니다.",
            "오늘 10분만 투자해서 작은 실험을 해보세요.",
        ],
        "transactional": [
            "샘플/템플릿을 내려받아 바로 출력해 활용하세요.",
            "시간을 25분 단위(포모도로)로 끊어 실행하면 효율이 올라갑니다.",
            "완료 후 체크리스트로 진도를 표시하세요.",
        ],
    }
    # 의도에 맞는 3개 선택
    cands = libs.get(intent, libs["informational"])
    return cands[:3]

def mini_routine(kw):
    return [
        "타이머 25분 ▶ 집중",
        "5분 휴식 ▶ 스트레칭/물 마시기",
        "핵심 3줄 요약 ▶ 체크리스트 표시",
    ]

def related(kw):
    seeds = [
        "초보가 자주 막히는 포인트 3가지",
        "무료로 바로 쓸 수 있는 자료 모음",
        "하루 10분 루틴 만들기",
        "다음 단계: 중급자를 위한 확장 아이디어",
    ]
    random.shuffle(seeds)
    return seeds[:2]

def build_article_html(title, date, sub, intent, kw):
    bullets = make_bullets(kw, intent)
    routine = mini_routine(kw)
    rel     = related(kw)
    # 본문 작성
    html = f"""<!doctype html><meta charset="utf-8">
<title>{title}</title><link rel="stylesheet" href="../style.css?v=2">
<article>
  <h1>{title}</h1>
  <p><small>{date} · tags: {intent}</small></p>

  <p>{make_intro(kw, sub, intent)}</p>

  <h3>빠른 요점</h3>
  <ul>
    <li>{bullets[0]}</li>
    <li>{bullets[1]}</li>
    <li>{bullets[2]}</li>
  </ul>

  <h3>바로 쓰는 미니 루틴</h3>
  <ol>
    <li>{routine[0]}</li>
    <li>{routine[1]}</li>
    <li>{routine[2]}</li>
  </ol>

  <h3>추가로 보면 좋은 것</h3>
  <ul>
    <li>{rel[0]}</li>
    <li>{rel[1]}</li>
  </ul>

  <hr>
  <p><b>유용한 자료</b></p>
  <ul>
    <li><a href="https://serenimoon.gumroad.com/l/dceyg" target="_blank">PDF 플래너 바로 받기</a></li>
    <li><a href="https://www.youtube.com/@yourchannel" target="_blank">관련 영상 보기</a></li>
  </ul>
</article>
"""
    return html

# ---------- 메인 ----------
def main():
    ensure_dirs()
    today = datetime.date.today().strftime("%Y-%m-%d")
    for kw, sub, intent in load_keywords()[:20]:
        title = f"{kw} — {sub}" if sub else kw
        slug  = slugify(title)
        html  = build_article_html(title, today, sub, intent, kw)
        out   = os.path.join(POSTS_DIR, f"{today}-{slug}.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
    print("OK: posts generated (blog-style)")

if __name__ == "__main__":
    main()
