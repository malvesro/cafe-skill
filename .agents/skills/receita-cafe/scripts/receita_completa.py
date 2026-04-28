#!/usr/bin/env python3
"""
receita_completa.py - Runtime canônico da skill receita-cafe.

Este wrapper evita execução conceitual da skill: sempre invoca o motor
determinístico com Flow Tracer, PNG técnico e Markdown portátil.
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime

from flow_trace_engine import append_jsonl, event, load_jsonl, write_artifacts
from output_paths import resolve_output_dir


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
OUTPUT_DIR = resolve_output_dir()
VALIDAR_CAFE = os.path.join(SCRIPT_DIR, "validar_cafe.py")
FINALIZAR_IMAGEM = os.path.join(SCRIPT_DIR, "finalizar_imagem_criativa.py")

TELEMETRY_MODE_ALLOWED = {"resumido", "normal", "detalhado"}
TELEMETRY_MODE_EVENTS = {
    "resumido": {"START", "DONE", "BLOCK", "ERROR"},
    "normal": {"START", "EXECUTE", "VALIDATE", "DECISION", "FINALIZE", "DONE", "BLOCK", "WARN", "ERROR"},
    "detalhado": {
        "START", "EXECUTE", "VALIDATE", "DECISION", "WRITE", "READ", "FINALIZE", "DONE", "BLOCK", "WARN", "ERROR"
    },
}
CHAT_TELEMETRY_ENABLED = True
CHAT_TELEMETRY_STYLE = "friendly"
TELEMETRY_SEQ = 0
CANONICAL_CHAT_STAGES = {"PRE-FLIGHT", "DETERMINISTIC", "ARTIFACT_PACKAGING", "MULTIMODAL_CLOSURE", "FINAL_RESPONSE"}
CHAT_STAGE_PTBR = {
    "PRE-FLIGHT": "PREPARACAO",
    "DETERMINISTIC": "EXECUCAO_DETERMINISTICA",
    "ARTIFACT_PACKAGING": "EMPACOTAMENTO_ARTEFATOS",
    "MULTIMODAL_CLOSURE": "FECHAMENTO_MULTIMODAL",
    "FINAL_RESPONSE": "RESPOSTA_FINAL",
}
CHAT_COMPONENT_PTBR = {
    "ORQUESTRADOR": "ORQUESTRADOR",
    "CONFIG": "CONFIGURACAO",
    "AMBIENTE": "AMBIENTE",
    "SCRIPT": "SCRIPT",
    "FLOW_TRACE": "RASTRO_EXECUCAO",
    "GATE": "PORTAO",
    "FINALIZER": "FINALIZADOR",
}
CHAT_ACTION_PTBR = {
    "START": "INICIAR",
    "EXECUTE": "EXECUTAR",
    "VALIDATE": "VALIDAR",
    "DECISION": "DECIDIR",
    "WRITE": "ESCREVER",
    "READ": "LER",
    "FINALIZE": "FINALIZAR",
    "DONE": "CONCLUIR",
    "BLOCK": "BLOQUEAR",
    "WARN": "ALERTAR",
    "ERROR": "FALHAR",
}


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
        "--artifacts-json",
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


def _format_ts():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _telemetry_mode():
    mode = os.environ.get("RECEITA_CAFE_TELEMETRY_MODE", "normal").strip().lower()
    return mode if mode in TELEMETRY_MODE_ALLOWED else "normal"


def _emit_chat_telemetry(run_id, etapa, componente, acao, nivel, mensagem):
    if not CHAT_TELEMETRY_ENABLED:
        return
    global TELEMETRY_SEQ
    TELEMETRY_SEQ += 1
    mode = _telemetry_mode()
    if acao not in TELEMETRY_MODE_EVENTS[mode]:
        return
    ts = _format_ts()
    etapa_chat = CHAT_STAGE_PTBR.get(etapa, etapa)
    componente_chat = CHAT_COMPONENT_PTBR.get(componente, componente)
    acao_chat = CHAT_ACTION_PTBR.get(acao, acao)
    if CHAT_TELEMETRY_STYLE == "technical":
        print(f"[{etapa_chat}][{componente_chat}][{acao_chat}][{nivel}][{ts}][{run_id}][seq:{TELEMETRY_SEQ}] {mensagem}")
        return

    stage_title = {
        "PREPARACAO": "Preparação",
        "EXECUCAO_DETERMINISTICA": "Execução determinística",
        "EMPACOTAMENTO_ARTEFATOS": "Empacotamento de artefatos",
        "FECHAMENTO_MULTIMODAL": "Fechamento multimodal",
        "RESPOSTA_FINAL": "Resposta final",
    }.get(etapa_chat, etapa_chat.title())
    level_title = {"INFO": "Info", "WARN": "Aviso", "ERROR": "Erro"}.get(nivel, nivel)
    print(
        f"{level_title}: {stage_title} | {componente_chat.title()} | {acao_chat.title()} | "
        f"{mensagem} (run_id={run_id}, seq={TELEMETRY_SEQ})"
    )


def _timeline_append(manifest, etapa, componente, acao, nivel, mensagem):
    global TELEMETRY_SEQ
    TELEMETRY_SEQ += 1
    timeline = manifest.setdefault("chat_timeline", [])
    timeline.append({
        "timestamp": _format_ts(),
        "run_id": manifest.get("run_id"),
        "seq": TELEMETRY_SEQ,
        "etapa": etapa,
        "componente": componente,
        "acao": acao,
        "nivel": nivel,
        "mensagem": mensagem,
    })


def _classify_error(result_returncode, missing, completion_allowed, creative_required):
    if result_returncode != 0:
        return "deterministic_runtime_failed"
    if missing:
        return "required_artifacts_missing"
    if creative_required and not completion_allowed:
        return "multimodal_pending"
    return None


def _recovery_hint(error_classification):
    hints = {
        "deterministic_runtime_failed": "Revise logs do validar_cafe.py e dependências (ex.: Pillow).",
        "required_artifacts_missing": "Reexecute e confirme geração de PNG, Markdown, prompt e traces.",
        "multimodal_pending": "Gere/impute imagem criativa PNG e finalize manifesto.",
        "flow_trace_incomplete": "Verifique escrita em .ia/output e reexecute com --flow habilitado.",
    }
    return hints.get(error_classification)


def _error_cause(error_classification):
    causes = {
        "deterministic_runtime_failed": "falha na execução determinística do motor técnico",
        "required_artifacts_missing": "artefatos obrigatórios não foram detectados após a execução",
        "multimodal_pending": "fechamento multimodal pendente por ausência de imagem criativa válida",
        "flow_trace_incomplete": "rastro de execução incompleto para auditoria obrigatória",
    }
    return causes.get(error_classification, "causa não mapeada")


def _file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _artifact_descriptors(paths):
    detailed = _telemetry_mode() == "detalhado"
    checksum_enabled = os.environ.get("RECEITA_CAFE_TELEMETRY_CHECKSUM") == "1"
    descriptors = []
    for p in paths:
        desc = p
        if detailed and checksum_enabled and p and os.path.exists(p):
            desc = f"{p}#sha256={_file_sha256(p)[:16]}"
        descriptors.append(desc)
    return descriptors


def _print_delivery_summary(manifest):
    artifacts = manifest.get("artifacts", {})
    technical_png = artifacts.get("technical_infographic_path")
    markdown_path = artifacts.get("portable_markdown_path")
    creative_image = artifacts.get("creative_image_path")
    suggested_creative = artifacts.get("suggested_creative_image_path")

    print("\n[RESUMO_ENTREGA]")
    if markdown_path:
        print(f"- Markdown portátil: {markdown_path}")
    if technical_png:
        print(f"- Infográfico técnico: {technical_png}")
    if creative_image:
        print(f"- Imagem criativa: {creative_image}")
    elif suggested_creative:
        print(f"- Imagem criativa: pendente (destino sugerido: {suggested_creative})")


def _chat_coverage_complete(manifest):
    stages = {e.get("etapa") for e in manifest.get("chat_timeline", [])}
    return CANONICAL_CHAT_STAGES.issubset(stages)


def _extract_path(stdout, label):
    pattern = rf"{label}: (.+)"
    match = re.search(pattern, stdout)
    if not match:
        return None
    return os.path.abspath(os.path.normpath(match.group(1).strip()))


def _extract_artifacts_json(stdout):
    marker = "[ARTIFACTS_JSON]"
    if marker not in stdout:
        return None
    after_marker = stdout.split(marker, 1)[1].strip()
    if not after_marker:
        return None
    first_line = after_marker.splitlines()[0].strip()
    if not first_line:
        return None
    try:
        return json.loads(first_line)
    except Exception:
        return None


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


def _validate_flow_trace_real(trace_events, trace_paths, creative_required, completion_allowed):
    has_runtime_start = any(
        e.get("phase") == "orchestration" and e.get("step_id") == "runtime_start"
        for e in trace_events
    )
    has_command_built = any(
        e.get("phase") == "orchestration" and e.get("step_id") == "command_built"
        for e in trace_events
    )
    has_deterministic_runtime = any(e.get("phase") == "deterministic_runtime" for e in trace_events)
    has_creative_finalized = any(
        e.get("phase") == "creative_image_runtime" and e.get("step_id") == "creative_image_finalized"
        for e in trace_events
    )
    has_trace_files = all(
        os.path.exists(trace_paths.get(key, ""))
        for key in ("flow_trace_jsonl_path", "flow_trace_json_path", "flow_trace_html_path")
    )
    creative_event_ok = True
    if creative_required and completion_allowed:
        creative_event_ok = has_creative_finalized

    return (
        has_runtime_start
        and has_command_built
        and has_deterministic_runtime
        and has_trace_files
        and creative_event_ok
    )


def _run_creative_finalizer(manifest_path, creative_image_path):
    creative_image_path = os.path.abspath(creative_image_path)
    cmd = [
        sys.executable,
        FINALIZAR_IMAGEM,
        "--manifest",
        manifest_path,
        "--creative-image-path",
        creative_image_path,
    ]
    result = subprocess.run(cmd, cwd=SKILL_DIR, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            "Falha ao finalizar imagem criativa.\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )


def _is_valid_png(path):
    if not path or not os.path.exists(path):
        return False
    if not path.lower().endswith(".png"):
        return False
    with open(path, "rb") as image_file:
        return image_file.read(8) == b"\x89PNG\r\n\x1a\n"


def _try_generate_creative_image_native(prompt_text, target_path):
    cmd_template = os.environ.get("RECEITA_CAFE_NATIVE_IMAGE_CMD")
    if not cmd_template:
        return None, "native_unavailable"
    if not prompt_text:
        return None, "prompt_unavailable"

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    prompt_file_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".prompt.txt",
            dir=OUTPUT_DIR,
            delete=False,
        ) as prompt_file:
            prompt_file.write(prompt_text)
            prompt_file.write("\n")
            prompt_file_path = prompt_file.name

        format_data = {
            "prompt_file": prompt_file_path,
            "output_path": os.path.abspath(target_path),
            "prompt_text": prompt_text,
        }
        rendered_cmd = cmd_template.format(**format_data)
        result = subprocess.run(
            ["/bin/bash", "-lc", rendered_cmd],
            cwd=SKILL_DIR,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            return None, f"native_failed_rc_{result.returncode}"
        if _is_valid_png(target_path):
            return os.path.abspath(target_path), "generated_native_prompt"
        return None, "native_output_invalid_png"
    except KeyError as exc:
        return None, f"native_template_missing_key_{exc}"
    finally:
        if prompt_file_path and os.path.exists(prompt_file_path):
            os.remove(prompt_file_path)


def _generate_creative_image_from_technical(source_path, target_path, cenario):
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps

    source = os.path.abspath(source_path)
    target = os.path.abspath(target_path)
    os.makedirs(os.path.dirname(target), exist_ok=True)

    with Image.open(source).convert("RGB") as base:
        # Pipeline simples para garantir artefato criativo distinto:
        # contraste/cor + glow + vinheta suave.
        enriched = ImageEnhance.Color(base).enhance(1.22)
        enriched = ImageEnhance.Contrast(enriched).enhance(1.18)
        glow = enriched.filter(ImageFilter.GaussianBlur(radius=3))
        merged = Image.blend(enriched, glow, alpha=0.20)

        vignette = Image.new("L", merged.size, 0)
        vignette = ImageOps.expand(vignette, border=0, fill=0).filter(ImageFilter.GaussianBlur(radius=80))
        # Inverte para deixar centro claro e bordas mais escuras.
        vignette = ImageOps.invert(vignette)
        merged.putalpha(vignette)
        final = Image.new("RGB", merged.size, (8, 10, 14))
        final.paste(merged, mask=merged.split()[-1])

        final.save(target, format="PNG")

    return target


def _resolve_creative_image_path_for_closure(args, png_path, suggested_path, creative_prompt):
    if args.creative_image_path:
        resolved = os.path.abspath(args.creative_image_path)
        if not os.path.exists(resolved):
            raise FileNotFoundError(f"Imagem criativa informada não existe: {resolved}")
        return resolved, "provided"

    native_image_path, native_mode = _try_generate_creative_image_native(
        prompt_text=creative_prompt,
        target_path=suggested_path,
    )
    if native_image_path:
        return native_image_path, native_mode

    if png_path and os.path.exists(png_path):
        target = _generate_creative_image_from_technical(
            source_path=png_path,
            target_path=suggested_path,
            cenario=args.cenario,
        )
        return target, f"generated_from_technical_png_fallback_{native_mode}"

    return None, native_mode


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
        help="Marca a fase agent-native de imagem criativa como obrigatória.",
    )
    parser.add_argument(
        "--creative-image-path",
        help="PNG criativo já gerado para finalizar automaticamente o manifesto no mesmo run.",
    )
    parser.add_argument(
        "--chat-telemetry",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Habilita telemetria textual amigável no chat durante a execução.",
    )
    parser.add_argument(
        "--chat-telemetry-style",
        choices=("friendly", "technical"),
        default=os.environ.get("RECEITA_CAFE_CHAT_TELEMETRY_STYLE", "friendly"),
        help="Formato da telemetria no chat: friendly (sem colchetes) ou technical (com colchetes).",
    )
    parser.add_argument(
        "--creative-execution-mode",
        choices=("auto", "manual_chat"),
        default=os.environ.get("RECEITA_CAFE_CREATIVE_EXECUTION_MODE", "auto"),
        help=(
            "Define como a imagem criativa será tratada: "
            "'auto' tenta nativo/fallback automaticamente; "
            "'manual_chat' não executa geração no Python e mantém pending_multimodal."
        ),
    )
    parser.add_argument("--manifest", action="store_true", help="Imprime manifesto JSON ao final.")
    args = parser.parse_args()
    global CHAT_TELEMETRY_ENABLED, CHAT_TELEMETRY_STYLE
    CHAT_TELEMETRY_ENABLED = args.chat_telemetry
    CHAT_TELEMETRY_STYLE = args.chat_telemetry_style
    if not args.creative_image_required and os.environ.get("RECEITA_CAFE_DEV_MODE") != "1":
        parser.error(
            "--no-creative-image-required é permitido apenas em modo de desenvolvimento "
            "(defina RECEITA_CAFE_DEV_MODE=1)."
        )

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    _emit_chat_telemetry(
        run_id,
        "PRE-FLIGHT",
        "ORQUESTRADOR",
        "START",
        "INFO",
        "Inicializando execução canônica da skill.",
    )
    _emit_chat_telemetry(
        run_id,
        "PRE-FLIGHT",
        "CONFIG",
        "VALIDATE",
        "INFO",
        (
            f"Parâmetros recebidos: cenário={args.cenario}, pessoas={args.pessoas}, "
            f"volume_ml={args.ml or 'auto'}, modo_criativo={args.creative_execution_mode}."
        ),
    )
    _emit_chat_telemetry(
        run_id,
        "PRE-FLIGHT",
        "AMBIENTE",
        "VALIDATE",
        "INFO",
        f"Diretório de saída configurado em {OUTPUT_DIR}.",
    )
    trace_jsonl_path = os.path.abspath(os.path.join(OUTPUT_DIR, f"flow_trace_{args.cenario}_{run_id}.jsonl"))
    append_jsonl(trace_jsonl_path, event(
        phase="orchestration",
        step_id="runtime_start",
        title="Runtime canônico iniciado",
        decision="O wrapper receita_completa.py iniciou execução completa obrigatória.",
        inputs={
            "cenario": args.cenario,
            "pessoas": args.pessoas,
            "ml": args.ml,
            "creative_image_required": args.creative_image_required,
        },
        files_read=["SKILL.md", "scripts/receita_completa.py"],
    ))
    cmd = _build_command(args)
    _emit_chat_telemetry(
        run_id,
        "DETERMINISTIC",
        "SCRIPT",
        "EXECUTE",
        "INFO",
        "Executando validar_cafe.py com flow, imagem, markdown e artefatos JSON.",
    )
    append_jsonl(trace_jsonl_path, event(
        phase="orchestration",
        step_id="command_built",
        title="Comando determinístico montado",
        decision="A CLI base sera chamada com --flow --imagem --markdown.",
        inputs={"command": cmd},
        files_read=["scripts/validar_cafe.py"],
    ))
    env = os.environ.copy()
    env["RECEITA_CAFE_FLOW_JSONL"] = trace_jsonl_path
    result = subprocess.run(cmd, cwd=SKILL_DIR, text=True, capture_output=True, env=env)
    _emit_chat_telemetry(
        run_id,
        "DETERMINISTIC",
        "SCRIPT",
        "DONE",
        "INFO" if result.returncode == 0 else "ERROR",
        f"validar_cafe.py finalizado com código de retorno={result.returncode}.",
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")

    artifacts_json = _extract_artifacts_json(result.stdout) or {}
    png_path = artifacts_json.get("technical_infographic_path") or _extract_path(result.stdout, "Infográfico gerado")
    markdown_path = artifacts_json.get("portable_markdown_path") or _extract_path(result.stdout, "Documento Markdown portátil gerado")
    creative_prompt = artifacts_json.get("creative_prompt_text") or _extract_creative_prompt(result.stdout)
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
    artifact_paths = [path for path in (png_path, markdown_path, creative_prompt_path) if path]
    artifact_desc = _artifact_descriptors(artifact_paths)
    _emit_chat_telemetry(
        run_id,
        "ARTIFACT_PACKAGING",
        "ARTEFATOS",
        "VALIDATE",
        "INFO" if deterministic_ok else "ERROR",
        f"Validação determinística: {'ok' if deterministic_ok else 'falhou'}; itens ausentes={len(missing)}; artefatos={len(artifact_paths)}.",
    )
    _emit_chat_telemetry(
        run_id,
        "ARTIFACT_PACKAGING",
        "ARQUIVOS",
        "WRITE",
        "INFO",
        f"Arquivos gerados/atualizados: {', '.join(artifact_desc[:3])}.",
    )
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
        "run_id": run_id,
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
        "flow_trace_real_validated": False,
        "completion_block_reason": None,
        "chat_timeline": [],
    }
    _timeline_append(manifest, "PRE-FLIGHT", "ORQUESTRADOR", "START", "INFO", "Inicialização concluída.")
    _timeline_append(manifest, "DETERMINISTIC", "SCRIPT", "DONE", "INFO" if deterministic_ok else "ERROR", f"Retorno do motor determinístico: {result.returncode}.")
    append_jsonl(trace_jsonl_path, event(
        phase="creative_image_runtime",
        step_id="creative_image_state",
        title="Estado da imagem criativa definido",
        decision=f"Imagem criativa obrigatória: {args.creative_image_required}; status multimodal: {multimodal_status}.",
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
        decision="Manifesto registra status, checks, artefatos e próxima ação obrigatória do agente.",
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
    checks["flow_trace_real"] = _validate_flow_trace_real(
        trace_events=trace_events,
        trace_paths=trace_paths,
        creative_required=args.creative_image_required,
        completion_allowed=manifest["completion_allowed"],
    )
    checks["markdown_links_flow_trace"] = _append_markdown_telemetry(markdown_path, trace_paths)
    _emit_chat_telemetry(
        run_id,
        "ARTIFACT_PACKAGING",
        "FLOW_TRACE",
        "VALIDATE",
        "INFO" if checks["flow_trace_real"] else "ERROR",
        f"Rastro de execução real validado={'sim' if checks['flow_trace_real'] else 'não'}.",
    )
    if not checks["flow_trace_real"] and "flow_trace_real" not in missing:
        missing.append("flow_trace_real")
    if not checks["flow_trace_real"]:
        manifest["completion_block_reason"] = "flow_trace_incomplete"
        _emit_chat_telemetry(
            run_id,
            "ARTIFACT_PACKAGING",
            "FLOW_TRACE",
            "BLOCK",
            "ERROR",
            _recovery_hint("flow_trace_incomplete"),
        )
    manifest["missing"] = missing
    manifest["flow_trace_real_validated"] = checks["flow_trace_real"]
    if not manifest["completion_allowed"]:
        error_classification = _classify_error(
            result_returncode=result.returncode,
            missing=missing,
            completion_allowed=manifest["completion_allowed"],
            creative_required=manifest["creative_image_required"],
        )
        manifest["error_classification"] = error_classification
        manifest["recovery_hint"] = _recovery_hint(error_classification)
        if manifest["deterministic_status"] != "ok":
            manifest["completion_block_reason"] = "deterministic_runtime_failed"
        elif manifest["creative_image_required"]:
            manifest["completion_block_reason"] = "creative_image_pending"
        else:
            manifest["completion_block_reason"] = "unknown_blocker"
        _emit_chat_telemetry(
            run_id,
            "MULTIMODAL_CLOSURE",
            "GATE",
            "ERROR",
            "ERROR",
            (
                f"erro={manifest.get('error_classification')}; "
                f"causa={_error_cause(manifest.get('error_classification'))}; "
                f"ação_recomendada={manifest.get('recovery_hint')}"
            ),
        )
    else:
        manifest["error_classification"] = None
        manifest["recovery_hint"] = None
    manifest["checks"] = checks
    _write_manifest(args.cenario, manifest, run_id)
    _timeline_append(
        manifest,
        "ARTIFACT_PACKAGING",
        "FLOW_TRACE",
        "VALIDATE",
        "INFO" if checks["flow_trace_real"] else "ERROR",
        f"Flow Trace real validado={checks['flow_trace_real']}.",
    )
    _timeline_append(
        manifest,
        "MULTIMODAL_CLOSURE",
        "GATE",
        "DECISION",
        "INFO" if manifest["completion_allowed"] else "WARN",
        f"status={manifest['status']} completion_allowed={manifest['completion_allowed']}.",
    )
    warn_hint = None
    if not manifest["completion_allowed"]:
        if manifest.get("completion_block_reason") == "creative_image_pending":
            warn_hint = "próximo_passo=gerar imagem criativa PNG e finalizar manifesto."
        elif manifest.get("completion_block_reason") == "flow_trace_incomplete":
            warn_hint = "próximo_passo=verificar escrita do rastro em .ia/output e reexecutar."
        else:
            warn_hint = "próximo_passo=consultar manifesto e seguir agent_next_action."
    _emit_chat_telemetry(
        run_id,
        "MULTIMODAL_CLOSURE",
        "GATE",
        "DECISION",
        "INFO" if manifest["completion_allowed"] else "WARN",
        (
            f"estado={manifest['status']}, conclusao_permitida={manifest['completion_allowed']}, "
            f"motivo={manifest.get('completion_block_reason')}."
            if manifest["completion_allowed"]
            else f"estado={manifest['status']}, conclusao_permitida={manifest['completion_allowed']}, "
            f"motivo={manifest.get('completion_block_reason')}, {warn_hint}"
        ),
    )

    if args.creative_image_required and deterministic_ok:
        if args.creative_execution_mode == "manual_chat":
            _emit_chat_telemetry(
                run_id,
                "MULTIMODAL_CLOSURE",
                "IMAGEM_CRIATIVA",
                "DECISION",
                "WARN",
                (
                    "Modo manual_chat ativo: gere a imagem com o prompt no chat e "
                    f"salve em {suggested_creative_image_path}."
                ),
            )
            _emit_chat_telemetry(
                run_id,
                "MULTIMODAL_CLOSURE",
                "IMAGEM_CRIATIVA",
                "BLOCK",
                "ERROR",
                (
                    "Fechamento multimodal pendente; execute geração nativa no chat "
                    f"com o prompt {creative_prompt_path} e finalize o manifesto."
                ),
            )
            with open(manifest_path, "r", encoding="utf-8") as manifest_file:
                manifest = json.load(manifest_file)
            manifest["status"] = "pending_multimodal"
            manifest["completion_allowed"] = False
            manifest["multimodal_status"] = "pending"
            manifest["completion_block_reason"] = "creative_image_pending"
            manifest["agent_next_action"] = "generate_creative_image_in_chat_then_run_finalizer"
            manifest["checks"]["creative_image_exists"] = False
            _timeline_append(
                manifest,
                "MULTIMODAL_CLOSURE",
                "FINALIZER",
                "BLOCK",
                "ERROR",
                "Modo manual_chat: aguardando imagem criativa gerada no chat para finalizar.",
            )
            _write_manifest(args.cenario, manifest, run_id)
        else:
            creative_image_path, creative_image_mode = _resolve_creative_image_path_for_closure(
                args=args,
                png_path=png_path,
                suggested_path=suggested_creative_image_path,
                creative_prompt=creative_prompt,
            )
            if creative_image_path:
                _emit_chat_telemetry(
                    run_id,
                    "MULTIMODAL_CLOSURE",
                    "IMAGEM_CRIATIVA",
                    "DECISION",
                    "INFO",
                    f"Imagem criativa resolvida via modo={creative_image_mode}.",
                )
                append_jsonl(trace_jsonl_path, event(
                    phase="creative_image_runtime",
                    step_id="creative_image_auto_resolved",
                    title="Imagem criativa resolvida para fechamento",
                    decision=f"Modo de resolução da imagem criativa: {creative_image_mode}.",
                    files_read=[creative_image_path],
                    artifacts=[creative_image_path],
                    status="ok",
                ))
                _write_manifest(args.cenario, manifest, run_id)
                _run_creative_finalizer(manifest_path, creative_image_path)
                _emit_chat_telemetry(
                    run_id,
                    "MULTIMODAL_CLOSURE",
                    "FINALIZER",
                    "FINALIZE",
                    "INFO",
                    "Finalizador multimodal executado com sucesso.",
                )
            else:
                _emit_chat_telemetry(
                    run_id,
                    "MULTIMODAL_CLOSURE",
                    "IMAGEM_CRIATIVA",
                    "BLOCK",
                    "ERROR",
                    "Não foi possível resolver imagem criativa automaticamente para fechamento.",
                )
                append_jsonl(trace_jsonl_path, event(
                    phase="creative_image_runtime",
                    step_id="creative_image_auto_resolved",
                    title="Imagem criativa indisponível para fechamento",
                    decision="Não foi possível resolver imagem criativa automaticamente; fechamento multimodal permaneceu pendente.",
                    artifacts=[suggested_creative_image_path],
                    status="failed",
                ))
            with open(manifest_path, "r", encoding="utf-8") as manifest_file:
                manifest = json.load(manifest_file)
            checks = manifest.get("checks", checks)
            missing = manifest.get("missing", missing)
            manifest["flow_trace_real_validated"] = checks.get("flow_trace_real", False)
            if manifest.get("completion_allowed", False):
                manifest["completion_block_reason"] = None
                manifest["error_classification"] = None
                manifest["recovery_hint"] = None
            _timeline_append(
                manifest,
                "MULTIMODAL_CLOSURE",
                "FINALIZER",
                "FINALIZE",
                "INFO" if manifest.get("completion_allowed", False) else "ERROR",
                "Fechamento multimodal concluído." if manifest.get("completion_allowed", False) else "Fechamento multimodal pendente.",
            )
            _write_manifest(args.cenario, manifest, run_id)

    _emit_chat_telemetry(
        run_id,
        "FINAL_RESPONSE",
        "ORQUESTRADOR",
        "DONE" if manifest.get("completion_allowed", False) else "BLOCK",
        "INFO" if manifest.get("completion_allowed", False) else "ERROR",
        f"Resposta final {'liberada' if manifest.get('completion_allowed', False) else 'bloqueada'} (status={manifest.get('status')}).",
    )
    _timeline_append(
        manifest,
        "FINAL_RESPONSE",
        "ORQUESTRADOR",
        "DONE" if manifest.get("completion_allowed", False) else "BLOCK",
        "INFO" if manifest.get("completion_allowed", False) else "ERROR",
        f"Resposta final {'liberada' if manifest.get('completion_allowed', False) else 'bloqueada'}.",
    )
    checks["chat_coverage_complete"] = _chat_coverage_complete(manifest)
    if not checks["chat_coverage_complete"] and "chat_coverage_complete" not in missing:
        missing.append("chat_coverage_complete")
    manifest["checks"] = checks
    manifest["missing"] = missing
    _write_manifest(args.cenario, manifest, run_id)

    _print_delivery_summary(manifest)
    print("\n[RUNTIME_MANIFEST]")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))

    if result.returncode != 0 or missing:
        return 1
    if args.creative_image_required and not manifest.get("completion_allowed", False):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
