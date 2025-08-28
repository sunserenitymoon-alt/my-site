# build_site.py — pretty card grid index (stdlib only)
import os, glob, datetime, shutil, re

DOCS  = "docs"
POSTS = "content/posts"

STYLE = """
/* base */
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Apple SD Gothic Neo,Noto Sans KR,sans-serif;
     max-width:980px;margin:28px auto;padding:0 14px;line-height:1.7;color:#111}
header{margin:10px 0 18px}
header h1{margin:0 0 4px;font-size:28px}
header p{margin:0;color:#666}
footer{opacity:.7;margin:24px 0 12px}

/* cards */
ul.posts{list-style:none;padding:0;display:grid;grid-template-columns:1fr;gap:14px;margin:18px 0}
@media(min-width:760px){ul.posts{grid-template-columns:1fr 1fr}}
.card{border:1px solid #eee;border-radius:14px;padding:16px;background:#fff;
      box-shadow:0 1px 2px rgba(0,0,0,.04)}
.card a.title{display:block;font-weight:700;text-decoration:none;color:#0a58ca;margin-bottom:6px}
.card a.title:hover{text-decoration:underline}
.meta{font-size:12px;color:#777;margin-bottom:8px;display:block}
.excerpt{font-size:14px;color:#333;margin:0}
"""

HTML_LAYOUT = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
<header>
  <h1>Auto Niche Site</h1>
  <p>{subtitle}</p>
</header>
<main>
{conten
