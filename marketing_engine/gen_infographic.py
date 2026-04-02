#!/usr/bin/env python3
"""
NeuralJira Image Engine — Motor de Infografías Profesionales
Invocable por Galldroko (OpenClaw) via CLI o import directo.

USO CLI:
  python gen_infographic.py tutorial   '{"title":"Cómo...", "steps":["paso1","paso2","paso3","paso4"], "cta":"¡Guarda este post!"}'
  python gen_infographic.py quote      '{"quote":"El código es...", "author":"Cory House"}'
  python gen_infographic.py news       '{"headline":"Título noticia", "body":"Resumen...", "source":"NeuralJira"}'
  python gen_infographic.py tips       '{"title":"5 Tips de Python", "tips":["tip1","tip2","tip3","tip4","tip5"]}'
  python gen_infographic.py comparison '{"title":"A vs B", "left_title":"Opción A", "left_items":["x","y"], "right_title":"Opción B", "right_items":["a","b"]}'
  python gen_infographic.py event      '{"name":"Evento...", "date":"Sábado 5 Abril", "desc":"Descripción corta"}'

Devuelve por stdout la ruta del archivo generado (para que Galldroko la capture).
"""

import sys
import json
import os
from datetime import datetime
from typing import List, Tuple, Optional

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Instala Pillow -> pip install Pillow", file=sys.stderr)
    sys.exit(1)

# ──────────────────────────────────────────────
#  BRAND COLORS — NeuralJira
# ──────────────────────────────────────────────
BG        = (10, 12, 24)       # Fondo oscuro profundo
SURFACE   = (22, 27, 50)       # Superficie de cards
PURPLE    = (139, 92, 246)     # #8B5CF6 - Morado neon
CYAN      = (34, 211, 238)     # #22D3EE - Cyan neon
GREEN     = (16, 185, 129)     # #10B981 - Verde
YELLOW    = (245, 158, 11)     # #F59E0B - Amarillo
RED       = (239, 68, 68)      # #EF4444 - Rojo
WHITE     = (248, 250, 252)    # Texto principal
GRAY      = (148, 163, 184)    # Texto secundario
DARK_CARD = (15, 20, 40)       # Card más oscura

STEP_COLORS = [CYAN, GREEN, YELLOW, RED, PURPLE]
TIP_COLORS  = [CYAN, GREEN, YELLOW, RED, PURPLE]

