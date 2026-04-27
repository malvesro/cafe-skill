#!/usr/bin/env python3
"""Flow Trace engine for receita-cafe.

The trace is mandatory for this skill: JSONL for real-time append, JSON for
automation, and HTML for a friendly execution timeline.
"""
import html
import json
import os
from datetime import datetime


def utcish_now():
    return datetime.now().isoformat(timespec="seconds")


def event(phase, step_id, title, status="ok", decision=None, inputs=None,
          files_read=None, files_written=None, artifacts=None):
    return {
        "timestamp": utcish_now(),
        "phase": phase,
        "step_id": step_id,
        "title": title,
        "status": status,
        "decision": decision,
        "inputs": inputs or {},
        "files_read": files_read or [],
        "files_written": files_written or [],
        "artifacts": artifacts or [],
    }


def append_jsonl(path, item):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as trace_file:
        trace_file.write(json.dumps(item, ensure_ascii=False))
        trace_file.write("\n")


def load_jsonl(path):
    if not path or not os.path.exists(path):
        return []
    events = []
    with open(path, "r", encoding="utf-8") as trace_file:
        for line in trace_file:
            stripped = line.strip()
            if stripped:
                events.append(json.loads(stripped))
    return events


def write_json(path, events, metadata):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "metadata": metadata,
        "events": events,
    }
    with open(path, "w", encoding="utf-8") as trace_file:
        json.dump(payload, trace_file, indent=2, ensure_ascii=False)
        trace_file.write("\n")


def _list_items(items):
    if not items:
        return "<span class='muted'>nenhum</span>"
    return "<ul>" + "".join(f"<li>{html.escape(str(item))}</li>" for item in items) + "</ul>"


def _dict_items(items):
    if not items:
        return "<span class='muted'>nenhum</span>"
    rows = []
    for key, value in items.items():
        rows.append(
            "<tr>"
            f"<th>{html.escape(str(key))}</th>"
            f"<td>{html.escape(json.dumps(value, ensure_ascii=False))}</td>"
            "</tr>"
        )
    return "<table>" + "".join(rows) + "</table>"


def write_html(path, events, metadata):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    title = f"Execution Trace - receita-cafe - {metadata.get('cenario', 'generico')}"
    cards = []
    for index, item in enumerate(events, start=1):
        status = html.escape(str(item.get("status", "ok")))
        decision = item.get("decision") or "Sem decisao registrada."
        cards.append(
            "<article class='event'>"
            f"<div class='marker'>{index:02d}</div>"
            "<div class='content'>"
            f"<div class='eyebrow'>{html.escape(str(item.get('phase', 'runtime')))} "
            f"<span class='badge {status}'>{status}</span></div>"
            f"<h2>{html.escape(str(item.get('title', 'Evento')))}</h2>"
            f"<p>{html.escape(str(decision))}</p>"
            "<details open><summary>Entradas</summary>"
            f"{_dict_items(item.get('inputs', {}))}</details>"
            "<details><summary>Arquivos lidos</summary>"
            f"{_list_items(item.get('files_read', []))}</details>"
            "<details><summary>Arquivos escritos</summary>"
            f"{_list_items(item.get('files_written', []))}</details>"
            "<details><summary>Artefatos</summary>"
            f"{_list_items(item.get('artifacts', []))}</details>"
            f"<div class='time'>{html.escape(str(item.get('timestamp', '')))}</div>"
            "</div>"
            "</article>"
        )

    summary = "".join(
        f"<li><strong>{html.escape(str(k))}</strong>: {html.escape(str(v))}</li>"
        for k, v in metadata.items()
    )
    document = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: light; --ink:#1f2933; --muted:#6b7280; --line:#d7dee8; --ok:#0f766e; --pending:#b45309; --failed:#b91c1c; --bg:#f7f8fb; --card:#ffffff; }}
    body {{ margin:0; font:15px/1.45 system-ui, -apple-system, Segoe UI, sans-serif; color:var(--ink); background:var(--bg); }}
    header {{ padding:32px min(6vw,64px) 18px; background:#ffffff; border-bottom:1px solid var(--line); }}
    h1 {{ margin:0 0 8px; font-size:28px; letter-spacing:0; }}
    .subtitle {{ color:var(--muted); margin:0; }}
    main {{ max-width:1120px; margin:0 auto; padding:24px; }}
    .summary {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:8px 18px; padding:16px 20px; background:var(--card); border:1px solid var(--line); border-radius:8px; }}
    .summary li {{ list-style:none; overflow-wrap:anywhere; }}
    .timeline {{ position:relative; margin-top:24px; }}
    .event {{ display:grid; grid-template-columns:48px 1fr; gap:14px; margin-bottom:16px; }}
    .marker {{ width:40px; height:40px; border-radius:999px; display:grid; place-items:center; background:#111827; color:white; font-weight:700; }}
    .content {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:16px 18px; box-shadow:0 1px 2px rgba(15,23,42,.05); }}
    .eyebrow {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em; display:flex; gap:8px; align-items:center; }}
    h2 {{ margin:6px 0 8px; font-size:18px; letter-spacing:0; }}
    p {{ margin:0 0 12px; }}
    details {{ border-top:1px solid var(--line); padding-top:8px; margin-top:8px; }}
    summary {{ cursor:pointer; font-weight:600; }}
    table {{ border-collapse:collapse; width:100%; margin-top:8px; }}
    th, td {{ text-align:left; vertical-align:top; border-bottom:1px solid #eef2f7; padding:6px 8px; overflow-wrap:anywhere; }}
    th {{ width:180px; color:var(--muted); }}
    ul {{ margin:8px 0 0 18px; padding:0; }}
    li {{ overflow-wrap:anywhere; }}
    .badge {{ border-radius:999px; padding:2px 8px; color:white; text-transform:none; letter-spacing:0; }}
    .badge.ok {{ background:var(--ok); }}
    .badge.pending, .badge.pending_multimodal {{ background:var(--pending); }}
    .badge.failed, .badge.blocked {{ background:var(--failed); }}
    .muted, .time {{ color:var(--muted); }}
    .time {{ font-size:12px; margin-top:12px; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p class="subtitle">Telemetria didatica obrigatoria da execucao da skill.</p>
  </header>
  <main>
    <ul class="summary">{summary}</ul>
    <section class="timeline">{''.join(cards)}</section>
  </main>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as trace_file:
        trace_file.write(document)


def write_artifacts(output_dir, cenario, run_id, events, metadata):
    jsonl_path = os.path.abspath(os.path.join(output_dir, f"flow_trace_{cenario}_{run_id}.jsonl"))
    json_path = os.path.abspath(os.path.join(output_dir, f"flow_trace_{cenario}_{run_id}.json"))
    html_path = os.path.abspath(os.path.join(output_dir, f"flow_trace_{cenario}_{run_id}.html"))
    write_json(json_path, events, metadata)
    write_html(html_path, events, metadata)
    return {
        "flow_trace_jsonl_path": jsonl_path,
        "flow_trace_json_path": json_path,
        "flow_trace_html_path": html_path,
    }
