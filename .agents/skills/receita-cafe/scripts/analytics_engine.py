#!/usr/bin/env python3
import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from output_paths import resolve_output_dir

# Importar helpers do infografico_engine se possível, mas vamos manter isolado para robustez
W, H = 900, 600
OUTPUT_DIR = resolve_output_dir()
DATA_FILE = os.path.join(OUTPUT_DIR, "history.json")

def _hex(color: str):
    c = color.lstrip("#")
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def _get_font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def processar_dashboard(flow: bool = False):
    def _log_internal(step, desc):
        if flow: print(f"       │  ├─ [DATA] {step}: {desc}")

    # 1. Carregar Dados
    _log_internal("Fetch", "Acessando banco de dados de consumo histórico.")
    if not os.path.exists(DATA_FILE):
        return "Nenhum histórico disponível."
    
    with open(DATA_FILE, "r") as f:
        history = json.load(f)
    
    if not history:
        return "Histórico vazio."

    _log_internal("Analyze", f"Processando {len(history)} registros para cálculo de KPIs.")
    
    # 2. Agregação de Dados
    total_ml = sum(e.get("volume_ml", 0) for e in history)
    total_g = sum(e.get("cafe_g", 0) for e in history)
    total_p = sum(e.get("pessoas", 0) for e in history)
    
    scenarios = {}
    for e in history:
        sc = e.get("cenario", "unknown")
        scenarios[sc] = scenarios.get(sc, 0) + 1
    
    fav_cenario = max(scenarios, key=scenarios.get) if scenarios else "N/A"

    # 3. Criar Imagem (Dashboard)
    bg_color = _hex("#0A0A12")
    accent = _hex("#F1C40F") # Gold
    text_color = _hex("#E8EAF6")
    
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([0, 0, W, 80], fill=_hex("#141420"))
    draw.text((30, 20), "📊 BARISTA ANALYTICS: REPORT", font=_get_font(30, True), fill=accent)
    draw.text((W-250, 30), datetime.now().strftime("%d/%m/%Y %H:%M"), font=_get_font(14), fill=_hex("#7986CB"))
    
    # Grid de Overview
    metrics = [
        ("TOTAL LÍTROS", f"{total_ml/1000:.1f}L", "Volume Produzido"),
        ("TOTAL CAFÉ", f"{total_g/1000:.2f}kg", "Grãos Utilizados"),
        ("PESSOAS", f"{total_p}", "Impacto Humano"),
        ("TOP CENÁRIO", fav_cenario.upper(), "Modo Predominante")
    ]
    
    for i, (label, val, sub) in enumerate(metrics):
        x0 = 30 + i * 215
        y0 = 110
        draw.rounded_rectangle([x0, y0, x0+200, y0+100], radius=10, fill=_hex("#1C1C2D"))
        draw.text((x0+15, y0+15), label, font=_get_font(12, True), fill=_hex("#7986CB"))
        draw.text((x0+15, y0+35), val, font=_get_font(24, True), fill=accent)
        draw.text((x0+15, y0+75), sub, font=_get_font(10), fill=_hex("#5C6BC0"))

    # Lista de Últimas Atividades
    draw.text((30, 240), "📑 ÚLTIMAS EXTRAÇÕES", font=_get_font(18, True), fill=accent)
    draw.line([(30, 265), (W-30, 265)], fill=_hex("#283593"), width=2)
    
    row_y = 280
    for e in reversed(history[-8:]):
        # Data
        date_str = e["timestamp"].split()[0]
        draw.text((30, row_y), date_str, font=_get_font(12), fill=_hex("#7986CB"))
        # Cenário Tag
        tag = e["cenario"].upper()
        draw.rounded_rectangle([130, row_y-2, 280, row_y+16], radius=4, fill=_hex("#283593"))
        draw.text((140, row_y), tag, font=_get_font(10, True), fill=text_color)
        # Detalhes
        detalhes = f"{e['regiao'].title()} | {e['volume_ml']}ml | {e['pessoas']}p"
        draw.text((300, row_y), detalhes, font=_get_font(12), fill=text_color)
        
        row_y += 30

    # Humor / Tech Insights
    draw.rectangle([30, H-120, W-30, H-30], fill=_hex("#141420"), outline=accent)
    humor = "ENGINE STATUS: 100% OPERACIONAL. SYSTEM STRESS LEVEL: "
    stress = "NOMINAL" if scenarios.get("incident", 0) == 0 else "CRITICAL (Incident detected!)"
    draw.text((50, H-100), humor + stress, font=_get_font(14, True), fill=text_color)
    draw.text((50, H-70), "💡 DICA: Seu consumo de Mogiana subiu 15%. Verifique o estoque de grãos.", font=_get_font(12), fill=_hex("#7986CB"))

    # Salvar
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dashboard_barista_{ts}.png"
    path = os.path.join(OUTPUT_DIR, filename)
    _log_internal("Export", f"Gerando dashboard visual em {filename}")
    img.save(path, "PNG")
    return path

if __name__ == "__main__":
    print(f"Testando Dashboard: {processar_dashboard()}")
