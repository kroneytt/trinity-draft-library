"""Overlay English card text onto Japanese Trinity Draft card scans.

Reads card data from data/cards.xlsx, applies terminology normalization and
per-card overrides (tools/card_overrides.yaml), and writes:
  images/en/<stem>.jpg          English card image (full resolution)
  reports/preview_<stem>.jpg    JP | EN side-by-side preview
  reports/overflow.md           cards whose text needed the minimum font size

Usage:
    python tools/make_card_images.py                 # every scan in images/jp
    python tools/make_card_images.py TD-01_X01 ...   # specific cards
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import openpyxl
import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
JP_DIR = ROOT / "images" / "jp"
EN_DIR = ROOT / "images" / "en"
REPORTS = ROOT / "reports"
XLSX = ROOT / "data" / "cards.xlsx"
OVERRIDES = ROOT / "tools" / "card_overrides.yaml"
WIN_FONTS = Path("C:/Windows/Fonts")

SS = 2  # supersampling factor for anti-aliased shapes

# --------------------------------------------------------------------------- layout
# All values are fractions of card width (x) / height (y).
FRAME_X0, FRAME_X1 = 0.024, 0.957   # vertical copyright strip starts at x≈0.962
FRAME_TOP_DEFAULT, FRAME_BOTTOM = 0.515, 0.889
BURST_BOX = (0.405, 0.893, 0.922, 0.980)  # stops before the green X logo
EPIC_BOX = (0.405, 0.893, 0.957, 0.980)   # Epic cards have no X logo
PANEL_ALPHA = 240
BACKDROP_BLUR = 8
CAPTIONS = [
    # (x0, y0, x1, y1, text)  - replaces the two small JP captions at the top
    (0.345, 0.066, 0.665, 0.107, "Color Condition: includes the above"),
    (0.092, 0.090, 0.340, 0.110, "Pay color to play this card"),
]
EFFECT_SIZE = (0.0235, 0.0140)   # max / min effect font size (x card height)
BURST_SIZE = (0.0190, 0.0120)

# --------------------------------------------------------------------------- styling
WHITE, BLACK = (255, 255, 255), (15, 15, 15)
DIM = (185, 185, 198)
KEYWORD = (255, 222, 120)
GOLD = (214, 172, 74)
GOLD_LIGHT = (240, 210, 140)
PANEL = (14, 14, 18)
COST_BG = (38, 38, 50)
COLOR_RGB = {
    "Red": (205, 45, 50), "Yellow": (222, 178, 40), "Blue": (45, 115, 215),
    "Purple": (145, 65, 195), "Colorless": (150, 150, 160),
}
TIMING = {
    "On Entry": (46, 96, 196), "On Attack": (128, 62, 196), "Trigger": (206, 118, 34),
    "Activate": (38, 148, 88), "Continuous": (28, 128, 150), "On Destroy": (92, 92, 104),
    "Shadow Condition": (78, 52, 122), "Equip Cost": (96, 96, 118),
}

FONT_FILES = {
    "regular": "segoeui.ttf", "bold": "segoeuib.ttf", "semibold": "seguisb.ttf",
    "italic": "segoeuii.ttf", "black": "seguibl.ttf", "jp": "YuGothB.ttc",
}

# --------------------------------------------------------------------------- terminology
# Prototype subset; the full table moves to data/glossary.yaml in phase 1.
RACE_MAP = {"Cavalry": "War Knight", "War Cavalry": "War Knight"}  # 戦騎
TEXT_REPLACEMENTS = [
    (re.compile(r"\[Optional\]"), "<Optional>"),
    (re.compile(r"\[(?:War )?Cavalry\]"), "[War Knight]"),
]

_font_cache: dict = {}


def font(kind: str, size: float) -> ImageFont.FreeTypeFont:
    key = (kind, max(int(size), 6))
    if key not in _font_cache:
        path = WIN_FONTS / FONT_FILES[kind]
        if not path.exists():
            path = WIN_FONTS / "arial.ttf"
        _font_cache[key] = ImageFont.truetype(str(path), key[1])
    return _font_cache[key]


def blend(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


# --------------------------------------------------------------------------- data
def stem_for(card_id: str) -> str:
    """'TD-01 LEG 01/20' -> 'TD-01_LEG_01'."""
    return re.sub(r"\s+", "_", re.sub(r"/\d+\s*$", "", card_id.strip()))


def load_cards() -> dict:
    ws = openpyxl.load_workbook(XLSX, read_only=True).active
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    cards = {}
    for row in rows:
        rec = dict(zip(header, row))
        if rec.get("Card_ID"):
            cards[stem_for(rec["Card_ID"])] = rec
    return cards


def normalize_text(text: str | None) -> str:
    text = (text or "").strip()
    for pat, rep in TEXT_REPLACEMENTS:
        text = pat.sub(rep, text)
    return text


def races_of(card) -> list[str]:
    raw = card.get("Race") or ""
    return [RACE_MAP.get(r.strip(), r.strip()) for r in raw.split("/") if r.strip()]


def split_name(name: str) -> tuple[str, str | None]:
    """Return (main name, epithet). Mirrors the JP layout of small epithet + big name."""
    if ", " in name:
        a, b = name.split(", ", 1)
        return (a, b) if b.lower().startswith("the ") else (b, a)
    return name, None


def type_label(t: str | None) -> str:
    return (t or "").upper().replace(" (", " · ").replace(")", "")


# --------------------------------------------------------------------------- rich text
TOKEN_RE = re.compile(r"\[[^\]]+\]|<[^>]+>|▶|\s+|[^\s\[<▶]+")


def ability_style(tag: str):
    if tag in TIMING:
        return TIMING[tag], WHITE, "chip"
    if re.match(r"(Shinra Summon|ZERO Summon|Reduced Summon)", tag):
        return GOLD, BLACK, "gold"
    if tag.endswith("Aura"):
        return (172, 42, 52), WHITE, "chip"
    return None


def split_abilities(text: str) -> list[str]:
    """Split effect text into paragraphs at ability tags that start a new sentence."""
    starts = [0]
    for m in re.finditer(r"\[([^\]]+)\]", text):
        if m.start() == 0 or not ability_style(m.group(1)):
            continue
        if text[: m.start()].rstrip()[-1:] in ".)|":
            starts.append(m.start())
    starts.append(len(text))
    paras = [text[a:b].strip(" |") for a, b in zip(starts, starts[1:])]
    return [p for p in paras if p]


@dataclass
class Atom:
    kind: str           # word | space | arrow | chip | gold | cost | opt | badge
    text: str
    width: float
    font: object = None
    color: tuple = WHITE
    bg: tuple | None = None
    fg: tuple | None = None


def make_chip(text, size, bg, fg, kind) -> Atom:
    f = font("semibold" if kind == "opt" else "bold", size * (0.74 if kind == "opt" else 0.80))
    pad = size * (0.62 if kind == "cost" else 0.40)
    return Atom(kind, text, f.getlength(text) + 2 * pad + size * 0.14, font=f, bg=bg, fg=fg)


def build_atoms(text: str, size: float, lead: Atom | None = None) -> list[Atom]:
    f_reg, f_bold, f_it = font("regular", size), font("bold", size), font("italic", size * 0.94)
    atoms = [lead, Atom("space", " ", f_reg.getlength(" "))] if lead else []
    depth = 0
    for tok in TOKEN_RE.findall(text):
        if tok.isspace():
            atoms.append(Atom("space", " ", f_reg.getlength(" ")))
        elif tok == "▶":
            atoms.append(Atom("arrow", "", size * 0.66))
        elif tok.startswith("[") and tok.endswith("]"):
            inner = tok[1:-1].strip()
            style = ability_style(inner)
            if style:
                atoms.append(make_chip(inner, size, *style))
            else:
                atoms.append(Atom("word", tok, f_bold.getlength(tok), font=f_bold, color=KEYWORD))
        elif tok.startswith("<") and tok.endswith(">"):
            inner = tok[1:-1].strip().strip("[]")
            if inner.lower() == "optional":
                atoms.append(make_chip("Optional", size, None, DIM, "opt"))
            else:
                atoms.append(make_chip(inner, size, COST_BG, WHITE, "cost"))
        else:
            opens = tok.count("(")
            dim = depth > 0 or opens > 0
            depth = max(depth + opens - tok.count(")"), 0)
            f = f_it if dim else f_reg
            atoms.append(Atom("word", tok, f.getlength(tok), font=f, color=DIM if dim else WHITE))
    return atoms


def wrap(paragraphs: list[list[Atom]], width: float):
    lines = []
    for atoms in paragraphs:
        line, x, first = [], 0.0, True
        for a in atoms:
            if a.kind == "space":
                if line:
                    line.append((a, x))
                    x += a.width
                continue
            if line and x + a.width > width:
                while line and line[-1][0].kind == "space":
                    line.pop()
                lines.append((line, first))
                line, x, first = [], 0.0, False
            line.append((a, x))
            x += a.width
        while line and line[-1][0].kind == "space":
            line.pop()
        if line:
            lines.append((line, first))
    return lines


def text_height(lines, size):
    paras = sum(1 for i, (_, first) in enumerate(lines) if first and i > 0)
    return len(lines) * size * 1.30 + paras * size * 0.32


def fit(paragraphs: list[str], width, height, max_size, min_size, lead_fn=None):
    size = max_size
    while True:
        built = [build_atoms(p, size, lead_fn(size) if (lead_fn and i == 0) else None)
                 for i, p in enumerate(paragraphs)]
        lines = wrap(built, width)
        if text_height(lines, size) <= height or size <= min_size:
            return size, lines, text_height(lines, size) > height
        size -= 1


def draw_atom(d: ImageDraw.ImageDraw, a: Atom, x, cy, size):
    if a.kind == "word":
        d.text((x, cy), a.text, font=a.font, fill=a.color, anchor="lm")
    elif a.kind == "arrow":
        s = size
        d.polygon([(x + s * 0.06, cy - s * 0.30), (x + s * 0.06, cy + s * 0.30), (x + s * 0.54, cy)], fill=WHITE)
    elif a.kind in ("chip", "gold", "badge", "opt", "cost"):
        h = size * 1.10
        x1 = x + a.width - size * 0.14
        box = [x, cy - h / 2, x1, cy + h / 2]
        if a.kind == "cost":
            k = h * 0.32
            pts = [(x, cy), (x + k, box[1]), (x1 - k, box[1]), (x1, cy), (x1 - k, box[3]), (x + k, box[3])]
            d.polygon(pts, fill=a.bg)
            d.line(pts + [pts[0]], fill=(205, 205, 220), width=max(int(size * 0.07), 1))
        elif a.kind == "opt":
            d.rounded_rectangle(box, radius=h * 0.3, outline=a.fg, width=max(int(size * 0.07), 1))
        else:
            outline = (120, 88, 28) if a.kind == "gold" else None
            d.rounded_rectangle(box, radius=h * (0.18 if a.kind == "badge" else 0.30), fill=a.bg,
                                outline=outline, width=max(int(size * 0.07), 1))
        d.text(((x + x1) / 2, cy), a.text, font=a.font, fill=a.fg, anchor="mm")


def draw_lines(d, lines, x0, y0, size):
    y, lh = y0, size * 1.30
    for i, (line, first) in enumerate(lines):
        if first and i > 0:
            y += size * 0.32
        for a, x in line:
            draw_atom(d, a, x0 + x, y + lh / 2, size)
        y += lh


# --------------------------------------------------------------------------- render
def render(stem: str, card: dict, ov: dict, src: Path | None = None) -> list[str]:
    issues = []
    base = Image.open(src or JP_DIR / f"{stem}.webp").convert("RGBA")
    W, H = base.size[0] * SS, base.size[1] * SS
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    X = lambda f: f * W  # noqa: E731
    Y = lambda f: f * H  # noqa: E731

    color_name = (card.get("Color") or "Colorless").split("/")[0].strip()
    tint = COLOR_RGB.get(color_name, COLOR_RGB["Colorless"])

    # --- top captions
    for x0, y0, x1, y1, text in CAPTIONS:
        d.rounded_rectangle([X(x0), Y(y0), X(x1), Y(y1)], radius=Y(y1 - y0) * 0.45, fill=(*PANEL, 225))
        s = Y(y1 - y0) * 0.62
        while font("semibold", s).getlength(text) > X(x1 - x0) * 0.92 and s > 6:
            s -= 1
        d.text(((X(x0) + X(x1)) / 2, (Y(y0) + Y(y1)) / 2), text, font=font("semibold", s), fill=WHITE, anchor="mm")

    # --- main text frame
    fx0, fx1 = X(FRAME_X0), X(FRAME_X1)
    fy0, fy1 = Y(ov.get("frame_top", FRAME_TOP_DEFAULT)), Y(FRAME_BOTTOM)
    d.rounded_rectangle([fx0, fy0, fx1, fy1], radius=X(0.022), fill=(*blend(PANEL, tint, 0.14), PANEL_ALPHA),
                        outline=(*tint, 255), width=int(SS * 2))
    d.line([(fx0 + X(0.03), fy0 + SS * 3), (fx1 - X(0.03), fy0 + SS * 3)], fill=(*blend(tint, WHITE, 0.4), 200), width=SS)
    pad = X(0.024)
    x, y = fx0 + pad, fy0 + Y(0.010)

    name, epithet = split_name((card.get("Name_English") or "").strip())
    if epithet:
        fe = font("semibold", Y(0.0175))
        d.text((x, y), epithet, font=fe, fill=GOLD_LIGHT, anchor="lt")
        y += Y(0.0175) * 1.30

    # chips + name row
    name_h = Y(0.036)
    cy = y + name_h / 2
    chip_size = Y(0.0195)
    cx = x
    chips = []
    if (card.get("Rarity") or "") == "Epic":
        chips.append(make_chip("EPIC", chip_size, GOLD, BLACK, "gold"))
    chips.append(make_chip(type_label(card.get("Type")), chip_size, (236, 236, 240), BLACK, "badge"))
    for c in chips:
        draw_atom(d, c, cx, cy, chip_size)
        cx += c.width
    cx += X(0.008)
    avail = fx1 - pad - cx
    ns = name_h
    while font("black", ns).getlength(name) > avail and ns > Y(0.018):
        ns -= 1
    if font("black", ns).getlength(name) > avail:
        issues.append("name too long for one line")
    d.text((cx, cy), name, font=font("black", ns), fill=WHITE, anchor="lm",
           stroke_width=int(SS * 1), stroke_fill=(0, 0, 0))
    y += name_h * 1.12

    # race banner + illustrator
    races = races_of(card)
    rh = Y(0.026)
    rcy = y + rh / 2
    if races:
        rtext = " / ".join(races)
        fr = font("semibold", Y(0.0170))
        rw = fr.getlength(rtext) + X(0.04)
        d.rounded_rectangle([x, y, x + rw, y + rh], radius=rh * 0.25, fill=(*blend(PANEL, tint, 0.62), 255))
        d.text((x + rw / 2, rcy), rtext, font=fr, fill=WHITE, anchor="mm")
    if ov.get("illustrator"):
        d.text((fx1 - pad, rcy), f"illus. {ov['illustrator']}", font=font("jp", Y(0.0125)), fill=DIM, anchor="rm")
    y += rh + Y(0.010)
    d.line([(x, y), (fx1 - pad, y)], fill=(*tint, 170), width=SS)
    y += Y(0.010)

    # effects
    effects = split_abilities(normalize_text(card.get("Effects")))
    if effects:
        size, lines, over = fit(effects, fx1 - pad - x, fy1 - Y(0.012) - y, Y(EFFECT_SIZE[0]), Y(EFFECT_SIZE[1]))
        draw_lines(d, lines, x, y, size)
        if over:
            issues.append("effect text overflows at minimum font size")

    # --- BURST / EPIC Rule panel
    burst = normalize_text(card.get("Epic_Rule_or_Burst"))
    if burst:
        m = re.match(r"^\[(BURST|EPIC Rule)\]\s*", burst, re.I)
        label = "EPIC RULE" if m and m.group(1).lower().startswith("epic") else "BURST"
        body = burst[m.end():] if m else burst
        box = EPIC_BOX if label == "EPIC RULE" else BURST_BOX
        bx0, by0, bx1, by1 = X(box[0]), Y(box[1]), X(box[2]), Y(box[3])
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=X(0.016), fill=(*PANEL, PANEL_ALPHA),
                            outline=(*(GOLD if label == "EPIC RULE" else (210, 210, 220)), 255), width=int(SS * 1.5))
        bp = X(0.016)

        def lead(s):
            if label == "BURST":
                return make_chip("BURST", s, WHITE, BLACK, "badge")
            return make_chip("EPIC RULE", s, GOLD, BLACK, "gold")

        size, lines, over = fit([body], bx1 - bx0 - 2 * bp, by1 - by0 - 2 * Y(0.006),
                                Y(BURST_SIZE[0]), Y(BURST_SIZE[1]), lead_fn=lead)
        th = text_height(lines, size)
        draw_lines(d, lines, bx0 + bp, by0 + max((by1 - by0 - th) / 2, Y(0.004)), size)
        if over:
            issues.append("BURST/EPIC text overflows at minimum font size")

    layer = layer.resize(base.size, Image.LANCZOS)
    # Blur the scan beneath the panels so leftover JP text can't be read through them.
    mask = layer.getchannel("A").point(lambda a: 255 if a > 8 else 0).filter(ImageFilter.MaxFilter(3))
    blurred = base.filter(ImageFilter.GaussianBlur(BACKDROP_BLUR))
    backdrop = Image.composite(blurred, base, mask)
    out = Image.alpha_composite(backdrop, layer).convert("RGB")
    EN_DIR.mkdir(parents=True, exist_ok=True)
    out.save(EN_DIR / f"{stem}.jpg", quality=93)

    # side-by-side preview
    jp = base.convert("RGB")
    gap = 24
    prev = Image.new("RGB", (jp.width * 2 + gap * 3, jp.height + gap * 2), (28, 28, 31))
    prev.paste(jp, (gap, gap))
    prev.paste(out, (jp.width + gap * 2, gap))
    REPORTS.mkdir(parents=True, exist_ok=True)
    prev.save(REPORTS / f"preview_{stem}.jpg", quality=90)
    return issues


def loose_key(s: str) -> str:
    """'TD01_R_13' and 'TD-01_R_013' both -> 'TD01R13' (case/hyphen/underscore/zero-pad insensitive)."""
    s = re.sub(r"[-_\s]", "", s.upper())
    return re.sub(r"(?<=\D)0+(?=\d)", "", s)


def main(argv: list[str]) -> int:
    cards = load_cards()
    overrides = yaml.safe_load(OVERRIDES.read_text(encoding="utf-8")) or {}
    by_key = {loose_key(s): s for s in cards}  # loose key -> canonical stem
    ov_by_key = {loose_key(s): v for s, v in overrides.items()}
    wanted = {loose_key(a.removesuffix(".webp")) for a in argv}
    report = []
    for src in sorted(JP_DIR.glob("*.webp")):
        k = loose_key(src.stem)
        if wanted and k not in wanted:
            continue
        stem = by_key.get(k)
        if not stem:
            report.append(f"- `{src.name}`: no matching Card_ID in cards.xlsx")
            print(f"{src.name}: NO MATCH")
            continue
        ov = ov_by_key.get(k) or {}
        card = {**cards[stem], **(ov.get("corrections") or {})}
        issues = render(stem, card, ov, src)
        print(f"{src.name} -> {stem}: {'OK' if not issues else '; '.join(issues)}")
        report += [f"- `{stem}`: {i}" for i in issues]
    (REPORTS / "overflow.md").write_text("# Overlay issues\n\n" + ("\n".join(report) or "None.") + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
