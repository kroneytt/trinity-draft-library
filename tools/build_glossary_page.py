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
    .glossary-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    .glossary-header {
      text-align: center;
      margin-bottom: 40px;
    }
    .glossary-header h1 {
      font-size: 2.5rem;
      color: #333;
    }
    .glossary-section {
      margin-bottom: 50px;
    }
    .glossary-section h2 {
      border-bottom: 2px solid #ceb352;
      padding-bottom: 10px;
      margin-bottom: 20px;
      text-transform: capitalize;
      font-size: 1.8rem;
      color: #444;
    }
    .term-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
    }
    .term-card {
      background: #fff;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .term-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .term-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      border-bottom: 1px dashed #eee;
      padding-bottom: 10px;
    }
    .term-name {
      font-size: 1.25rem;
      font-weight: 700;
      color: #222;
    }
    .term-badge {
      padding: 4px 8px;
      border-radius: 12px;
      color: #fff;
      font-size: 0.75rem;
      font-weight: bold;
      letter-spacing: 0.5px;
    }
    .term-desc {
      color: #555;
      line-height: 1.6;
      font-size: 0.95rem;
    }
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

  <main class="glossary-container">
    <div class="glossary-header">
      <h1>Glossary & Terminology</h1>
      <p>A comprehensive guide to keywords, auras, zones, and standard terminology used in Trinity Draft.</p>
    </div>

{content}
  </main>
</body>
</html>
"""

content_html = ""

for category, terms in data.items():
    if not terms:
        continue
    content_html += f"    <div class='glossary-section'>\n      <h2>{category}</h2>\n      <div class='term-grid'>\n"
    for name, info in terms.items():
        if info is None:
            info = {}
        
        badge_html = ""
        if "color" in info:
            badge_html = f"<span class='term-badge' style='background-color: {info['color']};'>{info.get('type', 'Keyword').upper()}</span>"
            
        desc = info.get("desc", "")
        jp = info.get("jp", "")
        
        content_html += f"""        <div class='term-card'>
          <div class='term-header'>
            <span class='term-name'>{name}</span>
            {badge_html}
          </div>"""
        if desc:
            content_html += f"\n          <div class='term-desc'>{desc}</div>"
            
        content_html += "\n        </div>\n"
        
    content_html += "      </div>\n    </div>\n"

final_html = html_template.replace("{content}", content_html)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"Improved glossary page generated at {OUT_PATH}")
