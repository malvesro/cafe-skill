#!/usr/bin/env python3
"""
validar_cafe.py — Valida os parâmetros de preparo do café coado.

Uso interativo : python scripts/validar_cafe.py
Uso direto     : python scripts/validar_cafe.py --gramas 10 --ml 150 --temp 93 --minutos 3.5
"""
import sys
import argparse


REGRAS = {
    "gramas_por_ml": (10 / 150),   # proporção ideal
    "temp_min": 90,
    "temp_max": 96,
    "tempo_min": 3.0,
    "tempo_max": 4.0,
    "pre_infusao_ml": 30,
    "pre_infusao_seg": 30,
}


def validar(gramas: float, ml: float, temp: float, minutos: float) -> tuple:
    erros = []
    avisos = []
    ok = []

    # Proporção
    proporcao = gramas / ml if ml > 0 else 0
    ideal = REGRAS["gramas_por_ml"]
    desvio = abs(proporcao - ideal) / ideal * 100
    if desvio > 20:
        erros.append(
            f"❌ Proporção fora do padrão: {gramas:.1f}g para {ml:.0f}ml "
            f"(ideal: 10g/150ml — desvio de {desvio:.0f}%)"
        )
    elif desvio > 10:
        avisos.append(
            f"⚠️  Proporção levemente fora: {gramas:.1f}g para {ml:.0f}ml "
            f"(ideal: 10g/150ml — desvio de {desvio:.0f}%)"
        )
    else:
        ok.append(f"✅ Proporção correta: {gramas:.1f}g para {ml:.0f}ml")

    # Temperatura
    if temp >= 100:
        erros.append(
            f"❌ Temperatura muito alta: {temp:.0f}°C "
            f"(água fervente extrai amargor — use entre 90 e 96 °C)"
        )
    elif temp < REGRAS["temp_min"]:
        erros.append(
            f"❌ Temperatura muito baixa: {temp:.0f}°C "
            f"(abaixo de 90°C resulta em subextração — café aguado)"
        )
    elif temp > REGRAS["temp_max"]:
        avisos.append(
            f"⚠️  Temperatura acima do ideal: {temp:.0f}°C "
            f"(recomendado entre 90 e 96 °C)"
        )
    else:
        ok.append(f"✅ Temperatura ideal: {temp:.0f}°C")

    # Tempo de extração
    if minutos < REGRAS["tempo_min"]:
        avisos.append(
            f"⚠️  Tempo curto: {minutos:.1f} min "
            f"(subextração possível — café pode ficar azedo)"
        )
    elif minutos > REGRAS["tempo_max"]:
        avisos.append(
            f"⚠️  Tempo longo: {minutos:.1f} min "
            f"(superextração possível — café pode ficar amargo)"
        )
    else:
        ok.append(f"✅ Tempo de extração ideal: {minutos:.1f} min")

    return ok, avisos, erros


def entrada_interativa():
    print("\n☕ Validador de Café Coado")
    print("─" * 40)
    try:
        gramas  = float(input("Quantidade de café (g): "))
        ml      = float(input("Quantidade de água (ml): "))
        temp    = float(input("Temperatura da água (°C): "))
        minutos = float(input("Tempo de extração (minutos): "))
    except ValueError:
        print("❌ Entrada inválida. Use números.")
        sys.exit(1)
    return gramas, ml, temp, minutos


def main():
    parser = argparse.ArgumentParser(description="Valida parâmetros do café coado.")
    parser.add_argument("--gramas",   type=float, help="Quantidade de café em gramas")
    parser.add_argument("--ml",       type=float, help="Quantidade de água em ml")
    parser.add_argument("--temp",     type=float, help="Temperatura da água em °C")
    parser.add_argument("--minutos",  type=float, help="Tempo de extração em minutos")
    args = parser.parse_args()

    if all([args.gramas, args.ml, args.temp, args.minutos]):
        gramas, ml, temp, minutos = args.gramas, args.ml, args.temp, args.minutos
    else:
        gramas, ml, temp, minutos = entrada_interativa()

    ok, avisos, erros = validar(gramas, ml, temp, minutos)

    print("\n── Resultado da Validação ──────────────")
    for msg in ok:
        print(f"  {msg}")
    for msg in avisos:
        print(f"  {msg}")
    for msg in erros:
        print(f"  {msg}")
    print("─" * 40)

    if erros:
        print(f"\n❌ {len(erros)} erro(s) encontrado(s). Ajuste os parâmetros antes de preparar.")
        sys.exit(1)
    elif avisos:
        print(f"\n⚠️  {len(avisos)} aviso(s). O café pode ficar bom, mas há margem para melhoria.")
    else:
        print("\n✅ Todos os parâmetros estão perfeitos. Bom café!")


if __name__ == "__main__":
    main()
