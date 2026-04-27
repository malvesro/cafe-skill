#!/usr/bin/env python3
"""
Helpers para padronizar artefatos em .ia/output no projeto aberto.
"""
import os
import tempfile


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, ".ia", "output")


def resolve_output_dir() -> str:
    """
    Resolve o diretório de saída para artefatos.

    Prioridade:
    1) RECEITA_CAFE_OUTPUT_DIR (quando explicitamente definido)
    2) <raiz-do-projeto>/.ia/output
    """
    output_dir = os.environ.get("RECEITA_CAFE_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=output_dir,
            prefix=".write_probe_",
            suffix=".tmp",
            delete=True,
            encoding="utf-8",
        ) as probe_file:
            probe_file.write("ok\n")
            probe_file.flush()
    except Exception as exc:
        raise PermissionError(
            f"Diretorio de output sem escrita: {output_dir}. "
            "Ajuste permissões ou defina RECEITA_CAFE_OUTPUT_DIR para um caminho gravável."
        ) from exc
    return output_dir
