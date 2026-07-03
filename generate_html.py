#!/usr/bin/env python3
"""Generate a single self-contained HTML study guide from markdown files."""

import markdown
import re
from pathlib import Path

DOCS_DIR = Path("docs")
OUTPUT = Path("docs/AD0-E724-Guia.html")

CHAPTER_ORDER = [
    ("README",      "Início"),
    ("pegadinhas",  "⚠️ Pegadinhas"),
    ("modulos",     "📦 Módulos & CLI"),
    ("di-plugins",  "🔌 DI & Plugins"),
    ("database",    "🗄️ DB & Cache"),
    ("stores",      "🏪 Stores"),
    ("produtos",    "📦 Produtos"),
    ("catalogo",    "🛍️ Catálogo & Sales"),
    ("frontend",    "🖥️ Frontend & Admin"),
    ("apis",        "🔗 APIs"),
    ("cloud",       "☁️ Cloud"),
]

MD_EXTENSIONS = ["extra", "fenced_code", "tables", "toc", "nl2br"]

def load_chapter(slug):
    path = DOCS_DIR / f"{slug}.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def convert(md_text):
    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    return md.convert(md_text)


def make_id(slug):
    return f"chapter-{slug}"


def build_toc(chapters):
    items = ""
    for slug, title in chapters:
        items += f'<li><a href="#{make_id(slug)}">{title}</a></li>\n'
    return items


def build_chapters(chapters):
    html = ""
    for slug, title in chapters:
        content = load_chapter(slug)
        if not content:
            continue
        body = convert(content)
        html += f"""
<section id="{make_id(slug)}" class="chapter">
  <div class="chapter-header">
    <h1 class="chapter-title">{title}</h1>
  </div>
  <div class="chapter-body">
    {body}
  </div>
</section>
"""
    return html


def main():
    toc = build_toc(CHAPTER_ORDER)
    chapters = build_chapters(CHAPTER_ORDER)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AD0-E724 — Guia de Estudos Adobe Commerce</title>
<style>
/* ─── Reset & base ─── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0f1117;--bg2:#1a1d27;--bg3:#242736;--bg4:#2e3145;
  --border:#3a3f5c;--text:#e2e4f0;--text2:#9ba3bf;
  --accent:#7c8fff;--accent2:#a78bfa;--green:#4ade80;--red:#f87171;
  --yellow:#fbbf24;--orange:#fb923c;
  --code-bg:#1e2130;--code-border:#313552;
  --font-sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --font-mono:'JetBrains Mono','Fira Code','Cascadia Code',Consolas,monospace;
  --radius:8px;--shadow:0 4px 20px rgba(0,0,0,.4);
}}
.light{{
  --bg:#f8f9fc;--bg2:#ffffff;--bg3:#f0f2f8;--bg4:#e4e7f0;
  --border:#d1d5e8;--text:#1a1d2e;--text2:#5a6080;
  --accent:#4f5bd5;--accent2:#7c3aed;
  --code-bg:#f3f4f9;--code-border:#d1d5e8;
  --shadow:0 4px 20px rgba(0,0,0,.08);
}}
html{{scroll-behavior:smooth}}
body{{
  font-family:var(--font-sans);background:var(--bg);color:var(--text);
  line-height:1.7;font-size:16px;
}}

/* ─── Layout ─── */
.app{{display:flex;min-height:100vh}}
.sidebar{{
  width:280px;flex-shrink:0;background:var(--bg2);border-right:1px solid var(--border);
  position:fixed;top:0;left:0;height:100vh;overflow-y:auto;z-index:100;
  transition:transform .3s ease;padding-bottom:2rem;
}}
.sidebar-header{{
  padding:1.25rem 1.5rem;border-bottom:1px solid var(--border);
  background:var(--bg3);position:sticky;top:0;z-index:1;
}}
.sidebar-title{{font-size:.75rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--text2)}}
.sidebar-subtitle{{font-size:.85rem;color:var(--accent);font-weight:600;margin-top:.2rem}}
nav ul{{list-style:none;padding:.5rem 0}}
nav ul li a{{
  display:block;padding:.55rem 1.5rem;color:var(--text2);text-decoration:none;
  font-size:.875rem;transition:all .15s;border-left:3px solid transparent;
}}
nav ul li a:hover{{color:var(--text);background:var(--bg3);border-left-color:var(--accent)}}
nav ul li a.active{{color:var(--accent);background:var(--bg3);border-left-color:var(--accent);font-weight:600}}

