#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# generate_infographic.sh — Utilitário de Desenvolvedor (Helper)
# ──────────────────────────────────────────────────────────────────────────────
# OBJETIVO: 
#   Atalho rápido para testar a geração do infográfico técnico standalone.
#
# OBSERVAÇÕES DE ARQUITETURA:
#   1. Este script é uma ferramenta de conveniência para o desenvolvedor.
#   2. O fluxo oficial e canônico da skill deve ser invocado via:
#      python3 scripts/receita_completa.py
#   3. O orquestrador oficial (receita_completa.py) NÃO utiliza este .sh 
#      internamente para garantir portabilidade e telemetria total.
# ──────────────────────────────────────────────────────────────────────────────

# Executa o motor técnico no cenário de refatoração para 5 pessoas
python3 validar_cafe.py --cenario refactoring --pessoas 5 --markdown
