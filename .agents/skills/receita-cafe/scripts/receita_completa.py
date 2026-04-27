#!/usr/bin/env python3
"""
receita_completa.py - Runtime canonico da skill receita-cafe.

Este wrapper evita execucao conceitual da skill: sempre invoca o motor
deterministico com Flow Tracer, PNG tecnico e Markdown portatil.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

from flow_trace_engine import append_jsonl, event, load_jsonl, write_artifacts
from output_paths import resolve_output_dir


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
OUTPUT_DIR = resolve_output_dir()
VALIDAR_CAFE = os.path.join(SCRIPT_DIR, "validar_cafe.py")


def _build_command(args):
    cmd = [
        sys.executable,
        VALIDAR_CAFE,
        "--cenario",
        args.cenario,
        "--pessoas",
        str(args.pessoas),
        "--flow",
        "--imagem",
        "--markdown",
    ]

    if args.ml:
        cmd.extend(["--ml", str(args.ml)])
    if args.regiao:
        cmd.extend(["--regiao", args.regiao])
    if args.story:
        cmd.extend(["--story", args.story])
    if args.temp:
        cmd.extend(["--temp", str(args.temp)])
    if args.tempo:
        cmd.extend(["--tempo", str(args.tempo)])
    if args.tds_agua:
        cmd.extend(["--tds_agua", str(args.tds_agua)])

    return cmd


def _extract_path(stdout, label):
    pattern = rf"{label}: (.+)"
    match = re.search(pattern, stdout)
    if not match:
        return None
    return os.path.abspath(os.path.normpath(match.group(1).strip()))


def _extract_creative_prompt(stdout):
    marker = "PROMPT PARA IMAGEM CRIATIVA"
    if marker not in stdout:
        return None

    after_marker = stdout.split(marker, 1)[1]
    lines = after_marker.splitlines()
    prompt_lines = []
    collecting = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("─"):
            if collecting:
                break
            collecting = True
            continue
        if collecting and stripped:
            prompt_lines.append(stripped)

    return " ".join(prompt_lines).strip() or None


def _write_creative_prompt(cenario, prompt, run_id):
    if not prompt:
        return None

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"prompt_criativo_{cenario}_{run_id}.txt")
    with open(path, "w", encoding="utf-8") as prompt_file:
        prompt_file.write(prompt)
        prompt_file.write("\n")
    return os.path.abspath(path)


def _write_manifest(cenario, manifest, run_id):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"runtime_manifest_{cenario}_{run_id}.json")
    manifest["artifacts"]["manifest_path"] = os.path.abspath(path)
    with open(path, "w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file, indent=2, ensure_ascii=False)
        manifest_file.write("\n")
    return os.path.abspath(path)


def _append_markdown_telemetry(markdown_path, trace_paths):
    if not markdown_path or not os.path.exists(markdown_path):
        return False
    section = f"""

---