.main{{
  margin-left:280px;flex:1;padding:2rem;max-width:860px;
  transition:margin .3s ease;
}}

/* ─── Top bar ─── */
.topbar{{
  position:fixed;top:0;left:280px;right:0;height:52px;
  background:var(--bg2);border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  padding:0 2rem;z-index:99;transition:left .3s ease;
}}
.topbar-title{{font-size:.85rem;color:var(--text2);font-weight:500}}
.topbar-actions{{display:flex;gap:.75rem;align-items:center}}

.btn{{
  background:var(--bg3);border:1px solid var(--border);color:var(--text);
  padding:.35rem .75rem;border-radius:var(--radius);cursor:pointer;
  font-size:.8rem;font-family:var(--font-sans);transition:all .15s;
}}
.btn:hover{{background:var(--bg4);border-color:var(--accent);color:var(--accent)}}

.hamburger{{display:none;background:none;border:none;color:var(--text);cursor:pointer;font-size:1.25rem;padding:.25rem}}

.main-content{{padding-top:52px}}

/* ─── Chapters ─── */
.chapter{{margin-bottom:3rem;padding-bottom:3rem;border-bottom:1px solid var(--border)}}
.chapter:last-child{{border-bottom:none}}
.chapter-header{{
  background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);
  padding:1.25rem 1.5rem;margin-bottom:2rem;
  border-left:4px solid var(--accent);
}}
.chapter-title{{font-size:1.6rem;font-weight:700;color:var(--text)}}

/* ─── Typography ─── */
.chapter-body h1{{font-size:1.4rem;color:var(--accent);margin:2rem 0 .75rem;padding-bottom:.4rem;border-bottom:1px solid var(--border)}}
.chapter-body h2{{font-size:1.15rem;color:var(--accent2);margin:1.75rem 0 .6rem}}
.chapter-body h3{{font-size:1rem;color:var(--yellow);margin:1.5rem 0 .5rem}}
.chapter-body p{{margin:.6rem 0;color:var(--text)}}
.chapter-body a{{color:var(--accent);text-decoration:none}}
.chapter-body a:hover{{text-decoration:underline}}
.chapter-body strong{{color:var(--text);font-weight:700}}
.chapter-body em{{color:var(--text2)}}
.chapter-body ul,.chapter-body ol{{padding-left:1.5rem;margin:.6rem 0}}
.chapter-body li{{margin:.3rem 0}}
.chapter-body blockquote{{
  background:var(--bg3);border-left:4px solid var(--accent2);
  padding:.75rem 1rem;border-radius:0 var(--radius) var(--radius) 0;
  margin:1rem 0;color:var(--text2);
}}
.chapter-body blockquote p{{color:var(--text2)}}
.chapter-body blockquote strong{{color:var(--accent)}}
hr{{border:none;border-top:1px solid var(--border);margin:1.5rem 0}}

/* ─── Code ─── */
.chapter-body code{{
  background:var(--code-bg);border:1px solid var(--code-border);
  padding:.15em .4em;border-radius:4px;font-family:var(--font-mono);
  font-size:.85em;color:var(--accent2);
}}
.chapter-body pre{{
  background:var(--code-bg);border:1px solid var(--code-border);
  border-radius:var(--radius);padding:1.25rem;overflow-x:auto;
  margin:1rem 0;position:relative;
}}
.chapter-body pre code{{
  background:none;border:none;padding:0;color:#c9d1d9;font-size:.85rem;
  line-height:1.6;
}}

