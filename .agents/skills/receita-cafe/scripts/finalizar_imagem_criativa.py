#!/usr/bin/env python3
"""Finaliza a fase agent-native de imagem criativa da skill receita-cafe."""
import argparse
import json
import os
import sys

from flow_trace_engine import append_jsonl, event, load_jsonl, write_artifacts


def _load_manifest(path):
    with open(path, "r", encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def _write_manifest(path, manifest):
    with open(path, "w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file, indent=2, ensure_ascii=False)
        manifest_file.write("\n")


def _validate_png(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Imagem criativa nao encontrada: {path}")
    if not path.lower().endswith(".png"):
        raise ValueError("A imagem criativa final deve ser um arquivo PNG.")
    with open(path, "rb") as image_file:
        signature = image_file.read(8)
    if signature != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Arquivo informado nao possui assinatura PNG valida.")


def main():
    parser = argparse.ArgumentParser(description="Atualiza o manifesto com a imagem criativa final.")
    parser.add_argument("--manifest", required=True, help="Caminho do runtime_manifest_*.json.")
    parser.add_argument("--creative-image-path", required=True, help="Caminho do PNG criativo gerado pelo agente.")
    args = parser.parse_args()

    manifest_path = os.path.abspath(args.manifest)
    creative_image_path = os.path.abspath(args.creative_image_path)

    manifest = _load_manifest(manifest_path)
    _validate_png(creative_image_path)

    checks = manifest.setdefault("checks", {})
    checks["creative_image_exists"] = True

    artifacts = manifest.setdefault("artifacts", {})
    artifacts["creative_image_path"] = creative_image_path
    artifacts["manifest_path"] = manifest_path

    missing = [item for item in manifest.get("missing", []) if item != "creative_image_exists"]
    manifest["missing"] = missing
    manifest["creative_image_required"] = True
    manifest["multimodal_status"] = "ok"
    manifest["completion_allowed"] = True
    manifest["agent_next_action"] = "respond_to_user"
    if manifest.get("deterministic_status") == "ok":
        manifest["status"] = "ok"

    trace_jsonl_path = artifacts.get("flow_trace_jsonl_path")
    if trace_jsonl_path:
        append_jsonl(trace_jsonl_path, event(
            phase="creative_image_runtime",
            step_id="creative_image_finalized",
            title="Imagem criativa finalizada",
            decision="A imagem gerada pelo agente foi validada como PNG e vinculada ao manifesto.",
            files_read=[creative_image_path],
            files_written=[manifest_path],
            artifacts=[creative_image_path, manifest_path],
            status="ok",
        ))
        output_dir = os.path.dirname(trace_jsonl_path)
        trace_name = os.path.basename(trace_jsonl_path).replace("flow_trace_", "").replace(".jsonl", "")
        parts = trace_name.split("_")
        run_id = "_".join(parts[-2:])
        cenario = "_".join(parts[:-2])
        metadata = {
            "cenario": cenario,
            "run_id": run_id,
            "status": manifest.get("status"),
            "deterministic_status": manifest.get("deterministic_status"),
            "multimodal_status": manifest.get("multimodal_status"),
            "completion_allowed": manifest.get("completion_allowed"),
        }
        trace_paths = write_artifacts(output_dir, cenario, run_id, load_jsonl(trace_jsonl_path), metadata)
        artifacts.update(trace_paths)
        checks["flow_trace_jsonl_exists"] = os.path.exists(trace_paths["flow_trace_jsonl_path"])
        checks["flow_trace_json_exists"] = os.path.exists(trace_paths["flow_trace_json_path"])
        checks["flow_trace_html_exists"] = os.path.exists(trace_paths["flow_trace_html_path"])

    _write_manifest(manifest_path, manifest)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Erro ao finalizar imagem criativa: {exc}", file=sys.stderr)
        raise SystemExit(1)
