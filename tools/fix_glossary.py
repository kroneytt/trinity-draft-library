import yaml

with open("data/glossary.yaml", "r", encoding="utf-8") as f:
    text = f.read()

replacements = {
    "登場晁E": "登場時",
    "アタチE晁E": "アタック時",
    "起勁E": "起動",
    "常晁E": "常時",
    "クイチEオーラ": "クイックオーラ",
    "神羁E喁E": "神羅召喚",
    "ZERO召喁E": "ZERO召喚",
    "軽減召喁E": "軽減召喚",
    "ブラチEィドライチE": "ブラッディドライブ",
    "カウンターヴォルチEクス": "カウンターヴォルテックス",
    "アビスゲーチE": "アビスゲート",
    "アルケミE": "アルケミー",
    "合佁E": "合体",
    "オーバEドライチE": "オーバードライブ",
    "オーバEカウンチE": "オーバーカウント",
    "地獁EチE": "地獄バック",
    "バEスチE": "バースト",
    "戦騁E": "戦騎",
    "機祁E": "機械",
    "精霁E": "精霊",
    "混沁E": "混沌",
    "ヴォイチE": "ヴォイド",
    "イチE": "イデア",
    "リザーチE": "リザーブ",
    "ライフデチE": "ライフデッキ",
    "獲得ライチE": "獲得ライフ",
    "ウォール": "ウォール",
    "有利なウォール": "有利なウォール"
}

for k, v in replacements.items():
    text = text.replace(k, v)

with open("data/glossary.yaml", "w", encoding="utf-8") as f:
    f.write(text)

print("Glossary mojibake fixed.")
