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
    "mogiana": {"ratio": 1/12, "temp": 92, "moagem": "Média-Fina", "notas": "Doçura, Chocolate"},
    "cerrado": {"ratio": 1/15, "temp": 94, "moagem": "Média", "notas": "Nozes, Caramelo"},
    "sul_de_minas": {"ratio": 1/14, "temp": 90, "moagem": "Média-Grossa", "notas": "Acidez Cítrica"},
    "espirito_santo": {"ratio": 1/13, "temp": 91, "moagem": "Média", "notas": "Especiarias"},
    "generico": {"ratio": 1/15, "temp": 93, "moagem": "Média", "notas": "Equilibrado"}
}

CENARIOS = {
    "planning": {
        "regiao": "mogiana", 
        "insight": "Para estimativas que nunca atrasam (nos primeiros 5 minutos).",
        "humor": "A doçura balanceada ajuda a aceitar aquele card que 'é só uma alteraçãozinha'."
    },
    "debugging": {
        "regiao": "cerrado", 
        "insight": "Se o bug for um NullPointerException, este café é o único objeto que não será nulo hoje.",
        "humor": "Intenso e resiliente, como o desenvolvedor que não desiste do breakpoint."
    },
    "deploy": {
        "regiao": "sul_de_minas", 
        "insight": "Digno de um pipeline que passou de primeira. Notas complexas para um código estável.",
        "humor": "Acidez vibrante para te manter alerta enquanto os logs de produção estabilizam."
    },
    "code_review": {
        "regiao": "espirito_santo", 
        "insight": "Limpo e transparente. Ideal para enxergar aquele code smell escondido no sub-módulo.",
        "humor": "Um café com 'clean code' garantido pelo terroir."
    },
    "documentation": {
        "regiao": "generico", 
        "insight": "Volume alto e extração lenta. Perfeito para preencher o README que você procrastinou.",
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
        "cenario": args.cenario,
        "regiao": res_regiao,
        "cafe_g": round(args.ml * config["ratio"], 1) if args.ml else 0,
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
        title = f" [BARISTA ENGINE] Sugestão p/ {args.cenario.upper()}" if args.cenario else f" [BARISTA ENGINE] Perfil: {res_regiao.upper()}"
        print(f"\n{title}")
        print(f"─" * 45)
        if insight: print(f"💡 {insight}")
        if humor: print(f"🎭 {humor}")
        print(f"─" * 45)
        print(f"Café: {params['cafe_g']}g | Água: {args.ml}ml")
        print(f"Temperatura: {params['temp_alvo']}°C | Moagem: {params['moagem_ideal']}")
        if alerts:
            print("\n📋 ALERTAS DO SISTEMA:")
            for a in alerts: print(f"  {a}")
        print(f"─" * 45)

    # → Geração de infográfico visual (Iteracão 3)
    if args.imagem:
        try:
            # Adiciona volume_ml ao dict de params para o engine
            params["volume_ml"] = args.ml or 0
            engine_dir = os.path.join(os.path.dirname(__file__))
            sys.path.insert(0, engine_dir)
            from infografico_engine import gerar_infografico
            img_path = gerar_infografico(params)
            print(f"\n\U0001f5bc️  Infográfico gerado: {img_path}")
        except ImportError:
            print("\u26a0️  infografico_engine.py não encontrado. Execute a partir do diretório da skill.")
        except Exception as e:
            print(f"\u26a0️  Erro ao gerar imagem: {e}")

if __name__ == "__main__":
    main()
