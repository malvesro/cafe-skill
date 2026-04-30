#!/usr/bin/env python3
"""Finaliza a fase agent-native de imagem criativa da skill receita-cafe."""
import argparse
import json
import os
import sys
import base64
from PIL import Image

from flow_trace_engine import append_jsonl, event, load_jsonl, write_artifacts


def _load_manifest(path):
    with open(path, "r", encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def _write_manifest(path, manifest):
    with open(path, "w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file, indent=2, ensure_ascii=False)
        manifest_file.write("\n")


def _validate_image(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Imagem criativa nao encontrada: {path}")
    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as e:
        raise ValueError(f"O arquivo informado nao e uma imagem valida ou esta corrompido: {e}")


def main():
    parser = argparse.ArgumentParser(description="Atualiza o manifesto com a imagem criativa final.")
    parser.add_argument("--manifest", required=True, help="Caminho do runtime_manifest_*.json.")
    parser.add_argument("--creative-image-path", required=False, help="Caminho do PNG criativo gerado pelo agente.")
    parser.add_argument("--error-msg", required=False, help="Mensagem de erro amigável em caso de limite de cota, p/ embutir no Markdown.")
    args = parser.parse_args()

    if not args.creative_image_path and not args.error_msg:
        parser.error("É necessário informar --creative-image-path ou --error-msg.")

    manifest_path = os.path.abspath(args.manifest)
    manifest = _load_manifest(manifest_path)

    checks = manifest.setdefault("checks", {})
    artifacts = manifest.setdefault("artifacts", {})
    
    if args.creative_image_path:
        creative_image_path = os.path.abspath(args.creative_image_path)
        _validate_image(creative_image_path)
        checks["creative_image_exists"] = True
        artifacts["creative_image_path"] = creative_image_path
    else:
        checks["creative_image_exists"] = False
        artifacts["creative_image_path"] = None

    artifacts["manifest_path"] = manifest_path

    missing = [item for item in manifest.get("missing", []) if item != "creative_image_exists"]
    manifest["missing"] = missing
    manifest["creative_image_required"] = not bool(args.error_msg)
    manifest["multimodal_status"] = "ok" if args.creative_image_path else "fallback_error"
    manifest["completion_allowed"] = True
    manifest["agent_next_action"] = "respond_to_user"
    if manifest.get("deterministic_status") == "ok":
        manifest["status"] = "ok"

    trace_jsonl_path = artifacts.get("flow_trace_jsonl_path")
    if trace_jsonl_path:
        append_jsonl(trace_jsonl_path, event(
            phase="creative_image_runtime",
            step_id="creative_image_finalized" if args.creative_image_path else "creative_image_failed",
            title="Imagem criativa finalizada" if args.creative_image_path else "Imagem criativa falhou (Cota)",
            decision="A imagem gerada pelo agente foi validada como PNG e vinculada ao manifesto." if args.creative_image_path else "A cota de imagem expirou e uma mensagem foi definida.",
            files_read=[args.creative_image_path] if args.creative_image_path else [],
            files_written=[manifest_path],
            artifacts=[args.creative_image_path, manifest_path] if args.creative_image_path else [manifest_path],
            status="ok" if args.creative_image_path else "fallback_error",
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

    # Injeção de Imagem Criativa no Markdown Portátil (Base64) ou Erro Amigável
    markdown_path = artifacts.get("portable_markdown_path")
    if markdown_path and os.path.exists(markdown_path):
        try:
            import re
            
            with open(markdown_path, "r", encoding="utf-8") as md_file:
                md_content = md_file.read()
                
            if args.creative_image_path:
                with Image.open(args.creative_image_path) as img:
                    img_format = img.format.lower() if img.format else "png"
                
                with open(args.creative_image_path, "rb") as image_file:
                    b64_image = base64.b64encode(image_file.read()).decode("utf-8")
                
                replacement = f"## 🎨 Imagem Criativa\n![Imagem Criativa](data:image/{img_format};base64,{b64_image})"
            else:
                replacement_text = args.error_msg
                # Mantém o header da imagem para o texto do erro
                replacement = f"## 🎨 Imagem Criativa\n\n> ⚠️ **Aviso:** {replacement_text}\n"

            # O pattern que remove a pendência e TUDO abaixo até o '---' ou fim para poder remontar se for erro
            # Mas espera! O prompt criativo DEVE SER MANTIDO conforme pedido "mantendo o texto criativo de criação da imagem".
            # O texto do prompt na validar_cafe.py é:
            # ## 🎨 Imagem Criativa
            # *(Pendente: Geração por IA não configurada neste ambiente)*
            # > **Prompt para geração manual:**
            # > {prompt_criativo}
            
            # Precisamos substituir APENAS a linha de pendência com a msg amigável, e deixar o resto!
            if not args.creative_image_path:
                marker_pattern = r"\*\s*\(Pendente: Geração por IA não configurada neste ambiente\)\s*\*"
                new_msg = f"⚠️ *{args.error_msg}*"
                new_md_content = re.sub(marker_pattern, new_msg, md_content)
                if new_md_content != md_content:
                    with open(markdown_path, "w", encoding="utf-8") as md_file:
                        md_file.write(new_md_content)
            else:
                marker_pattern = r"## 🎨 Imagem Criativa\n\*\s*\(Pendente: Geração por IA não configurada neste ambiente\)\s*\*"
                new_md_content = re.sub(marker_pattern, replacement, md_content)
                if new_md_content == md_content:
                     new_md_content = re.sub(r"## 🎨 Imagem Criativa\n.*", replacement, md_content)
                
                with open(markdown_path, "w", encoding="utf-8") as md_file:
                    md_file.write(new_md_content)

        except Exception as md_exc:
            print(f"Aviso: Falha ao injetar imagem base64 no Markdown: {md_exc}", file=sys.stderr)

    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Erro ao finalizar imagem criativa: {exc}", file=sys.stderr)
        raise SystemExit(1)
