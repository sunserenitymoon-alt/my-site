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
import random, textwrap

def make_intro(kw, sub, intent):
    pieces = []
    focus = f" Focus: {sub}." if sub else ""
    if intent == "transactional":
        pieces.append(f"Practical guide to “{kw}”.{focus} Grab-and-go tips plus a printable/ready-to-use asset.")
    else:
        pieces.append(f"Quick guide on “{kw}”.{focus} Key ideas in plain English so you can apply them fast.")
    pieces.append("You can finish this in ~10 minutes, then extend if you like.")
    return " ".join(pieces)

def make_value_list(kw, intent):
    base = [
        "A one-minute summary you can recall later",
        "A 3-step mini plan to get moving today",
        "A tiny checklist to tick as you go",
    ]
    if intent == "transactional":
        base.append("A printable/template link so you can use it right away")
    return base

def make_steps(kw):
    # generic + lightweight, works for any topic
    return [
        f"Define your goal for “{kw}” in one short sentence.",
        "Set a 25-minute timer and work only on this.",
        "Write a 3-line summary of what you did and what to do next.",
        "Save your notes (or printable) to a folder you can find again.",
        "Schedule the next 25-minute block on your calendar.",
    ]

def make_domain_example(kw, sub):
    t = (kw + " " + (sub or "")).lower()
    # very light heuristics to sound specific
    if "pokemon" in t or "card" in t:
        return ("Example: Use inner sleeves (62×89 mm) + outer sleeves (66×91 mm) "
                "and a 9-pocket binder. Keep binders vertical; target 45–55% humidity.")
    if "planner" in t or "time-block" in t:
        return ("Example: Time-block 25-min study + 5-min break ×4. "
                "Put math in the first block; languages after lunch when energy dips.")
    if "habit" in t:
        return ("Example: Pick one habit only (e.g., 10-minute reading). "
                "Track it Mon–Fri; mark ✅/❌; review every Sunday.")
    if "meditation" in t or "sleep" in t:
        return ("Example: 4-7-8 breathing for 3 rounds, then body scan from toes to head. "
                "Lights off, phone outside your room.")
    if "vocab" in t or "flashcard" in t:
        return ("Example: Make 10 cards: front = word + example gap; back = definition + full sentence. "
                "Quiz until you get 8/10 correct, then add 10 more tomorrow.")
    if "math" in t or "formula" in t:
        return ("Example: Copy 5 formulas on one page (area, perimeter, Pythagorean). "
                "Solve 3 quick problems; circle any step you hesitated on.")
    if "minecraft" in t:
        return ("Example: Starter base: 9×9 footprint, oak + cobblestone, chest/furnace/crafting triangle; "
                "torch the perimeter every 7 blocks.")
    return ("Example: Write a tiny scenario that uses today’s idea once. "
            "If it takes more than 10 minutes, cut the scope in half.")

def make_faq(kw):
    return [
        ("How long does this take?",
         "About 10–15 minutes for the quick version. You can repeat the mini-routine to go deeper."),
        ("What tools do I need?",
         "Just a timer and a notes app. If there’s a printable, you can use it on paper or as PDF.")
    ]

def build_article_html(title, date, sub, intent, kw):
    value = make_value_list(kw, intent)
    steps = make_steps(kw)
    ex    = make_domain_example(kw, sub)
    faq   = make_faq(kw)

    # tiny helper to list items as <li>
    def li_list(items): return "".join(f"<li>{x}</li>" for x in items)

    html = f"""<!doctype html><meta charset="utf-8">
<title>{title}</title><link rel="stylesheet" href="../style.css?v=6">
<article>
  <h1>{title}</h1>
  <p><small>{date} · tags: {intent}</small></p>

  <p>{make_intro(kw, sub, intent)}</p>

  <h3>What you’ll get</h3>
  <ul>{li_list(value)}</ul>

  <h3>Mini plan (3–5 steps)</h3>
  <ol>{li_list(steps)}</ol>

  <h3>Quick example</h3>
  <p>{ex}</p>

  <h3>Tiny checklist</h3>
  <ul>
    <li>Write 1-line goal</li>
    <li>Do one 25-minute block</li>
    <li>Capture 3-line summary</li>
  </ul>

  <div class="cta">
    <a href="https://serenimoon.gumroad.com/l/dceyg?utm_source=site&utm_medium=post&utm_campaign=cta&utm_content={kw.replace(' ','-')}" target="_blank">Get the PDF planner</a>
    <a href="https://www.youtube.com/@yourchannel" target="_blank">Watch related videos</a>
  </div>

  <h3>FAQ</h3>
  <p><strong>{faq[0][0]}</strong><br>{faq[0][1]}</p>
  <p><strong>{faq[1][0]}</strong><br>{faq[1][1]}</p>
</article>
"""
    return html


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
