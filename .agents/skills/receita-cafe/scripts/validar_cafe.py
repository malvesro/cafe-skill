#!/usr/bin/env python3
"""
validar_cafe.py — Engine de validação harmonizada (Didática + Técnica).
"""
import sys
import os
import argparse
import json

# Lógica de Negócio (Sync com SKILL.md v2.1)
TERROIRS = {
    "mogiana": {"ratio": 1/12, "temp": 92, "moagem": "Média-Fina", "notas": "Doçura, Chocolate, Acidez Baixa"},
    "cerrado": {"ratio": 1/15, "temp": 94, "moagem": "Média", "notas": "Nozes, Caramelo, Corpo Marcante"},
    "sul_de_minas": {"ratio": 1/14, "temp": 90, "moagem": "Média-Grossa", "notas": "Frutas Amarelas, Acidez Cítrica"},
    "espirito_santo": {"ratio": 1/13, "temp": 91, "moagem": "Média", "notas": "Especiarias, Chocolate Amargo"},
    "mantiqueira": {"ratio": 1/12, "temp": 92, "moagem": "Média-Fina", "notas": "Aroma Marcante, Frutado, Notas de Nozes"},
    "chapada_diamantina": {"ratio": 1/14, "temp": 93, "moagem": "Média", "notas": "Aveludado, Cítrico, Final Prolongado"},
    "matas_de_minas": {"ratio": 1/13, "temp": 91, "moagem": "Média", "notas": "Doçura Notável, Caramelo, Chocolate"},
    "alta_mogiana": {"ratio": 1/12, "temp": 92, "moagem": "Média-Fina", "notas": "Corpo Encorpado, Acidez Média, Frutado"},
    "amazonico": {"ratio": 1/11, "temp": 94, "moagem": "Grossa", "notas": "Intenso, Amadeirado, Alta Cafeína"},
    "generico": {"ratio": 1/15, "temp": 93, "moagem": "Média", "notas": "Equilibrado"}
}

CENARIOS = {
    "planning": {
        "regiao": "mogiana", 
        "insight": "Sprint Planning: Estimativas que nunca atrasam (nos primeiros 5 minutos).",
        "humor": "A doçura ajuda a aceitar aquele card que 'é só uma alteraçãozinha'."
    },
    "debugging": {
        "regiao": "cerrado", 
        "insight": "Debugging: Se o bug for um NullPointerException, este café é o único objeto não nulo.",
        "humor": "Intenso e resiliente, como o dev que não desiste do breakpoint."
    },
    "deploy": {
        "regiao": "sul_de_minas", 
        "insight": "Deploy: Digno de um pipeline que passou de primeira. Notas complexas para código estável.",
        "humor": "Acidez vibrante para te manter alerta enquanto os logs de produção estabilizam."
    },
    "code_review": {
        "regiao": "espirito_santo", 
        "insight": "Code Review: Limpo e transparente. Ideal para ver aquele code smell escondido.",
        "humor": "Um café com 'clean code' garantido pelo terroir."
    },
    "scrum": {
        "regiao": "mantiqueira",
        "insight": "Scrum Rituals: Equilíbrio e cadência. Ideal para Daily e Retrospectiva.",
        "humor": "Corpo aveludado para suavizar os feedbacks da retrospectiva."
    },
    "team_topologies": {
        "regiao": "chapada_diamantina",
        "insight": "Team Topologies: Estruturando fluxos e domínios. Notas cítricas para clareza de fronteiras.",
        "humor": "O café ideal para alinhar Cognitive Load com a arquitetura do time."
    },
    "architecture": {
        "regiao": "matas_de_minas",
        "insight": "Software Architecture: Complexidade e visão de alto nível. Notas encorpadas e complexas.",
        "humor": "Tão bem estruturado quanto um diagrama C4 de nível 3."
    },
    "security": {
        "regiao": "amazonico",
        "insight": "Security/InfoSec: Alerta máximo. Robusta para garantir resiliência e foco total.",
        "humor": "Mais cafeína que uma sessão de pentest de madrugada."
    },
    "refactoring": {
        "regiao": "alta_mogiana",
        "insight": "Refactoring: Limpeza e otimização. Doçura alta para tornar o legado suportável.",
        "humor": "Removendo technical debt e adicionando aroma achocolatado."
    },
    "incident": {
        "regiao": "amazonico",
        "insight": "Incident Management: War Room. Café potente para restaurar o serviço em tempo recorde.",
        "humor": "O SLA de 99.9% de disponibilidade começa nesta xícara."
    },
    "documentation": {
        "regiao": "generico", 
        "insight": "Documentation: Volume alto e extração lenta. Perfeito para o README procrastinado.",
        "humor": "O café ideal para quando o único bug é a falta de comentários no código."
    }
}

