with open("site/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# insert a link below the h1
if "<h1>Trinity Draft - English Library</h1>" in html:
    html = html.replace("<h1>Trinity Draft - English Library</h1>", "<h1>Trinity Draft - English Library</h1>\n        <p><a href=\"rulebook.html\">Read the English Rulebook</a></p>")

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Link added.")
