import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "glossary.yaml"
OUT_PATH = ROOT / "site" / "glossary.html"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Trinity Draft - Glossary</title>
  <link rel="stylesheet" href="css/style.css">
  <style>
    .glossary-section { margin-bottom: 40px; }
    .glossary-section h2 { border-bottom: 2px solid #ceb352; padding-bottom: 5px; text-transform: capitalize; }
    .term-card { background: #fff; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
    .term-name { font-size: 1.2em; font-weight: bold; color: #333; margin-bottom: 5px; display: inline-block; }
    .term-badge { padding: 2px 6px; border-radius: 4px; color: #fff; font-size: 0.8em; margin-left: 10px; vertical-align: super;}
    .term-desc { margin-top: 10px; color: #555; line-height: 1.5; }
    .term-jp { color: #888; font-size: 0.9em; font-style: italic; }
  </style>
</head>
<body>
  <header class="navbar">
    <div class="logo">
      <span class="gold-text">TRINITY DRAFT</span> Glossary
    </div>
    <div class="header-links">
      <a href="index.html">Card Library</a>
      <a href="rulebook.html">Rulebook</a>
    </div>
  </header>

  <main class="container">
    <h1>Glossary & Terminology</h1>
    <p>This glossary defines the keywords, auras, zones, and standard terminology used across Trinity Draft.</p>

{content}
  </main>
</body>
</html>
"""

content_html = ""

for category, terms in data.items():
    if not terms:
        continue
    content_html += f"    <div class='glossary-section'>\n      <h2>{category}</h2>\n"
    for name, info in terms.items():
        if info is None:
            info = {}
        
        badge_html = ""
        if "color" in info:
            badge_html = f"<span class='term-badge' style='background-color: {info['color']};'>{info.get('type', 'Keyword').upper()}</span>"
            
        desc = info.get("desc", "")
        jp = info.get("jp", "")
        
        content_html += f"""      <div class='term-card'>
        <div class='term-name'>{name} {badge_html}</div>
        """
        if desc:
            content_html += f"<div class='term-desc'>{desc}</div>"
            
        content_html += "      </div>\n"
        
    content_html += "    </div>\n"

final_html = html_template.replace("{content}", content_html)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"Glossary page generated at {OUT_PATH}")
