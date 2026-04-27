#!/usr/bin/env python3
"""Smoke test do runtime completo da skill receita-cafe."""
import json
import os
import subprocess
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILL_DIR = os.path.join(ROOT, ".agents", "skills", "receita-cafe")
WRAPPER = os.path.join(SKILL_DIR, "scripts", "receita_completa.py")


def _load_manifest(stdout):
    marker = "[RUNTIME_MANIFEST]"
    if marker not in stdout:
        raise AssertionError("Manifesto de runtime nao foi impresso.")
    raw_manifest = stdout.split(marker, 1)[1].strip()
    return json.loads(raw_manifest)


def main():
    result = subprocess.run(
        [
            sys.executable,
            WRAPPER,
            "--cenario",
            "team_topologies",
            "--pessoas",
            "2",
            "--story",
            "Smoke test do runtime completo da skill receita-cafe.",
        ],
        cwd=SKILL_DIR,
        text=True,
        capture_output=True,
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")

    if result.returncode != 0:
        raise AssertionError(f"Runtime completo falhou com codigo {result.returncode}.")

    manifest = _load_manifest(result.stdout)
    if manifest["status"] != "pending_multimodal":
        raise AssertionError(f"Manifesto retornou status inesperado: {manifest['status']}")
    if manifest["deterministic_status"] != "ok":
        raise AssertionError("Runtime deterministico nao ficou OK.")
    if manifest["multimodal_status"] != "pending":
        raise AssertionError("Runtime multimodal deveria ficar pendente ate a imagem criativa ser gerada.")
    if manifest["completion_allowed"]:
        raise AssertionError("Conclusao nao deve ser permitida antes da imagem criativa.")
    if manifest["agent_next_action"] != "generate_creative_image_with_native_tool_then_run_finalizer":
        raise AssertionError("Proxima acao do agente deveria ser gerar imagem criativa e finalizar manifesto.")
    if not manifest["creative_image_required"]:
        raise AssertionError("Imagem criativa deveria estar marcada como obrigatoria.")
    if manifest["missing"]:
        raise AssertionError(f"Checks ausentes: {manifest['missing']}")

    artifacts = manifest["artifacts"]
    for key in (
        "manifest_path",
        "technical_infographic_path",
        "portable_markdown_path",
        "creative_prompt_path",
        "flow_trace_jsonl_path",
        "flow_trace_json_path",
        "flow_trace_html_path",
    ):
        path = artifacts[key]
        if not path or not os.path.exists(path):
            raise AssertionError(f"Artefato ausente: {key} -> {path}")
    if not artifacts["suggested_creative_image_path"].endswith(".png"):
        raise AssertionError("Path sugerido para imagem criativa deve ser PNG.")
    if artifacts["creative_image_path"] is not None:
        raise AssertionError("Imagem criativa nao deveria estar preenchida no smoke deterministico.")

    with open(artifacts["portable_markdown_path"], "r", encoding="utf-8") as md_file:
        markdown = md_file.read()
        if "data:image/png;base64" not in markdown:
            raise AssertionError("Markdown nao contem infografico embutido em Base64.")
        if "Telemetria da Execução" not in markdown:
            raise AssertionError("Markdown nao contem secao de telemetria.")

    for check in ("flow_trace_jsonl_exists", "flow_trace_json_exists", "flow_trace_html_exists", "markdown_links_flow_trace"):
        if not manifest["checks"].get(check):
            raise AssertionError(f"Check de telemetria ausente ou falso: {check}")

    with open(artifacts["flow_trace_json_path"], "r", encoding="utf-8") as trace_file:
        trace = json.load(trace_file)
    phases = {event["phase"] for event in trace["events"]}
    expected = {"orchestration", "deterministic_runtime", "artifact_generation", "creative_image_runtime", "manifest_finalization"}
    if not expected.issubset(phases):
        raise AssertionError(f"Fases esperadas ausentes no Flow Trace: {expected - phases}")

    print("Smoke test receita_completa: OK")


if __name__ == "__main__":
    raise SystemExit(main())
