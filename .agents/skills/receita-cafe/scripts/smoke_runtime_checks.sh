#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
SCRIPT="$ROOT_DIR/.agents/skills/receita-cafe/scripts/receita_completa.py"
OUT_DIR="$ROOT_DIR/.ia/output"
RUN_ID="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT_DIR"

OUT_A="$OUT_DIR/_smoke_a_${RUN_ID}.out"
OUT_B="$OUT_DIR/_smoke_b_${RUN_ID}.out"
MAN_A="$OUT_DIR/_smoke_a_${RUN_ID}.manifest.json"

extract_manifest() {
  python3 - "$1" "$2" <<'PY'
import json
import sys

source_path = sys.argv[1]
target_path = sys.argv[2]
marker = "[RUNTIME_MANIFEST]"

with open(source_path, "r", encoding="utf-8") as fh:
    content = fh.read()

idx = content.find(marker)
if idx < 0:
    raise SystemExit("[SMOKE][FAIL] marcador [RUNTIME_MANIFEST] não encontrado")

payload = content[idx + len(marker):].strip()
try:
    data = json.loads(payload)
except Exception as exc:  # pragma: no cover - script utilitário
    raise SystemExit(f"[SMOKE][FAIL] manifesto inválido: {exc}")

with open(target_path, "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
PY
}

echo "[SMOKE] A: execução padrão deve fechar multimodal com sucesso"
python3 "$SCRIPT" --cenario debugging --pessoas 2 --manifest --chat-telemetry-style technical >"$OUT_A" 2>&1
extract_manifest "$OUT_A" "$MAN_A"

python3 - "$MAN_A" <<'PY'
import json
import os
import sys

manifest_path = sys.argv[1]
with open(manifest_path, "r", encoding="utf-8") as fh:
    manifest = json.load(fh)

if manifest.get("status") != "ok":
    raise SystemExit("[SMOKE][FAIL] A: status esperado=ok")
if manifest.get("completion_allowed") is not True:
    raise SystemExit("[SMOKE][FAIL] A: completion_allowed deve ser true")
if manifest.get("multimodal_status") != "ok":
    raise SystemExit("[SMOKE][FAIL] A: multimodal_status deve ser ok")
creative_path = (manifest.get("artifacts") or {}).get("creative_image_path")
if not creative_path or not creative_path.endswith(".png") or not os.path.exists(creative_path):
    raise SystemExit("[SMOKE][FAIL] A: creative_image_path inválido")
checks = manifest.get("checks") or {}
if manifest.get("flow_trace_real_validated") is not True:
    raise SystemExit("[SMOKE][FAIL] A: flow_trace_real_validated deve ser true")
if checks.get("creative_image_exists") is not True:
    raise SystemExit("[SMOKE][FAIL] A: creative_image_exists deve ser true")

timeline = manifest.get("chat_timeline") or []
required_stages = [
    "PRE-FLIGHT",
    "DETERMINISTIC",
    "ARTIFACT_PACKAGING",
    "MULTIMODAL_CLOSURE",
    "FINAL_RESPONSE",
]
stage_first_seq = {}
last_seq = 0
for event in timeline:
    seq = int(event.get("seq") or 0)
    if seq <= last_seq:
        raise SystemExit("[SMOKE][FAIL] A: seq não está em ordem crescente")
    last_seq = seq
    stage = event.get("etapa")
    if stage in required_stages and stage not in stage_first_seq:
        stage_first_seq[stage] = seq

missing = [stage for stage in required_stages if stage not in stage_first_seq]
if missing:
    raise SystemExit(f"[SMOKE][FAIL] A: marcos ausentes no chat_timeline: {missing}")

ordered = [stage_first_seq[s] for s in required_stages]
if ordered != sorted(ordered):
    raise SystemExit("[SMOKE][FAIL] A: marcos fora de ordem canônica")
PY

echo "[SMOKE][OK] A"

echo "[SMOKE] B: bloqueio multimodal deve expor motivo no chat"
set +e
python3 "$SCRIPT" --cenario debugging --pessoas 2 --manifest --chat-telemetry-style technical --creative-image-path "$OUT_DIR/_arquivo_inexistente_${RUN_ID}.png" >"$OUT_B" 2>&1
rc_b=$?
set -e
if [[ $rc_b -eq 0 ]]; then
  echo "[SMOKE][FAIL] B: esperado exit != 0 ao forçar imagem criativa inválida"
  exit 1
fi
if ! rg -q '\[FECHAMENTO_MULTIMODAL\]\[PORTAO\]\[DECIDIR\]\[WARN\].*motivo=creative_image_pending' "$OUT_B"; then
  echo "[SMOKE][FAIL] B: motivo de bloqueio não encontrado na telemetria de chat"
  exit 1
fi
echo "[SMOKE][OK] B"

echo "[SMOKE] C: telemetria de chat deve evitar termos legados em inglês"
if rg -q '\[(PRE-FLIGHT|DETERMINISTIC|ARTIFACT_PACKAGING|MULTIMODAL_CLOSURE|FINAL_RESPONSE)\]' "$OUT_A"; then
  echo "[SMOKE][FAIL] C: etapa legada em inglês detectada no chat"
  exit 1
fi
if rg -q '^\[[^]]+\]\[[^]]+\]\[(START|EXECUTE|VALIDATE|DECISION|FINALIZE|DONE|BLOCK)\]' "$OUT_A"; then
  echo "[SMOKE][FAIL] C: ação legada em inglês detectada no chat"
  exit 1
fi
echo "[SMOKE][OK] C"

echo "[SMOKE] Todos os checks de UX + multimodal passaram."
