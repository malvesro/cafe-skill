#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
SCRIPT="$ROOT_DIR/.agents/skills/receita-cafe/scripts/receita_completa.py"

echo "[SMOKE] A: criativa obrigatória deve bloquear conclusão (exit != 0)"
set +e
python3 "$SCRIPT" --cenario debugging --pessoas 2 --manifest >/tmp/smoke_a.out 2>&1
rc_a=$?
set -e
if [[ $rc_a -eq 0 ]]; then
  echo "[SMOKE][FAIL] A: esperado exit != 0, obtido 0"
  exit 1
fi
grep -q '"completion_allowed": false' /tmp/smoke_a.out
grep -q '"completion_block_reason": "creative_image_pending"' /tmp/smoke_a.out
echo "[SMOKE][OK] A"

echo "[SMOKE] B: bypass só em modo dev"
set +e
python3 "$SCRIPT" --cenario debugging --pessoas 1 --no-creative-image-required --manifest >/tmp/smoke_b1.out 2>&1
rc_b1=$?
set -e
if [[ $rc_b1 -eq 0 ]]; then
  echo "[SMOKE][FAIL] B1: esperado erro sem RECEITA_CAFE_DEV_MODE"
  exit 1
fi
RECEITA_CAFE_DEV_MODE=1 python3 "$SCRIPT" --cenario debugging --pessoas 1 --no-creative-image-required --manifest >/tmp/smoke_b2.out 2>&1
grep -q '"status": "ok"' /tmp/smoke_b2.out
echo "[SMOKE][OK] B"

echo "[SMOKE] C: trace real validado no manifesto"
grep -q '"flow_trace_real_validated": true' /tmp/smoke_a.out
echo "[SMOKE][OK] C"

echo "[SMOKE] Todos os checks mínimos passaram."