## Telemetria da Execução
- **Flow Trace JSONL:** {trace_paths['flow_trace_jsonl_path']}
- **Flow Trace JSON:** {trace_paths['flow_trace_json_path']}
- **Flow Trace HTML:** {trace_paths['flow_trace_html_path']}
"""
    with open(markdown_path, "a", encoding="utf-8") as md_file:
        md_file.write(section)
    return True


def _validate_deterministic(stdout, png_path, markdown_path, prompt_path):
    checks = {
        "flow_tracer": "[FLOW]" in stdout,
        "technical_png_exists": bool(png_path and os.path.exists(png_path)),
        "portable_markdown_exists": bool(markdown_path and os.path.exists(markdown_path)),
        "creative_prompt_exists": bool(prompt_path and os.path.exists(prompt_path)),
        "markdown_embeds_base64": False,
    }

    if checks["portable_markdown_exists"]:
        with open(markdown_path, "r", encoding="utf-8") as md_file:
            checks["markdown_embeds_base64"] = "data:image/png;base64" in md_file.read()

    missing = [name for name, ok in checks.items() if not ok]
    return checks, missing


def main():
    parser = argparse.ArgumentParser(description="Executa a receita-cafe no modo completo.")
    parser.add_argument("--cenario", required=True)
    parser.add_argument("--pessoas", type=int, required=True)
    parser.add_argument("--ml", type=int)
    parser.add_argument("--regiao")
    parser.add_argument("--story")
    parser.add_argument("--temp", type=int)
    parser.add_argument("--tempo", type=int)
    parser.add_argument("--tds_agua", type=int)
    parser.add_argument(
        "--creative-image-required",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Marca a fase agent-native de imagem criativa como obrigatoria.",
    )
    parser.add_argument("--manifest", action="store_true", help="Imprime manifesto JSON ao final.")
    args = parser.parse_args()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    trace_jsonl_path = os.path.abspath(os.path.join(OUTPUT_DIR, f"flow_trace_{args.cenario}_{run_id}.jsonl"))
    append_jsonl(trace_jsonl_path, event(
        phase="orchestration",
        step_id="runtime_start",
        title="Runtime canonico iniciado",
        decision="O wrapper receita_completa.py iniciou execucao completa obrigatoria.",
        inputs={
            "cenario": args.cenario,
            "pessoas": args.pessoas,
            "ml": args.ml,
            "creative_image_required": args.creative_image_required,
        },
        files_read=["SKILL.md", "scripts/receita_completa.py"],
    ))
    cmd = _build_command(args)
    append_jsonl(trace_jsonl_path, event(
        phase="orchestration",
        step_id="command_built",
        title="Comando deterministico montado",
        decision="A CLI base sera chamada com --flow --imagem --markdown.",
        inputs={"command": cmd},
        files_read=["scripts/validar_cafe.py"],
    ))
    env = os.environ.copy()
    env["RECEITA_CAFE_FLOW_JSONL"] = trace_jsonl_path
    result = subprocess.run(cmd, cwd=SKILL_DIR, text=True, capture_output=True, env=env)

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")

    png_path = _extract_path(result.stdout, "Infográfico gerado")
    markdown_path = _extract_path(result.stdout, "Documento Markdown portátil gerado")
    creative_prompt = _extract_creative_prompt(result.stdout)
    creative_prompt_path = _write_creative_prompt(args.cenario, creative_prompt, run_id)
    suggested_creative_image_path = os.path.abspath(
        os.path.join(OUTPUT_DIR, f"imagem_criativa_{args.cenario}_{run_id}.png")
    )
    checks, missing = _validate_deterministic(result.stdout, png_path, markdown_path, creative_prompt_path)
    append_jsonl(trace_jsonl_path, event(
        phase="artifact_generation",
        step_id="artifacts_detected",
        title="Artefatos determinísticos detectados",
        decision="O wrapper extraiu os caminhos produzidos pelo motor base e validou a entrega deterministica.",
        files_written=[path for path in (png_path, markdown_path, creative_prompt_path) if path],
        artifacts=[path for path in (png_path, markdown_path, creative_prompt_path) if path],
        inputs={"checks": checks, "missing": missing},
        status="ok" if not missing else "failed",
    ))
    deterministic_ok = result.returncode == 0 and not missing
    multimodal_status = "pending" if args.creative_image_required else "not_required"
    completion_allowed = deterministic_ok and not args.creative_image_required
    status = "failed"
    agent_next_action = "fix_deterministic_runtime"
    if deterministic_ok and args.creative_image_required:
        status = "pending_multimodal"
        agent_next_action = "generate_creative_image_with_native_tool_then_run_finalizer"
    elif deterministic_ok:
        status = "ok"
        agent_next_action = "respond_to_user"

    manifest = {
        "status": status,
        "deterministic_status": "ok" if deterministic_ok else "failed",
        "multimodal_status": multimodal_status if deterministic_ok else "blocked",
        "creative_image_required": args.creative_image_required,
        "completion_allowed": completion_allowed,
        "agent_next_action": agent_next_action,
        "command": cmd,
        "returncode": result.returncode,
        "artifacts": {
            "manifest_path": None,
            "technical_infographic_path": png_path,
            "portable_markdown_path": markdown_path,
            "creative_prompt_path": creative_prompt_path,
            "creative_image_path": None,
            "suggested_creative_image_path": suggested_creative_image_path,
            "flow_trace_jsonl_path": trace_jsonl_path,
            "flow_trace_json_path": None,
            "flow_trace_html_path": None,
        },
        "checks": checks,
        "missing": missing,
    }
    append_jsonl(trace_jsonl_path, event(
        phase="creative_image_runtime",
        step_id="creative_image_state",
        title="Estado da imagem criativa definido",
        decision=f"Imagem criativa obrigatoria: {args.creative_image_required}; status multimodal: {multimodal_status}.",
        files_read=[creative_prompt_path] if creative_prompt_path else [],
        artifacts=[suggested_creative_image_path],
        status=multimodal_status,
    ))
    manifest_path = _write_manifest(args.cenario, manifest, run_id)
    manifest["artifacts"]["manifest_path"] = manifest_path
    append_jsonl(trace_jsonl_path, event(
        phase="manifest_finalization",
        step_id="manifest_written",
        title="Manifesto de runtime persistido",
        decision="Manifesto registra status, checks, artefatos e proxima acao obrigatoria do agente.",
        files_written=[manifest_path],
        artifacts=[manifest_path],
        status=status,
    ))

    metadata = {
        "cenario": args.cenario,
        "run_id": run_id,
        "status": status,
        "deterministic_status": manifest["deterministic_status"],
        "multimodal_status": manifest["multimodal_status"],
        "completion_allowed": manifest["completion_allowed"],
    }
    trace_events = load_jsonl(trace_jsonl_path)
    trace_paths = write_artifacts(OUTPUT_DIR, args.cenario, run_id, trace_events, metadata)
    manifest["artifacts"].update(trace_paths)
    checks["flow_trace_jsonl_exists"] = os.path.exists(trace_paths["flow_trace_jsonl_path"])
    checks["flow_trace_json_exists"] = os.path.exists(trace_paths["flow_trace_json_path"])
    checks["flow_trace_html_exists"] = os.path.exists(trace_paths["flow_trace_html_path"])
    checks["markdown_links_flow_trace"] = _append_markdown_telemetry(markdown_path, trace_paths)
    manifest["checks"] = checks
    _write_manifest(args.cenario, manifest, run_id)

    print("\n[RUNTIME_MANIFEST]")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))

    if result.returncode != 0 or missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
