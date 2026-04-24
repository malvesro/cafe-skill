#!/usr/bin/env python3
"""
validar_cafe.py — Engine de validação harmonizada (Didática + Técnica).
"""
import sys
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
    parser.add_argument("--regiao", type=str, default="generico")
    parser.add_argument("--tds_agua", type=int, help="TDS da água (ppm)")
    parser.add_argument("--json", action="store_true", help="Saída em formato JSON")
    args = parser.parse_args()

    config = TERROIRS.get(args.regiao.lower(), TERROIRS["generico"])
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
        "regiao": args.regiao,
        "cafe_g": round(args.ml * config["ratio"], 1) if args.ml else 0,
        "temp_alvo": config["temp"],
        "moagem_ideal": config["moagem"],
        "notas": config["notas"],
        "avisos_barista": alerts
    }

    if args.json:
        print(json.dumps(params, indent=2))
    else:
        print(f"\n☕ [BARISTA ENGINE] Perfil: {args.regiao.upper()}")
        print(f"─" * 40)
        print(f"Café: {params['cafe_g']}g | Água: {args.ml}ml")
        print(f"Temperatura Ideal: {params['temp_alvo']}°C")
        print(f"Configuração de Moagem: {params['moagem_ideal']}")
        if alerts:
            print("\n📋 ALERTAS E DIAGNÓSTICOS:")
            for a in alerts: print(f"  {a}")
        print(f"─" * 40)

if __name__ == "__main__":
    main()
