# stdlib-only post generator (EN) with AUTO-KEYWORD EXPANSION
# - If keywords.csv has too few rows, auto-creates 150+ English-friendly topics
# - No external packages / APIs (stable on GitHub Actions)

import os, csv, re, datetime, random

POSTS_DIR = "content/posts"
KEYWORDS  = "content/keywords/keywords.csv"
MIN_POOL  = 150    # ensure at least this many topics exist
DAILY_MAX = 8      # max posts per run

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\\s-]", "", s)
    s = re.sub(r"\\s+", "-", s).strip("-")
    return s[:70] or "post"

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
    with open(KEYWORDS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["keyword","subtopic","intent"])
        w.writeheader()
        for it in items:
            w.writerow(it)

def auto_expand(existing):
    """If too few topics, auto-generate a large English pool (student-friendly)."""
    if len(existing) >= MIN_POOL:
        return existing

    themes = [
        ("Study planner",            ["Weekly","Monthly","Daily","Exam week"],         "transactional"),
        ("Printable habit tracker",  ["Minimalist","A4","Black & white"],             "transactional"),
        ("Guided meditation script", ["Sleep","Focus","Anxiety relief"],              "informational"),
        ("Vocabulary flashcards",    ["Irregular verbs","Top 1000","Quiz sheet"],     "transactional"),
        ("Math formula cheatsheet",  ["Algebra","Geometry","Probability"],            "informational"),
        ("Science fair ideas",       ["Physics","Chemistry","Biology"],               "informational"),
        ("Time-block planner",       ["School days","Weekend","Exam prep"],           "transactional"),
        ("Reading log",              ["Monthly","Genre-based","Summary template"],    "transactional"),
        ("Pomodoro tracker",         ["12 rounds","Focus mode","Printable"],          "transactional"),
        ("Minecraft build ideas",    ["Starter base","Farm design","Redstone"],       "informational"),
        ("Pokemon card tips",        ["Sleeves/Binder","Deck list","Trading etiquette"], "informational"),
        ("Study routine checklist",  ["Morning","Night","Before exams"],              "transactional"),
    ]

    variants = [
        "Beginner guide to {kw}",
        "{kw} template",
        "{kw} PDF printable",
        "Quick start with {kw}",
        "{kw} checklist",
        "{kw} best practices",
        "One-page {kw}",
    ]
    suffixes = ["(printable)","(A4)","(Letter)","(minimal)"]

    seen = set((it["keyword"], it["subtopic"], it["intent"]) for it in existing)
    items = existing[:]

    def add(kw, sub, intent):
        key = (kw, sub, intent)
        if kw and key not in seen:
            items.append({"keyword": kw, "subtopic": sub, "intent": intent})
            seen.add(key)

    random.seed(101)
    for base_kw, subs, intent in themes:
        for sub in subs:
            add(base_kw, sub, intent)
            for v in random.sample(variants, k=min(4, len(variants))):
                add(v.format(kw=base_kw), sub, intent)
            for suf in random.sample(suffixes, k=2):
                add(f"{base_kw} {suf}", sub, intent)

    fillers = [
        "Exam revision timetable", "Note-taking tips", "Study motivation hacks",
        "Focus playlist ideas", "Weekly goals worksheet", "Daily reflection journal",
        "Mind map template", "Weekly review checklist", "Project planner for school",
    ]
    for f in fillers:
        add(f, "Student", "informational")
        add(f + " PDF", "Printable", "transactional")

    # ensure threshold
    if len(items) < MIN_POOL:
        for e in ["Study group rules", "Online class focus tips", "Weekly study audit"]:
            add(e, "Simple checklist", "informational")

    write_keywords(items)
    return items

# ---------- Text generation (EN) ----------
def make_intro(kw, sub, intent):
    base = f"Quick guide on “{kw}”."
    if sub: base += f" Focus: {sub}."
    tone = {
        "informational": "Key ideas summarized so you can apply them fast.",
        "transactional": "Includes ready-to-use templates and printables.",
        "navigational":  "Jump straight to what you need.",
    }.get(intent, "Just the essentials you need.")
    return base + " " + tone

def make_bullets(intent):
    libs = {
        "informational": [
            "Summarize the core idea in one sentence.",
            "Create one example and test yourself.",
            "Spend just 10 minutes to try a tiny experiment today.",
        ],
        "transactional": [
            "Download/print the template and use it right away.",
            "Run in 25-minute Pomodoro blocks and tick off items.",
            "Write a short reflection after you finish.",
        ],
    }
    return libs.get(intent, libs["informational"])[:3]

def mini_routine():
    return [
        "25-minute focus ▶ full attention",
        "5-minute break ▶ stretch & hydrate",
        "Write a 3-line summary ▶ tick your checklist",
    ]

def related_list():
    pool = [
        "Free study resources you can use today",
        "Build a 10-minute daily routine",
        "Exam-week focus tips",
        "Time management basics for students",
    ]
    random.shuffle(pool)
    return pool[:2]

def build_article_html(title, date, sub, intent, kw):
    bullets = make_bullets(intent)
    routine = mini_routine()
    rel     = related_list()
    return f"""<!doctype html><meta charset="utf-8">
<title>{title}</title><link rel="stylesheet" href="../style.css?v=4">
<article>
  <h1>{title}</h1>
  <p><small>{date} · tags: {intent}</small></p>

  <p>{make_intro(kw, sub, intent)}</p>

  <h3>Key takeaways</h3>
  <ul>
    <li>{bullets[0]}</li><li>{bullets[1]}</li><li>{bullets[2]}</li>
  </ul>

  <h3>Mini routine to try</h3>
  <ol>
    <li>{routine[0]}</li><li>{routine[1]}</li><li>{routine[2]}</li>
  </ol>

  <h3>Also useful</h3>
  <ul>
    <li>{rel[0]}</li><li>{rel[1]}</li>
  </ul>

  <div class="cta">
    <a href="https://serenimoon.gumroad.com/l/dceyg" target="_blank">Get the PDF planner</a>
    <a href="https://www.youtube.com/@yourchannel" target="_blank">Watch related videos</a>
  </div>
</article>
"""

# ---------- Main ----------
def main():
    ensure_dirs()
    kws = auto_expand(read_keywords())
    random.seed(datetime.date.today().toordinal())
    picks = random.sample(kws, k=min(DAILY_MAX, len(kws)))
    today = datetime.date.today().strftime("%Y-%m-%d")
    for it in picks:
        kw, sub, intent = it["keyword"], it["subtopic"], it["intent"]
        title = f"{kw} — {sub}" if sub else kw
        slug  = slugify(title)
        html  = build_article_html(title, today, sub, intent, kw)
        out   = os.path.join(POSTS_DIR, f"{today}-{slug}.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
    print(f"OK: posts generated (EN, auto keywords, {len(picks)} posts)")

if __name__ == "__main__":
    main()