SIZE = (1080, 1080)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ──────────────────────────────────────────────
#  FONT LOADER  (Windows / Linux / Fallback)
# ──────────────────────────────────────────────
def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Carga la mejor fuente disponible en el sistema."""
    # 1. Fuente personalizada en assets/fonts/
    assets_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    custom = ["FiraCode-Bold.ttf", "FiraCode-Regular.ttf",
              "Inter-Bold.ttf", "Inter-Regular.ttf",
              "Montserrat-Bold.ttf", "Montserrat-Regular.ttf"]
    for fname in custom:
        if bold and "Bold" not in fname:
            continue
        path = os.path.join(assets_dir, fname)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    # 2. Fuentes del sistema Windows
    win_fonts = [
        r"C:\Windows\Fonts\arialbd.ttf",   # Arial Bold
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",  # Calibri Bold
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\verdanab.ttf",
        r"C:\Windows\Fonts\verdana.ttf",
    ]
    # 3. Fuentes del sistema Linux (VPS)
    linux_fonts = [
        "/usr/share/fonts/opentype/firacode/FiraCode-Bold.ttf",
        "/usr/share/fonts/opentype/firacode/FiraCode-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    candidates = (win_fonts if bold else win_fonts[1::2]) + linux_fonts
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    # 4. Fallback Pillow default
    return ImageFont.load_default()


# ──────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────
def _gradient_bg(draw: ImageDraw.ImageDraw, w: int, h: int):
    """Fondo con degradado sutil diagonal."""
    for i in range(h):
        ratio = i / h
        r = int(BG[0] + (SURFACE[0] - BG[0]) * ratio * 0.4)
        g = int(BG[1] + (SURFACE[1] - BG[1]) * ratio * 0.4)
        b = int(BG[2] + (SURFACE[2] - BG[2]) * ratio * 0.4)
        draw.line([(0, i), (w, i)], fill=(r, g, b))


def _hex_border(draw: ImageDraw.ImageDraw, x0, y0, x1, y1, color, width=3, radius=12):
    """Rectángulo redondeado con borde de color."""
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius,
                            outline=color, width=width, fill=DARK_CARD)


def _wrap(text: str, font: ImageFont.ImageFont, max_w: int) -> List[str]:
    """Word-wrap sin dependencias externas."""
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        try:
            tw = font.getlength(test)
        except AttributeError:
            tw = font.getsize(test)[0]
        if tw <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines or [""]


def _text_w(text: str, font: ImageFont.ImageFont) -> int:
    try:
        return int(font.getlength(text))
    except AttributeError:
        return font.getsize(text)[0]


def _draw_centered(draw, text, y, font, color, w=1080):
    tw = _text_w(text, font)
    draw.text(((w - tw) // 2, y), text, font=font, fill=color)


def _brand_header(draw, img_w=1080):
    """Logo NEURALJIRA + línea neon en la parte superior."""
    fnt = _load_font(38, bold=True)
    lbl = "NEURALJIRA"
    tw = _text_w(lbl, fnt)
    draw.text(((img_w - tw) // 2, 36), lbl, font=fnt, fill=PURPLE)
    # Línea neon debajo del logo
    draw.line([(60, 88), (img_w - 60, 88)], fill=CYAN, width=2)


def _brand_footer(draw, img_w=1080, img_h=1080):
    """Línea + URL de marca abajo."""
    draw.line([(60, img_h - 72), (img_w - 60, img_h - 72)], fill=PURPLE, width=2)
    fnt = _load_font(26)
    lbl = "neuraljira.com  •  @NeuralJira"
    tw = _text_w(lbl, fnt)
    draw.text(((img_w - tw) // 2, img_h - 58), lbl, font=fnt, fill=GRAY)


def _save(img: Image.Image, prefix: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"{prefix}_{ts}.jpg")
    img.save(path, format="JPEG", quality=92, optimize=True)
    return path


# ──────────────────────────────────────────────
#  TEMPLATES
# ──────────────────────────────────────────────

def make_tutorial(data: dict) -> str:
    """
    data: {
      "title": str,
      "steps": [str, str, str, str],   # 2–4 pasos
      "cta": str
    }
    """
    img = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(img)
    _gradient_bg(draw, *SIZE)

    # Decoración esquinas
    draw.rectangle([0, 0, 8, SIZE[1]], fill=PURPLE)
    draw.rectangle([SIZE[0]-8, 0, SIZE[0], SIZE[1]], fill=CYAN)

    _brand_header(draw)

    # Título principal
    fnt_title = _load_font(52, bold=True)
    title = data.get("title", "TUTORIAL").upper()
    lines = _wrap(title, fnt_title, 940)
    y = 112
    for line in lines[:3]:
        _draw_centered(draw, line, y, fnt_title, WHITE)
        y += 64

    # Steps
    steps = data.get("steps", [])[:4]
    step_top = y + 24
    step_h = min(170, (SIZE[1] - step_top - 130) // max(len(steps), 1))
    margin = 60
    inner_w = SIZE[0] - margin * 2

    fnt_label = _load_font(32, bold=True)
    fnt_desc  = _load_font(30)

    for i, step_text in enumerate(steps):
        color = STEP_COLORS[i % len(STEP_COLORS)]
        y0 = step_top + i * (step_h + 16)
        y1 = y0 + step_h - 8
        _hex_border(draw, margin, y0, SIZE[0] - margin, y1, color, width=3, radius=14)

        # Número del paso
        num_lbl = f"PASO {i+1}"
        draw.text((margin + 20, y0 + 14), num_lbl, font=fnt_label, fill=color)

        # Descripción con wrap
        desc_lines = _wrap(step_text, fnt_desc, inner_w - 140)
        dy = y0 + 14
        for dl in desc_lines[:2]:
            draw.text((margin + 160, dy), dl, font=fnt_desc, fill=WHITE)
            dy += 36

    # CTA
    fnt_cta = _load_font(30, bold=True)
    cta = data.get("cta", "¡Guarda este post! 🚀")
    _draw_centered(draw, cta, SIZE[1] - 108 - 40, fnt_cta, CYAN)

    _brand_footer(draw)
    return _save(img, "tutorial")


def make_quote(data: dict) -> str:
    """
    data: {
      "quote": str,
      "author": str
    }
    """
    img = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(img)
    _gradient_bg(draw, *SIZE)

    # Patrón de puntos decorativos
    for px in range(0, SIZE[0], 40):
        for py in range(0, SIZE[1], 40):
            draw.ellipse([px, py, px+2, py+2], fill=(50, 55, 90))

    # Marco central
    draw.rounded_rectangle([60, 200, SIZE[0]-60, SIZE[1]-200],
                            radius=24, outline=PURPLE, width=2, fill=(18, 22, 45))

    _brand_header(draw)

    # Comillas gigantes
    fnt_q = _load_font(140, bold=True)
    draw.text((90, 195), "\u201c", font=fnt_q, fill=PURPLE)
    draw.text((SIZE[0]-110, SIZE[1]-340), "\u201d", font=fnt_q, fill=PURPLE)

    # Texto de la cita
    fnt_quote  = _load_font(44, bold=False)
    quote_text = data.get("quote", "")
    lines = _wrap(quote_text, fnt_quote, 860)
    total_h = len(lines) * 58
    start_y = (SIZE[1] - total_h) // 2 - 20
    for line in lines:
        _draw_centered(draw, line, start_y, fnt_quote, WHITE)
        start_y += 58

    # Línea separadora + autor
    draw.line([(360, start_y + 30), (SIZE[0]-360, start_y + 30)], fill=CYAN, width=2)
    fnt_author = _load_font(32, bold=True)
    author = data.get("author", "")
    _draw_centered(draw, f"— {author}", start_y + 48, fnt_author, CYAN)

    _brand_footer(draw)
    return _save(img, "quote")


def make_news(data: dict) -> str:
    """
    data: {
      "headline": str,
      "body": str,
      "source": str   (opcional)
    }
    """
    img = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(img)
    _gradient_bg(draw, *SIZE)

    # Barra de "BREAKING NEWS"
    draw.rectangle([0, 96, SIZE[0], 148], fill=RED)
    fnt_break = _load_font(30, bold=True)
    _draw_centered(draw, "⚡ TECH NEWS  •  NEURALJIRA", 108, fnt_break, WHITE)

    _brand_header(draw)

    # Titular
    fnt_hl = _load_font(56, bold=True)
    headline = data.get("headline", "").upper()
    lines_hl = _wrap(headline, fnt_hl, 960)
    y = 168
    for line in lines_hl[:3]:
        _draw_centered(draw, line, y, fnt_hl, WHITE)
        y += 68

    # Línea divisora
    draw.line([(60, y + 12), (SIZE[0]-60, y + 12)], fill=CYAN, width=3)
    y += 36

    # Cuerpo de la noticia
    fnt_body = _load_font(34)
    body = data.get("body", "")
    body_lines = _wrap(body, fnt_body, 960)
    for line in body_lines[:8]:
        draw.text((60, y), line, font=fnt_body, fill=WHITE)
        y += 46

    # Fuente
    if data.get("source"):
        fnt_src = _load_font(28, bold=True)
        _draw_centered(draw, f"📌 Fuente: {data['source']}", SIZE[1]-128, fnt_src, GRAY)

    _brand_footer(draw)
    return _save(img, "news")


def make_tips(data: dict) -> str:
    """
    data: {
      "title": str,
      "tips": [str, str, str, str, str]  # hasta 5 tips
    }
    """
    img = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(img)
    _gradient_bg(draw, *SIZE)

    draw.rectangle([0, 0, 8, SIZE[1]], fill=GREEN)
    draw.rectangle([SIZE[0]-8, 0, SIZE[0], SIZE[1]], fill=CYAN)

    _brand_header(draw)

    fnt_title = _load_font(52, bold=True)
    title = data.get("title", "5 TIPS").upper()
    title_lines = _wrap(title, fnt_title, 940)
    y = 110
    for line in title_lines[:2]:
        _draw_centered(draw, line, y, fnt_title, WHITE)
        y += 62

    tips = data.get("tips", [])[:5]
    tip_h = min(140, (SIZE[1] - y - 120) // max(len(tips), 1))
    fnt_num  = _load_font(44, bold=True)
    fnt_tip  = _load_font(30)
    margin = 60

    for i, tip in enumerate(tips):
        color = TIP_COLORS[i % len(TIP_COLORS)]
        y0 = y + 24 + i * (tip_h + 12)
        y1 = y0 + tip_h
        _hex_border(draw, margin, y0, SIZE[0]-margin, y1, color, width=3, radius=12)

        # Número con círculo
        draw.ellipse([margin+10, y0+18, margin+70, y0+78], fill=color)
        num_tw = _text_w(str(i+1), fnt_num)
        draw.text((margin + 10 + (60 - num_tw)//2, y0 + 22), str(i+1),
                  font=fnt_num, fill=BG)

        # Texto del tip
        tip_lines = _wrap(tip, fnt_tip, SIZE[0] - margin*2 - 90)
        dy = y0 + max(12, (tip_h - len(tip_lines)*36)//2)
        for tl in tip_lines[:2]:
            draw.text((margin + 86, dy), tl, font=fnt_tip, fill=WHITE)
            dy += 36

    _brand_footer(draw)
    return _save(img, "tips")


def make_comparison(data: dict) -> str:
    """
    data: {
      "title": str,
      "left_title": str,
      "left_items": [str, ...],
      "right_title": str,
      "right_items": [str, ...]
    }
    """
    img = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(img)
    _gradient_bg(draw, *SIZE)

    _brand_header(draw)

    fnt_title = _load_font(46, bold=True)
    title = data.get("title", "A vs B").upper()
    _draw_centered(draw, title, 108, fnt_title, WHITE)

    # VS central
    draw.line([(SIZE[0]//2 - 1, 200), (SIZE[0]//2 - 1, SIZE[1]-100)], fill=GRAY, width=2)
    fnt_vs = _load_font(54, bold=True)
    draw.ellipse([SIZE[0]//2-40, SIZE[1]//2-40, SIZE[0]//2+40, SIZE[1]//2+40], fill=SURFACE)
    vs_w = _text_w("VS", fnt_vs)
    draw.text((SIZE[0]//2 - vs_w//2, SIZE[1]//2-34), "VS", font=fnt_vs, fill=YELLOW)

    # Columnas
    cols = [
        (data.get("left_title",""), data.get("left_items",[]), CYAN,   60,        480),
        (data.get("right_title",""), data.get("right_items",[]), PURPLE, SIZE[0]//2+20, SIZE[0]-60),
    ]
    fnt_col_title = _load_font(36, bold=True)
    fnt_item      = _load_font(28)

    for col_title, items, color, x0, x1 in cols:
        col_w = x1 - x0
        draw.rectangle([x0, 192, x1, 212], fill=color)
        ct_w = _text_w(col_title.upper(), fnt_col_title)
        draw.text((x0 + (col_w - ct_w)//2, 220), col_title.upper(),
                  font=fnt_col_title, fill=color)

        item_y = 278
        for item in items[:6]:
            item_lines = _wrap(f"✓  {item}", fnt_item, col_w - 10)
            for il in item_lines[:2]:
                draw.text((x0 + 8, item_y), il, font=fnt_item, fill=WHITE)
                item_y += 36
            item_y += 8

    _brand_footer(draw)
    return _save(img, "comparison")


def make_event(data: dict) -> str:
    """
    data: {
      "name": str,
      "date": str,
      "time": str   (opcional),
      "desc": str,
      "cta": str    (opcional)
    }
    """
    img = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(img)
    _gradient_bg(draw, *SIZE)

    # Barra superior de evento
    draw.rectangle([0, 96, SIZE[0], 160], fill=PURPLE)
    fnt_event_lbl = _load_font(32, bold=True)
    _draw_centered(draw, "🎉  PRÓXIMO EVENTO", 114, fnt_event_lbl, WHITE)

    _brand_header(draw)

    # Nombre del evento
    fnt_name = _load_font(60, bold=True)
    name_lines = _wrap(data.get("name","").upper(), fnt_name, 960)
    y = 180
    for line in name_lines[:3]:
        _draw_centered(draw, line, y, fnt_name, WHITE)
        y += 72

    # Card de fecha
    draw.rounded_rectangle([120, y+20, SIZE[0]-120, y+120],
                            radius=16, fill=SURFACE, outline=CYAN, width=3)
    fnt_date = _load_font(44, bold=True)
    date_str = data.get("date","")
    if data.get("time"):
        date_str += f"   🕐 {data['time']}"
    _draw_centered(draw, f"📅  {date_str}", y+42, fnt_date, CYAN)
    y += 140

    # Descripción
    fnt_desc = _load_font(32)
    desc = data.get("desc","")
    desc_lines = _wrap(desc, fnt_desc, 960)
    y += 20
    for line in desc_lines[:5]:
        _draw_centered(draw, line, y, fnt_desc, WHITE)
        y += 46

    # CTA
    cta = data.get("cta", "¡No te lo pierdas! Comparte 👇")
    fnt_cta = _load_font(34, bold=True)
    _draw_centered(draw, cta, SIZE[1]-128, fnt_cta, YELLOW)

    _brand_footer(draw)
    return _save(img, "event")


# ──────────────────────────────────────────────
#  DISPATCHER
# ──────────────────────────────────────────────
TEMPLATES = {
    "tutorial":   make_tutorial,
    "quote":      make_quote,
    "news":       make_news,
    "tips":       make_tips,
    "comparison": make_comparison,
    "event":      make_event,
}


def generate(template: str, data: dict) -> str:
    """API pública para llamar desde otros módulos Python."""
    fn = TEMPLATES.get(template.lower())
    if not fn:
        raise ValueError(f"Template desconocido: '{template}'. Opciones: {list(TEMPLATES)}")
    return fn(data)


def main():
    if len(sys.argv) < 2:
        print("USO: python gen_infographic.py <template> [json_data]")
        print("Templates disponibles:", ", ".join(TEMPLATES.keys()))
        sys.exit(1)

    template = sys.argv[1].lower()
    raw_data = sys.argv[2] if len(sys.argv) > 2 else "{}"

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON inválido — {e}", file=sys.stderr)
        sys.exit(1)

    try:
        output_path = generate(template, data)
        # Devuelve solo la ruta absoluta por stdout — Galldroko la captura
        print(os.path.abspath(output_path))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
