import re

with open("tools/build_tts_save.py", "r", encoding="utf-8") as f:
    py = f.read()

# Change playmat scale
py = re.sub(r'"scaleX": 15, "scaleY": 1, "scaleZ": 15', '"scaleX": 5, "scaleY": 0.1, "scaleZ": 5', py)
py = re.sub(r'"posY": 0.9,', '"posY": 1.05,', py)

with open("tools/build_tts_save.py", "w", encoding="utf-8") as f:
    f.write(py)
