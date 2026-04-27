#!/usr/bin/env python3
"""Smoke test da finalizacao multimodal da skill receita-cafe."""
import base64
import json
import os
import subprocess
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILL_DIR = os.path.join(ROOT, ".agents", "skills", "receita-cafe")
WRAPPER = os.path.join(SKILL_DIR, "scripts", "receita_completa.py")
FINALIZER = os.path.join(SKILL_DIR, "scripts", "finalizar_imagem_criativa.py")

PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
)


def _load_manifest(stdout):
    marker = "[RUNTIME_MANIFEST]"
    if marker not in stdout:
        raise AssertionError("Manifesto de runtime nao foi impresso.")
    return json.loads(stdout.split(marker, 1)[1].strip())


def main():
    result = subprocess.run(
        [
            sys.executable,
            WRAPPER,
            "--cenario",
            "documentation",
            "--pessoas",
            "1",
            "--story",
            "Smoke test da finalizacao multimodal.",
        ],
        cwd=SKILL_DIR,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, file=sys.stderr, end="")
        raise AssertionError(f"Runtime completo falhou com codigo {result.returncode}.")

    manifest = _load_manifest(result.stdout)
    manifest_path = manifest["artifacts"]["manifest_path"]
    creative_image_path = manifest["artifacts"]["suggested_creative_image_path"]

    with open(creative_image_path, "wb") as image_file:
        image_file.write(PNG_1X1)

    finalized = subprocess.run(
        [
            sys.executable,
            FINALIZER,
            "--manifest",
            manifest_path,
            "--creative-image-path",
            creative_image_path,
        ],
        cwd=SKILL_DIR,
        text=True,
        capture_output=True,
    )
    if finalized.returncode != 0:
        print(finalized.stdout, end="")
        print(finalized.stderr, file=sys.stderr, end="")
        raise AssertionError(f"Finalizador falhou com codigo {finalized.returncode}.")

    updated = json.loads(finalized.stdout)
    if updated["status"] != "ok":
        raise AssertionError("Manifesto finalizado deveria retornar status ok.")
    if updated["multimodal_status"] != "ok":
        raise AssertionError("Manifesto nao foi finalizado como multimodal ok.")
    if not updated["completion_allowed"]:
        raise AssertionError("Conclusao deveria ser permitida depois da imagem criativa.")
    if updated["agent_next_action"] != "respond_to_user":
        raise AssertionError("Proxima acao deveria ser responder ao usuario.")
    if updated["artifacts"]["creative_image_path"] != os.path.abspath(creative_image_path):
        raise AssertionError("creative_image_path nao foi preenchido corretamente.")
    if not updated["checks"]["creative_image_exists"]:
        raise AssertionError("Check creative_image_exists nao foi marcado.")
    for check in ("flow_trace_jsonl_exists", "flow_trace_json_exists", "flow_trace_html_exists"):
        if not updated["checks"].get(check):
            raise AssertionError(f"Check de telemetria ausente apos finalizacao: {check}")

    with open(updated["artifacts"]["flow_trace_json_path"], "r", encoding="utf-8") as trace_file:
        trace = json.load(trace_file)
    step_ids = {event["step_id"] for event in trace["events"]}
    if "creative_image_finalized" not in step_ids:
        raise AssertionError("Flow Trace nao registrou a finalizacao da imagem criativa.")

    print("Smoke test finalizar_imagem_criativa: OK")


if __name__ == "__main__":
    raise SystemExit(main())
