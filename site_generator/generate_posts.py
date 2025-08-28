# stdlib-only post generator with AUTO-KEYWORD EXPANSION
# - keywords.csv가 부족하면 자동으로 100~200개를 생성/추가
# - 외부 API/패키지 없음 (GitHub Actions에서 안정 동작)
import os, csv, re, datetime, random

POSTS_DIR = "content/posts"
KEYWORDS  = "content/keywords/keywords.csv"
MIN_POOL  = 120     # 부족하면 이 수량 이상이 되도록 자동 생성
DAILY_MAX = 10      # 하루에 최대 생성할 글 수

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9ㄱ-힣\\s-]', '', s)
    s = re.sub(r'\\s+', '-', s).strip('-')
    return s[:70] if s else "post"

def ensure_dirs():
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(KEYWORDS), exist_ok=True)

def read_keywords():
    items = []
    if os.path.exists(KEYWORDS):
        with open(KEYWORDS, encoding="utf-8") as f:
            r = csv.DictReader(f)
            for x in r:
                kw = (x.get("keyword") or "").strip()
                sub = (x.get("subtopic") or "").strip()
                intent = (x.get("intent") or "informational").strip().lower()
                if kw:
                    items.append({"keyword": kw, "subtopic": sub, "intent": intent})
    return items

def write_keywords(items):
    # header 보장 + UTF-8
    with open(KEYWORDS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["keyword","subtopic","intent"])
        w.writeheader()
        for it in items:
            w.writerow({"keyword": it["keyword"], "subtopic": it["subtopic"], "intent": it["intent"]})

def auto_expand(existing):
    """CSV가 부족하면 중학생 친화 주제를 자동 생성해서 추가"""
    if len(existing) >= MIN_POOL:
        return existing

    # ① 큰 테마(카테고리)
    themes = [
        ("시험 공부 플래너", ["중학생용","월간","주간","일일","기말/중간"], "transactional"),
        ("수학 공식 정리 프린트", ["중학 수학","도형/기하","확률과 통계","등식/부등식"], "informational"),
        ("영어 단어 암기표", ["주 100단어","불규칙동사","중학 필수","빈칸 채우기"], "transactional"),
        ("과학 실험 아이디어", ["화학","물리","생물","지구과학"], "informational"),
        ("국어 문법 요약", ["어종/어법","비문학 독해","문학 개념"], "informational"),
        ("마인크래프트 건축 아이디어", ["서바이벌","집/농장","레드스톤"], "informational"),
        ("포켓몬 카드 보관 팁", ["슬리브/바인더","덱 리스트","교환 매너"], "informational"),
        ("하루 10분 명상", ["집중력","긴장 완화","수면 전"], "informational"),
        ("공부 습관 체크리스트", ["모닝 루틴","야간 루틴","시험 주간"], "transactional"),
        ("타임블록 플래너", ["평일용","주말용","시험기간"], "transactional"),
        ("독서 기록장", ["월간","장르별","서평 템플릿"], "transactional"),
        ("코딩 기초 연습", ["파이썬 입문","알고리즘 맛보기","문제 풀이 루틴"], "informational"),
    ]

    # ② 변형 템플릿 (문구 조합용)
    variants = [
        "{kw} 템플릿", "초보용 {kw}", "{kw} PDF", "{kw} 가이드",
        "{kw} 체크리스트", "{kw} 베스트 팁", "{kw} 예시 모음",
        "빠르게 하는 {kw}", "한 장으로 끝내는 {kw}"
    ]
    sub_suffix = ["(출력용)", "(스마트폰용)", "(A4/흑백)", "(심플/미니멀)"]

    # 기존 중복 방지 셋
    seen = set((it["keyword"], it["subtopic"], it["intent"]) for it in existing)
    items = existing[:]

    def add(kw, sub, intent):
        key = (kw, sub, intent)
        if kw and key not in seen:
            items.append({"keyword": kw, "subtopic": sub, "intent": intent})
            seen.add(key)

    # ③ 조합으로 풍부하게 생성
    random.seed(42)  # 안정적 결과
    for base_kw, subs, intent in themes:
        for sub in subs:
            add(base_kw, sub, intent)
            # 변형 키워드 추가
            for v in random.sample(variants, k=min(4, len(variants))):
                add(v.format(kw=base_kw), sub, intent)
            # 서브토픽 꼬리표도 일부 랜덤 부착
            for suf in random.sample(sub_suffix, k=2):
                add(f"{base_kw} {suf}", sub, intent)

    # ④ 부족하면 보조 주제 랜덤 생성
    fillers = [
        "시험 전날 벼락치기 전략", "학습 계획표 작성법", "학교생활 시간관리",
        "시험기간 건강관리 팁", "필기 잘하는 법", "노트 정리 아이디어",
        "단권화 노하우", "과목별 오답노트 양식", "모의고사 활용법",
    ]
    for f in fillers:
        add(f, "중학생용", "informational")
        add(f + " PDF", "출력용", "transactional")

    # ⑤ 상한선까지 잘 채워졌는지 확인
    if len(items) < MIN_POOL:
        extra = ["스터디 그룹 규칙", "온라인 수업 집중 팁", "학습 계획 주간 점검"]
        for e in extra:
            add(e, "간단 체크리스트", "informational")

    write_keywords(items)
    return items