def diagnosticar_extração(tempo_seg):
    if tempo_seg < 180:
        return "⚠️ Fluxo muito rápido. Sugestão: Use uma moagem mais FINA para aumentar a resistência."
    if tempo_seg > 270:
        return "⚠️ Fluxo muito lento. Sugestão: Use uma moagem mais GROSSA para facilitar a passagem."
    return "✅ Tempo de extração perfeito."

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ml", type=int, help="Volume de água")
    parser.add_argument("--gramas", type=float, help="Peso do café")
    parser.add_argument("--temp", type=int, help="Temperatura")
    parser.add_argument("--tempo", type=int, help="Tempo total em segundos")
    parser.add_argument("--regiao", type=str)
    parser.add_argument("--cenario", type=str, choices=CENARIOS.keys())
    parser.add_argument("--tds_agua", type=int, help="TDS da água (ppm)")
    parser.add_argument("--json", action="store_true", help="Saída em formato JSON")
    parser.add_argument("--imagem", action="store_true", help="Gera infográfico PNG da extracão")
    parser.add_argument("--markdown", action="store_true", help="Gera documento Markdown portátil (.md) com imagem embutida")
    args = parser.parse_args()

    # Lógica de cenário sobrepõe região se fornecido
    res_regiao = args.regiao or "generico"
    insight, humor = "", ""
    
    if args.cenario:
        conf = CENARIOS[args.cenario]
        res_regiao = conf["regiao"]
        insight = conf["insight"]
        humor = conf["humor"]

    config = TERROIRS.get(res_regiao.lower(), TERROIRS["generico"])
    alerts = []

    # Alerta Químico de Água
    if args.tds_agua:
        if args.tds_agua < 50: alerts.append("Água muito pura (mole). Café pode ficar sem corpo.")
        if args.tds_agua > 200: alerts.append("Água muito dura (mineralizada). Pode gerar amargor excessivo.")

    # Diagnóstico de Tempo
    if args.tempo:
        alerts.append(diagnosticar_extração(args.tempo))

    # Cálculo de Parâmetros
    params = {
        "cenario": args.cenario or "generico",
        "regiao": res_regiao,
        "cafe_g": round(args.ml * config["ratio"], 1) if args.ml else 0,
        "volume_ml": args.ml or 0,
        "temp_alvo": config["temp"],
        "moagem_ideal": config["moagem"],
        "notas": config["notas"],
        "insight_dev": insight,
        "humor_barista": humor,
        "avisos_barista": alerts
    }

    if args.json:
        print(json.dumps(params, indent=2, ensure_ascii=False))
    else:
        title = f" [BARISTA ENGINE] Sugestão p/ {params['cenario'].upper()}"
        print(f"\n{title}")
        print(f"─" * 45)
        if insight: print(f"💡 {insight}")
        if humor: print(f"🎭 {humor}")
        print(f"─" * 45)
        print(f"Café: {params['cafe_g']}g | Água: {params['volume_ml']}ml")
        print(f"Temperatura: {params['temp_alvo']}°C | Moagem: {params['moagem_ideal']}")
        if alerts:
            print("\n📋 ALERTAS DO SISTEMA:")
            for a in alerts: print(f"  {a}")
        print(f"─" * 45)

    # → Geração de infográfico visual (Iteracão 3)
    img_path = None
    if args.imagem:
        try:
            engine_dir = os.path.join(os.path.dirname(__file__))
            sys.path.insert(0, engine_dir)
            from infografico_engine import gerar_infografico
            img_path = gerar_infografico(params)
            print(f"\n🖼️  Infográfico gerado: {img_path}")
        except Exception as e:
            print(f"⚠️  Erro ao gerar imagem: {e}")

    # → Geração de Documento Markdown Portátil (Estratégia Sênior)
    if args.markdown and img_path:
        try:
            import base64
            from datetime import datetime
            
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            md_filename = f"receita_{params['cenario']}_{timestamp}.md"
            md_path = os.path.join(os.path.dirname(__file__), "..", "output", md_filename)
            
            md_content = f"""# ☕ Protocolo de Café: {params['cenario'].capitalize()}

Este documento é **autocontido** e portátil, gerado automaticamente pela *Advanced Brazilian Coffee Engine*.

## 🎬 Contexto (Storytelling)
{insight if insight else "Preparando um café excepcional para o momento atual."}
*{humor if humor else "Foco e precisão técnica em cada gota."}*

## 🧪 Parâmetros Técnicos
- **Região:** {params['regiao'].capitalize()} ({params['notas']})
- **Proporção:** {params['cafe_g']}g de café para {params['volume_ml']}ml de água
- **Temperatura Alvo:** {params['temp_alvo']}°C
- **Moagem Sugerida:** {params['moagem_ideal']}

## 📋 Protocolo de Execução
1. **Setup:** Aquecer a água e escaldar o filtro.
2. **Blooming:** Pré-infusão com 2x o peso do pó por 30s.
3. **Extração:** Despejos circulares em pulsos (40%/60%).
4. **Tempo:** 3:00 - 4:00 min.

---

## 🖼️ Infográfico Técnico (Embedded)
![Infográfico](data:image/png;base64,{encoded_string})

---
*Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write(md_content)
            print(f"📄 Documento Markdown portátil gerado: {os.path.abspath(md_path)}")
        except Exception as e:
            print(f"⚠️  Erro ao gerar Markdown: {e}")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
