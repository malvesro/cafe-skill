#!/usr/bin/env python3
"""
infografico_engine.py — Motor de geração de infográficos visuais para a skill receita-cafe.
Converte os parâmetros de extração em um PNG criativo e contextual, com identidade visual
única por cenário de desenvolvimento.

Uso standalone (teste):
    python3 infografico_engine.py --test
"""

import os
import sys
import json
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


# ─────────────────────────────────────────────────────────────
# PALETAS DE TEMAS — identidade visual por cenário
# ─────────────────────────────────────────────────────────────
TEMAS = {
    "debugging": {
        "emoji":        "🐛",
        "titulo":       "WAR ROOM",
        "bg_top":       "#1A0A0A",   # vermelho sangue escuro
        "bg_mid":       "#2D1515",
        "bg_bot":       "#1A0A0A",
        "accent":       "#C0392B",   # vermelho intenso
        "accent2":      "#E67E22",   # âmbar
        "text_title":   "#FF6B5B",
        "text_body":    "#F5CBA7",
        "text_muted":   "#922B21",
        "border":       "#E74C3C",
        "badge_bg":     "#922B21",
        "badge_fg":     "#FADBD8",
        "metric_bg":    "#3B1212",
    },
    "deploy": {
        "emoji":        "🚀",
        "titulo":       "LAUNCH MODE",
        "bg_top":       "#071A07",   # verde floresta escuro
        "bg_mid":       "#0D2B0D",
        "bg_bot":       "#071A07",
        "accent":       "#27AE60",   # verde esmeralda
        "accent2":      "#F1C40F",   # dourado
        "text_title":   "#58D68D",
        "text_body":    "#A9DFBF",
        "text_muted":   "#1E8449",
        "border":       "#2ECC71",
        "badge_bg":     "#1E8449",
        "badge_fg":     "#D5F5E3",
        "metric_bg":    "#0D280D",
    },
    "planning": {
        "emoji":        "🗺️",
        "titulo":       "SPRINT PLANNING",
        "bg_top":       "#050D1A",   # azul marinha profundo
        "bg_mid":       "#0A1930",
        "bg_bot":       "#050D1A",
        "accent":       "#2980B9",   # azul slate
        "accent2":      "#CD853F",   # cobre
        "text_title":   "#5DADE2",
        "text_body":    "#AED6F1",
        "text_muted":   "#1A5276",
        "border":       "#3498DB",
        "badge_bg":     "#154360",
        "badge_fg":     "#D6EAF8",
        "metric_bg":    "#0A1525",
    },
    "code_review": {
        "emoji":        "🔍",
        "titulo":       "CODE REVIEW",
        "bg_top":       "#100A1A",   # roxo profundo
        "bg_mid":       "#1E1030",
        "bg_bot":       "#100A1A",
        "accent":       "#8E44AD",   # roxo
        "accent2":      "#BDC3C7",   # prata
        "text_title":   "#BB8FCE",
        "text_body":    "#D7BDE2",
        "text_muted":   "#6C3483",
        "border":       "#9B59B6",
        "badge_bg":     "#512E5F",
        "badge_fg":     "#F5EEF8",
        "metric_bg":    "#1A0D28",
    },
    "documentation": {
        "emoji":        "📝",
        "titulo":       "DOC MODE",
        "bg_top":       "#1A1205",   # marrom café
        "bg_mid":       "#2D2010",
        "bg_bot":       "#1A1205",
        "accent":       "#A0522D",   # sienna/café
        "accent2":      "#DEB887",   # burlywood/creme
        "text_title":   "#D2A679",
        "text_body":    "#EDD9B8",
        "text_muted":   "#6B3A1F",
        "border":       "#C27A2E",
        "badge_bg":     "#5D2E0C",
        "badge_fg":     "#FAF0DC",
        "metric_bg":    "#251A08",
    },
    "generico": {
        "emoji":        "☕",
        "titulo":       "BARISTA MODE",
        "bg_top":       "#0A0A12",
        "bg_mid":       "#141420",
        "bg_bot":       "#0A0A12",
        "accent":       "#5C6BC0",
        "accent2":      "#80CBC4",
        "text_title":   "#7986CB",
        "text_body":    "#C5CAE9",
        "text_muted":   "#3949AB",
        "border":       "#5C6BC0",
        "badge_bg":     "#283593",
        "badge_fg":     "#E8EAF6",
        "metric_bg":    "#0E0E1A",
    },
}

REGIOES = {
    "mogiana":       "🌿 Mogiana, MG",
    "cerrado":       "🌾 Cerrado, MG",
    "sul_de_minas":  "🍋 Sul de Minas, MG",
    "espirito_santo":"🌶 Espírito Santo, ES",
    "generico":      "☕ Blend Especial",
}