# ---------------- 본문 자동 작성 ----------------
def make_intro(kw, sub, intent):
    base = f"'{kw}' 주제를 간단히 정리합니다."
    if sub: base += f" (서브토픽: {sub})"
    tone = {
        "informational": "핵심을 이해하고 바로 써먹을 수 있게 요점만 담았어요.",
        "transactional": "바로 출력/활용 가능한 실전 자료도 함께 안내해요.",
    }.get(intent, "핵심만 빠르게 훑어봅시다.")
    return f"{base} {tone}"

def make_bullets(intent):
    libs = {
        "informational": [
            "핵심 개념을 한 문장으로 요약한다.",
            "예시 1개를 만들어 직접 적용해 본다.",
            "오늘 10분만 투자해 작은 실험을 한다.",
        ],
        "transactional": [
            "샘플/템플릿을 내려받아 바로 써본다.",
            "25분 타이머로 실행 → 체크리스트 표시.",
            "완료 후 짧게 회고를 남긴다.",
        ],
    }
    return libs.get(intent, libs["informational"])[:3]

def mini_routine():
    return [
        "타이머 25분 ▶ 집중",
        "5분 휴식 ▶ 스트레칭/물 마시기",
        "핵심 3줄 요약 ▶ 체크 표시",
    ]

def related_list():
    pool = [
        "무료로 바로 쓰는 학습 자료 모음",
        "하루 10분 루틴 만들기",
        "시험 주간 집중력 관리 팁",
        "중학생을 위한 시간관리 베이직",
    ]
    random.shuffle(pool)
    return pool[:2]

def build_article_html(title, date, sub, intent, kw):
    bullets = make_bullets(intent)
    routine = mini_routine()
    rel     = related_list()
    html = f"""<!doctype html><meta charset="utf-8">
<title>{title}</title><link rel="stylesheet" href="../style.css?v=2">
<article>
  <h1>{title}</h1>
  <p><small>{date} · tags: {intent}</small></p>

  <p>{make_intro(kw, sub, intent)}</p>

  <h3>빠른 요점</h3>
  <ul>
    <li>{bullets[0]}</li><li>{bullets[1]}</li><li>{bullets[2]}</li>
  </ul>

  <h3>바로 쓰는 미니 루틴</h3>
  <ol>
    <li>{routine[0]}</li><li>{routine[1]}</li><li>{routine[2]}</li>
  </ol>

  <h3>추가로 보면 좋은 것</h3>
  <ul>
    <li>{rel[0]}</li><li>{rel[1]}</li>
  </ul>

  <div class="cta">
    <a href="https://serenimoon.gumroad.com/l/dceyg" target="_blank">📘 PDF 플래너 받기</a>
    <a href="https://www.youtube.com/@yourchannel" target="_blank">▶️ 관련 영상 보기</a>
  </div>
</article>
"""
    return html

# ---------------- 메인 ----------------
def main():
    ensure_dirs()

    # 1) 키워드 읽기 & 자동 확장
    kws = read_keywords()
    kws = auto_expand(kws)  # 부족하면 자동 생성/추가

    # 2) 오늘 쓸 키워드 선택 (랜덤, 하루 최대 DAILY_MAX개)
    random.seed(datetime.date.today().toordinal())  # 날짜 기반 시드
    picks = random.sample(kws, k=min(DAILY_MAX, len(kws)))

    # 3) 글 생성
    today = datetime.date.today().strftime("%Y-%m-%d")
    for it in picks:
        kw   = it["keyword"]
        sub  = it["subtopic"]
        intent = it["intent"]
        title = f"{kw} — {sub}" if sub else kw
        slug  = slugify(title)
        html  = build_article_html(title, today, sub, intent, kw)
        out   = os.path.join(POSTS_DIR, f"{today}-{slug}.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)

    print(f"OK: posts generated (auto keywords, {len(picks)} posts)")

if __name__ == "__main__":
    main()