/* ─── Tables ─── */
.chapter-body table{{
  width:100%;border-collapse:collapse;margin:1rem 0;font-size:.875rem;
  display:block;overflow-x:auto;
}}
.chapter-body th{{
  background:var(--bg3);color:var(--accent);font-weight:700;
  padding:.6rem .9rem;text-align:left;border:1px solid var(--border);
}}
.chapter-body td{{
  padding:.55rem .9rem;border:1px solid var(--border);color:var(--text);
  vertical-align:top;
}}
.chapter-body tr:nth-child(even) td{{background:var(--bg3)}}
.chapter-body tr:hover td{{background:var(--bg4)}}
.chapter-body td del,.chapter-body th del{{color:var(--red);text-decoration:line-through}}

/* ─── Badges inline ─── */
.chapter-body td:first-child code{{color:var(--green)}}

/* ─── Scrollbar ─── */
::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:var(--bg2)}}
::-webkit-scrollbar-thumb{{background:var(--border);border-radius:3px}}
::-webkit-scrollbar-thumb:hover{{background:var(--accent)}}

/* ─── Sidebar overlay mobile ─── */
.sidebar-overlay{{
  display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:99;
}}

/* ─── Mobile ─── */
@media(max-width:768px){{
  .sidebar{{transform:translateX(-100%)}}
  .sidebar.open{{transform:translateX(0)}}
  .sidebar-overlay.open{{display:block}}
  .main{{margin-left:0;padding:1rem}}
  .topbar{{left:0}}
  .hamburger{{display:block}}
  .chapter-title{{font-size:1.25rem}}
  .chapter-body h1{{font-size:1.2rem}}
  .chapter-body h2{{font-size:1.05rem}}
  .chapter-body pre{{font-size:.78rem;padding:.9rem}}
  .chapter-body table{{font-size:.78rem}}
}}

/* ─── Print ─── */
@media print{{
  .sidebar,.topbar{{display:none}}
  .main{{margin:0;padding:1rem;max-width:100%}}
  .main-content{{padding-top:0}}
  .chapter{{break-inside:avoid}}
}}
</style>
</head>
<body>

<div class="sidebar-overlay" id="overlay" onclick="closeSidebar()"></div>

<aside class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <div class="sidebar-title">Adobe Commerce</div>
    <div class="sidebar-subtitle">AD0-E724 — Guia de Estudos</div>
  </div>
  <nav>
    <ul>
      {toc}
    </ul>
  </nav>
</aside>

<div class="topbar" id="topbar">
  <button class="hamburger" onclick="toggleSidebar()" aria-label="Menu">☰</button>
  <span class="topbar-title">AD0-E724 — Adobe Commerce Developer Professional</span>
  <div class="topbar-actions">
    <button class="btn" onclick="toggleTheme()" id="themeBtn">🌙 Dark</button>
  </div>
</div>

<main class="main" id="main">
  <div class="main-content">
    {chapters}
  </div>
</main>

<script>
// ─── Theme ───
const THEME_KEY = 'theme';
function applyTheme(t) {{
  document.body.classList.toggle('light', t === 'light');
  document.getElementById('themeBtn').textContent = t === 'light' ? '🌙 Dark' : '☀️ Light';
}}
function toggleTheme() {{
  const t = document.body.classList.contains('light') ? 'dark' : 'light';
  localStorage.setItem(THEME_KEY, t);
  applyTheme(t);
}}
applyTheme(localStorage.getItem(THEME_KEY) || 'dark');

// ─── Sidebar mobile ───
function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}}
function closeSidebar() {{
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
}}

// ─── Active nav link on scroll ───
const sections = document.querySelectorAll('.chapter');
const links = document.querySelectorAll('nav a');
const observer = new IntersectionObserver((entries) => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      const id = e.target.id;
      links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + id));
    }}
  }});
}}, {{rootMargin: '-10% 0px -80% 0px'}});
sections.forEach(s => observer.observe(s));

// ─── Close sidebar on nav click (mobile) ───
links.forEach(l => l.addEventListener('click', () => {{
  if (window.innerWidth <= 768) closeSidebar();
}}));
</script>
</body>
</html>"""

    OUTPUT.write_text(html, encoding="utf-8")
    size = OUTPUT.stat().st_size / 1024
    print(f"Generated: {OUTPUT} ({size:.1f} KB)")


if __name__ == "__main__":
    main()