W, H = 900, 560
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def _hex(color: str):
    """Converte hex string para tuple RGB."""
    c = color.lstrip("#")
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))


def _get_font(size: int, bold: bool = False):
    """Busca fontes disponíveis no sistema, fallback para default."""
    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    paths = candidates_bold if bold else candidates
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _draw_gradient_bg(draw: ImageDraw.ImageDraw, tema: dict):
    """Desenha um gradiente vertical de 3 zonas no background."""
    top = _hex(tema["bg_top"])
    mid = _hex(tema["bg_mid"])
    bot = _hex(tema["bg_bot"])
    half = H // 2
    for y in range(half):
        t = y / max(half - 1, 1)
        r = int(top[0] + (mid[0] - top[0]) * t)
        g = int(top[1] + (mid[1] - top[1]) * t)
        b = int(top[2] + (mid[2] - top[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    for y in range(half, H):
        t = (y - half) / max(H - half - 1, 1)
        r = int(mid[0] + (bot[0] - mid[0]) * t)
        g = int(mid[1] + (bot[1] - mid[1]) * t)
        b = int(mid[2] + (bot[2] - mid[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def _draw_border(draw: ImageDraw.ImageDraw, tema: dict):
    """Borda dupla com acento temático."""
    accent = _hex(tema["border"])
    accent2 = _hex(tema["accent2"])
    draw.rectangle([0, 0, W - 1, H - 1], outline=accent, width=3)
    draw.rectangle([6, 6, W - 7, H - 7], outline=accent2, width=1)


def _draw_header(draw: ImageDraw.ImageDraw, tema: dict, cenario: str, regiao_label: str):
    """Header com modo ativo, emoji e região."""
    # Linha separadora do header
    accent = _hex(tema["accent"])
    draw.line([(20, 85), (W - 20, 85)], fill=(*accent, 150), width=2)

    # Badge de modo
    badge_bg = _hex(tema["badge_bg"])
    badge_fg = _hex(tema["badge_fg"])
    badge_text = f"  {tema['emoji']} {tema['titulo']}  "
    font_badge = _get_font(13, bold=True)
    # Calcular largura do badge
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 20
    bh = 28
    draw.rounded_rectangle([20, 16, 20 + bw, 16 + bh], radius=5, fill=badge_bg)
    draw.text((30, 20), badge_text, font=font_badge, fill=badge_fg)

    # Título principal: "CAFÉ RECEITA"
    font_title = _get_font(32, bold=True)
    title_text = "☕ CAFÉ RECEITA"
    draw.text((20, 44), title_text, font=font_title, fill=_hex(tema["text_title"]))

    # Região à direita
    font_region = _get_font(13)
    region_text = regiao_label
    bbox_r = font_region.getbbox(region_text)
    rw = bbox_r[2] - bbox_r[0]
    draw.text((W - rw - 25, 20), region_text, font=font_region, fill=_hex(tema["text_muted"]))

    # Cenário à direita
    font_cenario = _get_font(11)
    cen_text = f"Contexto: {cenario.upper()}" if cenario else ""
    draw.text((W - 200, 38), cen_text, font=font_cenario, fill=_hex(tema["accent2"]))


def _draw_metrics(draw: ImageDraw.ImageDraw, tema: dict, params: dict):
    """Painel central de métricas: 4 cards lado a lado."""
    metrics = [
        ("PESSOAS", f"{params.get('num_pessoas', 1)}p",     "Rendimento"),
        ("CAFÉ",    f"{params.get('cafe_g', 0)}g",      "Peso do Pó"),
        ("ÁGUA",    f"{params.get('volume_ml', '—')}ml", "Volume Alvo"),
        ("TEMP",    f"{params.get('temp_alvo', 0)}°C",  "Temperatura"),
        ("MOAGEM",  params.get('moagem_ideal', '—'),     "Granulometria"),
    ]

    # 5 cards entre x=20 e x=880
    card_w = 160
    card_h = 90
    gap = (W - 40 - 5 * card_w) // 4
    y0 = 100

    metric_bg = _hex(tema["metric_bg"])
    accent = _hex(tema["accent"])
    accent2 = _hex(tema["accent2"])
    text_body = _hex(tema["text_body"])
    text_muted = _hex(tema["text_muted"])

    font_label = _get_font(10)
    font_value = _get_font(26, bold=True)
    font_sub = _get_font(10)

    for i, (label, value, subtitle) in enumerate(metrics):
        x0 = 20 + i * (card_w + gap)
        # Fundo do card
        draw.rounded_rectangle([x0, y0, x0 + card_w, y0 + card_h], radius=8, fill=metric_bg)
        # Borda left accent
        draw.rounded_rectangle([x0, y0, x0 + 3, y0 + card_h], radius=2, fill=accent)

        # Label topo
        draw.text((x0 + 12, y0 + 8), label, font=font_label, fill=_hex(tema["text_muted"]))
        # Valor central
        draw.text((x0 + 12, y0 + 22), value, font=font_value, fill=accent2)
        # Subtitle
        draw.text((x0 + 12, y0 + 66), subtitle, font=font_sub, fill=text_muted)


def _draw_insight(draw: ImageDraw.ImageDraw, tema: dict, params: dict):
    """Bloco de insight do desenvolvedor e humor do barista."""
    insight = params.get("insight_dev", "")
    humor = params.get("humor_barista", "")
    notas = params.get("notas", "")

    y = 210
    accent = _hex(tema["accent"])
    accent2 = _hex(tema["accent2"])
    text_body = _hex(tema["text_body"])
    text_muted = _hex(tema["text_muted"])
    metric_bg = _hex(tema["metric_bg"])

    # Separador
    draw.line([(20, y - 5), (W - 20, y - 5)], fill=(*accent, 100), width=1)

    font_sec = _get_font(11, bold=True)
    font_body = _get_font(12)
    font_small = _get_font(10)

    # Notas sensoriais (badge)
    if notas:
        draw.text((20, y + 2), "NOTAS SENSORIAIS:", font=font_sec, fill=_hex(tema["accent2"]))
        draw.text((20, y + 18), f"  🫘 {notas}", font=font_body, fill=text_body)
        y += 42

    # Insight Dev
    if insight:
        draw.text((20, y + 2), "💡 INSIGHT DO BARISTA-DEV:", font=font_sec, fill=_hex(tema["accent"]))
        # Wrap simples: máximo ~90 chars por linha
        words = insight.split()
        line, lines = "", []
        for w in words:
            if len(line) + len(w) + 1 <= 88:
                line += ("" if not line else " ") + w
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        for j, l in enumerate(lines[:2]):
            draw.text((20, y + 18 + j * 17), f"  {l}", font=font_body, fill=text_body)
        y += 20 + len(lines[:2]) * 17 + 6

    # Humor / Motivação
    if humor:
        draw.text((20, y + 2), "🎭 MOTIVAÇÃO:", font=font_sec, fill=_hex(tema["text_muted"]))
        words = humor.split()
        line, lines = "", []
        for w in words:
            if len(line) + len(w) + 1 <= 88:
                line += ("" if not line else " ") + w
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        for j, l in enumerate(lines[:2]):
            draw.text((20, y + 18 + j * 17), f"  {l}", font=font_body, fill=_hex(tema["text_muted"]))


def _draw_protocol(draw: ImageDraw.ImageDraw, tema: dict):
    """Mini-checklist do protocolo de execução (Golden Path)."""
    passos = [
        "⚙️  Setup Térmico (90–94°C)",
        "💧 Purga do Filtro",
        "🌸 Bloom 30s",
        "🔄 Extração em Pulsos (40% → 60%)",
    ]
    accent2 = _hex(tema["accent2"])
    text_muted = _hex(tema["text_muted"])
    metric_bg = _hex(tema["metric_bg"])

    x0 = W - 270
    y0 = 210
    pw, ph = 250, 155

    font_sec = _get_font(10, bold=True)
    font_step = _get_font(11)

    draw.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=8, fill=metric_bg)
    draw.text((x0 + 10, y0 + 8), "PROTOCOLO GOLDEN PATH", font=font_sec, fill=accent2)
    draw.line([(x0 + 10, y0 + 24), (x0 + pw - 10, y0 + 24)], fill=(*_hex(tema["accent"]), 120), width=1)

    for i, passo in enumerate(passos):
        y_p = y0 + 32 + i * 28
        # check circle
        cx, cy = x0 + 20, y_p + 7
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=_hex(tema["accent"]), width=1)
        draw.text((cx - 4, cy - 5), "✓", font=_get_font(10, bold=True), fill=_hex(tema["accent2"]))
        draw.text((x0 + 34, y_p), passo, font=font_step, fill=_hex(tema["text_body"]))


def _draw_footer(draw: ImageDraw.ImageDraw, tema: dict, params: dict):
    """Footer com QA alerts e assinatura."""
    accent = _hex(tema["accent"])
    accent2 = _hex(tema["accent2"])
    text_muted = _hex(tema["text_muted"])

    draw.line([(20, H - 55), (W - 20, H - 55)], fill=(*accent, 100), width=1)

    font_small = _get_font(10)
    font_warn = _get_font(10, bold=True)

    # Avisos de QA
    avisos = params.get("avisos_barista", [])
    if avisos:
        draw.text((20, H - 48), "⚠️ QA:", font=font_warn, fill=_hex(tema["accent2"]))
        aviso_txt = " | ".join(avisos)[:100]
        draw.text((58, H - 48), aviso_txt, font=font_small, fill=text_muted)

    # Assinatura
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    sig = f"Advanced Brazilian Coffee Engine v3.0 • {ts}"
    bbox = font_small.getbbox(sig)
    sw = bbox[2] - bbox[0]
    draw.text((W - sw - 20, H - 28), sig, font=font_small, fill=text_muted)

    # Ratio info
    ratio_label = f"Ratio: 1:{round(1/params.get('cafe_g', 1) * params.get('volume_ml', 1), 0):.0f}" if params.get("cafe_g") else ""
    draw.text((20, H - 28), ratio_label, font=font_small, fill=_hex(tema["accent2"]))


def gerar_infografico(params: dict) -> str:
    """
    Gera um infográfico PNG baseado nos parâmetros da skill.

    Args:
        params: dict com chaves: cenario, regiao, cafe_g, temp_alvo,
                moagem_ideal, notas, insight_dev, humor_barista,
                avisos_barista, volume_ml.

    Returns:
        Caminho absoluto para o arquivo PNG gerado.
    """
    cenario = params.get("cenario") or "generico"
    tema = TEMAS.get(cenario, TEMAS["generico"])
    regiao_key = params.get("regiao", "generico") or "generico"
    regiao_label = REGIOES.get(regiao_key.lower(), f"☕ {regiao_key.title()}")

    # Criar imagem
    img = Image.new("RGB", (W, H), _hex(tema["bg_top"]))
    draw = ImageDraw.Draw(img)

    _draw_gradient_bg(draw, tema)
    _draw_border(draw, tema)
    _draw_header(draw, tema, cenario, regiao_label)
    _draw_metrics(draw, tema, params)
    _draw_insight(draw, tema, params)
    _draw_protocol(draw, tema)
    _draw_footer(draw, tema, params)

    # Salvar
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cafe_{cenario}_{ts}.png"
    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path, "PNG")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Motor de infográfico — receita-cafe")
    parser.add_argument("--test", action="store_true", help="Gera um infográfico de teste para cada cenário.")
    args = parser.parse_args()

    if args.test:
        import importlib.util, sys
        # Parâmetros de exemplo por cenário
        exemplos = {
            "debugging": {"cenario": "debugging", "regiao": "cerrado", "cafe_g": 20.0, "temp_alvo": 94, "moagem_ideal": "Média", "notas": "Nozes, Caramelo", "insight_dev": "Se o bug for um NullPointerException, este café é o único objeto que não será nulo hoje.", "humor_barista": "Intenso e resiliente, como o desenvolvedor que não desiste do breakpoint.", "avisos_barista": [], "volume_ml": 300},
            "deploy":    {"cenario": "deploy", "regiao": "sul_de_minas", "cafe_g": 35.7, "temp_alvo": 90, "moagem_ideal": "Média-Grossa", "notas": "Acidez Cítrica", "insight_dev": "Digno de um pipeline que passou de primeira.", "humor_barista": "Acidez vibrante para te manter alerta.", "avisos_barista": [], "volume_ml": 500},
            "planning":  {"cenario": "planning", "regiao": "mogiana", "cafe_g": 25.0, "temp_alvo": 92, "moagem_ideal": "Média-Fina", "notas": "Doçura, Chocolate", "insight_dev": "Para estimativas que nunca atrasam (nos primeiros 5 minutos).", "humor_barista": "A doçura ajuda a aceitar aquele card que 'é só uma alteraçãozinha'.", "avisos_barista": [], "volume_ml": 300},
            "code_review":{"cenario": "code_review", "regiao": "espirito_santo", "cafe_g": 23.0, "temp_alvo": 91, "moagem_ideal": "Média", "notas": "Especiarias", "insight_dev": "Limpo e transparente. Para enxergar o code smell escondido.", "humor_barista": "Um café com clean code garantido pelo terroir.", "avisos_barista": [], "volume_ml": 300},
            "documentation":{"cenario": "documentation", "regiao": "generico", "cafe_g": 20.0, "temp_alvo": 93, "moagem_ideal": "Média", "notas": "Equilibrado", "insight_dev": "Volume alto para o README que você procrastinou.", "humor_barista": "O café ideal para quando o único bug é a falta de comentários.", "avisos_barista": ["Lembre de commitar a documentação!"], "volume_ml": 300},
        }
        print("Gerando infográficos de teste...\n")
        for nome, params_ex in exemplos.items():
            path = gerar_infografico(params_ex)
            print(f"  ✅ {nome:<15} → {path}")
        print("\nTeste concluído.")
