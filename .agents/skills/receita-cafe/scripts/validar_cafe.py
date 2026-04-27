#!/usr/bin/env python3
"""
validar_cafe.py — Engine de validação harmonizada (Didática + Técnica).
"""
import sys
import os
import argparse
import json
import subprocess
import shutil
import base64
from datetime import datetime
from output_paths import resolve_output_dir

# Lógica de Negócio (Sync com SKILL.md v2.1)
TERROIRS = {
    "mogiana": {"ratio": 1/12, "temp": 92, "moagem": "Média-Fina", "notas": "Doçura, Chocolate, Acidez Baixa"},
    "cerrado": {"ratio": 1/15, "temp": 94, "moagem": "Média", "notas": "Nozes, Caramelo, Corpo Marcante"},
    "sul_de_minas": {"ratio": 1/14, "temp": 90, "moagem": "Média-Grossa", "notas": "Frutas Amarelas, Acidez Cítrica"},
    "espirito_santo": {"ratio": 1/13, "temp": 91, "moagem": "Média", "notas": "Especiarias, Chocolate Amargo"},
    "mantiqueira": {"ratio": 1/12, "temp": 92, "moagem": "Média-Fina", "notas": "Aroma Marcante, Frutado, Notas de Nozes"},
    "chapada_diamantina": {"ratio": 1/14, "temp": 93, "moagem": "Média", "notas": "Aveludado, Cítrico, Final Prolongado"},
    "matas_de_minas": {"ratio": 1/13, "temp": 91, "moagem": "Média", "notas": "Doçura Notável, Caramelo, Chocolate"},
    "alta_mogiana": {"ratio": 1/12, "temp": 92, "moagem": "Média-Fina", "notas": "Corpo Encorpado, Acidez Média, Frutado"},
    "amazonico": {"ratio": 1/11, "temp": 94, "moagem": "Grossa", "notas": "Intenso, Amadeirado, Alta Cafeína"},
    "generico": {"ratio": 1/15, "temp": 93, "moagem": "Média", "notas": "Equilibrado"}
}

CENARIOS = {
    "planning": {
        "regiao": "mogiana", 
        "insight": "Sprint Planning: Estimativas que nunca atrasam (nos primeiros 5 minutos).",
        "humor": "A doçura ajuda a aceitar aquele card que 'é só uma alteraçãozinha'."
    },
    "debugging": {
        "regiao": "cerrado", 
        "insight": "Debugging: Se o bug for um NullPointerException, este café é o único objeto não nulo.",
        "humor": "Intenso e resiliente, como o dev que não desiste do breakpoint."
    },
    "deploy": {
        "regiao": "sul_de_minas", 
        "insight": "Deploy: Digno de um pipeline que passou de primeira. Notas complexas para código estável.",
        "humor": "Acidez vibrante para te manter alerta enquanto os logs de produção estabilizam."
    },
    "code_review": {
        "regiao": "espirito_santo", 
        "insight": "Code Review: Limpo e transparente. Ideal para ver aquele code smell escondido.",
        "humor": "Um café com 'clean code' garantido pelo terroir."
    },
    "scrum": {
        "regiao": "mantiqueira",
        "insight": "Scrum Rituals: Equilíbrio e cadência. Ideal para Daily e Retrospectiva.",
        "humor": "Corpo aveludado para suavizar os feedbacks da retrospectiva."
    },
    "team_topologies": {
        "regiao": "chapada_diamantina",
        "insight": "Team Topologies: Estruturando fluxos e domínios. Notas cítricas para clareza de fronteiras.",
        "humor": "O café ideal para alinhar Cognitive Load com a arquitetura do time."
    },
    "architecture": {
        "regiao": "matas_de_minas",
        "insight": "Software Architecture: Complexidade e visão de alto nível. Notas encorpadas e complexas.",
        "humor": "Tão bem estruturado quanto um diagrama C4 de nível 3."
    },
    "security": {
        "regiao": "amazonico",
        "insight": "Security/InfoSec: Alerta máximo. Robusta para garantir resiliência e foco total.",
        "humor": "Mais cafeína que uma sessão de pentest de madrugada."
    },
    "refactoring": {
        "regiao": "alta_mogiana",
        "insight": "Refactoring: Limpeza e otimização. Doçura alta para tornar o legado suportável.",
        "humor": "Removendo technical debt e adicionando aroma achocolatado."
    },
    "incident": {
        "regiao": "amazonico",
        "insight": "Incident Management: War Room. Café potente para restaurar o serviço em tempo recorde.",
        "humor": "O SLA de 99.9% de disponibilidade começa nesta xícara."
    },
    "documentation": {
        "regiao": "generico", 
        "insight": "Documentation: Volume alto e extração lenta. Perfeito para o README procrastinado.",
        "humor": "O café ideal para quando o único bug é a falta de comentários no código."
    }
}

OUTPUT_DIR = resolve_output_dir()
HISTORY_FILE = os.path.join(OUTPUT_DIR, "history.json")

def check_dependencies():
    """Valida dependências necessárias (Pillow) sem auto-instalação em runtime."""
    try:
        from PIL import Image  # noqa: F401
        return True
    except ImportError:
        print("❌ Dependência ausente: Pillow (PIL).")
        print("Instale previamente no ambiente, por exemplo:")
        print("  - Ubuntu/Debian: sudo apt install python3-pil")
        print("  - venv local: pip install Pillow")
        return False

def registrar_historico(params):
    """Persiste a extração no histórico em formato JSON."""
    history_file = HISTORY_FILE
    os.makedirs(os.path.dirname(history_file), exist_ok=True)

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cenario": params["cenario"],
        "regiao": params["regiao"],
        "volume_ml": params["volume_ml"],
        "cafe_g": params["cafe_g"],
        "pessoas": params["num_pessoas"]
    }
    
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                content = f.read()
                if content:
                    history = json.loads(content)
        except Exception:
            history = []
            
    history.append(entry)
    
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

def gerar_dashboard(flow=False):
    """Aciona o motor de analytics para gerar o infográfico de histórico."""
    try:
        engine_dir = os.path.dirname(__file__)
        sys.path.insert(0, engine_dir)
        from analytics_engine import processar_dashboard
        img_path = processar_dashboard(flow=flow)
        print(f"\n📊 Barista Analytics: {img_path}")
    except Exception as e:
        print(f"❌ Erro ao gerar dashboard: {e}")

def diagnosticar_extração(tempo_seg):
    if tempo_seg < 180:
        return "⚠️ Fluxo muito rápido. Sugestão: Use uma moagem mais FINA para aumentar a resistência."
    if tempo_seg > 270:
        return "⚠️ Fluxo muito lento. Sugestão: Use uma moagem mais GROSSA para facilitar a passagem."
    return "✅ Tempo de extração perfeito."

def emit_flow_event(step, description, files=None):
    """Persiste evento JSONL obrigatorio quando o wrapper define o destino."""
    trace_path = os.environ.get("RECEITA_CAFE_FLOW_JSONL")
    if not trace_path:
        return
    try:
        engine_dir = os.path.dirname(__file__)
        sys.path.insert(0, engine_dir)
        from flow_trace_engine import append_jsonl, event

        append_jsonl(trace_path, event(
            phase="deterministic_runtime",
            step_id=step.lower().replace(" ", "_"),
            title=step,
            status="ok",
            decision=description,
            files_read=files or [],
        ))
    except Exception as exc:
        print(f"⚠️  Erro ao registrar Flow Trace estruturado: {exc}")

def log_flow(step, description, files=None):
    """Exibe o fluxo de execução de forma didática."""
    print(f"\n[FLOW] 🛤️ {step.upper()}")
    print(f"       └─ {description}")
    if files:
        print(f"       📂 Recursos: {', '.join(files)}")
    emit_flow_event(step, description, files)

def gerar_prompt_imagem(params):
    """Gera o prompt de imagem usando o template de .agents/prompt_imagem_template.md"""
    cenario = params.get("cenario", "generico")
    regiao = params.get("regiao", "generico")
    notas = params.get("notas", "café especial")
    pessoas = params.get("num_pessoas", 1)
    
    # Mapeamento de variáveis conforme prompt_imagem_template.md
    variaveis = {
        "planning": {
            "ESTILO_XICARA": "xícara de vidro transparente (clareza)",
            "ESTILO_LUZ": "luz natural quente da manhã",
            "ELEMENTO_HUMOR": "post-its coloridos com histórias de usuário",
            "SIMBOLO_GEEK": "um colchete [ ]",
            "CENARIO_DEV": "sprint planning com quadro Kanban"
        },
        "debugging": {
            "ESTILO_XICARA": "caneca robusta de cerâmica",
            "ESTILO_LUZ": "luz azulada de monitores com sombras dramáticas",
            "ELEMENTO_HUMOR": "um patinho de borracha (Rubber Duck Debugging)",
            "SIMBOLO_GEEK": "um terminal com código",
            "CENARIO_DEV": "war room de debugging com múltiplos monitores"
        },
        "deploy": {
            "ESTILO_XICARA": "caneca de cerâmica robusta e fosca",
            "ESTILO_LUZ": "luz de neon verde (pipeline success)",
            "ELEMENTO_HUMOR": "um post-it escrito 'PIPELINE GREEN'",
            "SIMBOLO_GEEK": "um foguete decolando",
            "CENARIO_DEV": "sala de deploy com telas mostrando logs"
        },
        "scrum": {
            "ESTILO_XICARA": "xícara de porcelana minimalista",
            "ESTILO_LUZ": "luz natural suave",
            "ELEMENTO_HUMOR": "quadro com post-its coloridos",
            "SIMBOLO_GEEK": "um checkmark",
            "CENARIO_DEV": "daily standup meeting"
        },
        "incident": {
            "ESTILO_XICARA": "caneca de cerâmica robusta",
            "ESTILO_LUZ": "luz azulada de monitores com sombras dramáticas",
            "ELEMENTO_HUMOR": "um patinho de borracha",
            "SIMBOLO_GEEK": "um gráfico de métricas subindo",
            "CENARIO_DEV": "war room de incident com dashboards"
        },
        "code_review": {
            "ESTILO_XICARA": "xícara de vidro transparente",
            "ESTILO_LUZ": "luz suave de escritório",
            "ELEMENTO_HUMOR": "um teclado mecânico",
            "SIMBOLO_GEEK": "um pull request merge",
            "CENARIO_DEV": "code review em tela grande"
        },
        "architecture": {
            "ESTILO_XICARA": "xícara de porcelana minimalista",
            "ESTILO_LUZ": "luz suave e organizada",
            "ELEMENTO_HUMOR": "um diagrama C4",
            "SIMBOLO_GEEK": "uma engrenagem",
            "CENARIO_DEV": "sessão de arquitetura com whiteboard"
        },
        "security": {
            "ESTILO_XICARA": "caneca preta fosca",
            "ESTILO_LUZ": "luz azulada de terminal",
            "ELEMENTO_HUMOR": "um escudo",
            "SIMBOLO_GEEK": "um cadeado",
            "CENARIO_DEV": "análise de segurança"
        },
        "refactoring": {
            "ESTILO_XICARA": "xícara de cerâmica moderna",
            "ESTILO_LUZ": "luz suave e organizada",
            "ELEMENTO_HUMOR": "código limpo e organizado",
            "SIMBOLO_GEEK": "uma chave { }",
            "CENARIO_DEV": "refatoração de código"
        },
        "team_topologies": {
            "ESTILO_XICARA": "xícara de vidro",
            "ESTILO_LUZ": "luz moderna",
            "ELEMENTO_HUMOR": "nós conectados representando times",
            "SIMBOLO_GEEK": "um grafo de conexões",
            "CENARIO_DEV": "mapeamento de team topologies"
        },
        "documentation": {
            "ESTILO_XICARA": "caneca clássica",
            "ESTILO_LUZ": "luz suave de leitura",
            "ELEMENTO_HUMOR": "um teclado mecânico clássico",
            "SIMBOLO_GEEK": "um documento Markdown",
            "CENARIO_DEV": "escrita de documentação"
        }
    }
    
    # Pegar variáveis do cenário ou usar defaults
    vars_cenario = variaveis.get(cenario, variaveis["planning"])
    
    # Gerar o prompt conforme template
    prompt = f"""Uma fotografia cinematográfica de alta resolução de uma xícara de café especial preparada na hora, servida em uma {vars_cenario['ESTILO_XICARA']}. O café é um {regiao.capitalize()} com notas de {notas}. Ao fundo, um ambiente de {vars_cenario['CENARIO_DEV']} com iluminação {vars_cenario['ESTILO_LUZ']}. É possível ver {vars_cenario['ELEMENTO_HUMOR']} próximo à xícara. Vapor sutil sobe do café, formando levemente o contorno de {vars_cenario['SIMBOLO_GEEK']}. Estilo visual premium, 8k, profundidade de campo rasa, focado na textura do café."""
    
    return prompt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ml", type=int, help="Volume de água")
    parser.add_argument("--gramas", type=float, help="Peso do café")
    parser.add_argument("--temp", type=int, help="Temperatura")
    parser.add_argument("--tempo", type=int, help="Tempo total em segundos")
    parser.add_argument("--regiao", type=str)
    parser.add_argument("--cenario", type=str, choices=CENARIOS.keys())
    parser.add_argument("--tds_agua", type=int, help="TDS da água (ppm)")
    parser.add_argument("--json", action="store_true", help="Saída em formato JSON")
    parser.add_argument("--imagem", action="store_true", help="Gera infográfico PNG da extracão")
    parser.add_argument("--markdown", action="store_true", help="Gera documento Markdown portátil (.md) com imagem embutida")
    parser.add_argument("--story", type=str, help="Texto de storytelling/contexto rico para o documento.")
    parser.add_argument("--pessoas", type=int, default=1, help="Número de pessoas que serão servidas.")
    parser.add_argument("--dashboard", action="store_true", help="Gera o infográfico de Analytics (Barista Histórico).")
    parser.add_argument("--flow", action="store_true", default=True, help="Habilita o modo de rastreabilidade passo a passo (Padrão: Ativo).")
    parser.add_argument("--artifacts-json", action="store_true", help="Emite JSON estruturado com artefatos ao final.")
    args = parser.parse_args()

    if args.flow:
        log_flow("Início da Skill", "O Agente foi invocado e está inicializando a Engine de Extração.", ["validar_cafe.py", "SKILL.md"])

    if args.dashboard:
        if args.flow: log_flow("Módulo Analytics", "Acessando banco de dados de consumo para gerar dashboard.", ["data/history.json", "analytics_engine.py"])
        gerar_dashboard(flow=args.flow)
        return

    # Cenários de reunião que requerem inferência de pessoas
    CENARIOS_REUNIAO = ["planning", "scrum", "team_topologies", "debugging", "code_review", "architecture"]
    
    # Lógica de Inferência (SKILL.md item 2.2)
    # Se cenário é reunião e pessoas não foi explicitado, inferir do volume
    if args.cenario in CENARIOS_REUNIAO and args.pessoas == 1 and args.ml:
        pessoas_inferidas = round(args.ml / 150)
        if pessoas_inferidas > 1:
            args.pessoas = pessoas_inferidas
            if args.flow: 
                log_flow("Inferência de Pessoas", f"Cenário de reunião detectado. Inferindo {pessoas_inferidas} pessoas (150ml/pessoa).", [])

    # Lógica de cenário sobrepõe região se fornecido
    res_regiao = args.regiao or "generico"
    insight, humor = "", ""
    
    if args.cenario:
        if args.flow: log_flow("Análise de Contexto", f"Mapeando o cenário '{args.cenario}' para um perfil sensorial específico.")
        conf = CENARIOS[args.cenario]
        res_regiao = conf["regiao"]
        insight = conf["insight"]
        humor = conf["humor"]

    config = TERROIRS.get(res_regiao.lower(), TERROIRS["generico"])
    if args.flow: log_flow("Cálculo de Extração", f"Aplicando Ratio técnico 1:{int(1/config['ratio'])} para a região {res_regiao}.")
    alerts = []

    # Lógica de Inferência de Volume por Pessoas
    volume_final = args.ml
    if not volume_final and args.pessoas:
        if args.flow: log_flow("Inferência de Volume", f"Calculando volume base de 150ml p/ {args.pessoas} pessoa(s).")
        volume_final = args.pessoas * 150

    # Alerta Químico de Água
    if args.tds_agua:
        if args.tds_agua < 50: alerts.append("Água muito pura (mole). Café pode ficar sem corpo.")
        if args.tds_agua > 200: alerts.append("Água muito dura (mineralizada). Pode gerar amargor excessivo.")

    # Diagnóstico de Tempo
    if args.tempo:
        alerts.append(diagnosticar_extração(args.tempo))

    # Cálculo de Parâmetros
    params = {
        "cenario": args.cenario or "generico",
        "regiao": res_regiao,
        "cafe_g": round(volume_final * config["ratio"], 1) if volume_final else 0,
        "volume_ml": volume_final or 0,
        "num_pessoas": args.pessoas,
        "temp_alvo": config["temp"],
        "moagem_ideal": config["moagem"],
        "notas": config["notas"],
        "insight_dev": insight,
        "humor_barista": humor,
        "story": args.story,
        "avisos_barista": alerts
    }

    if args.json:
        print(json.dumps(params, indent=2, ensure_ascii=False))
    else:
        if args.flow: log_flow("Persistência de Dados", "Registrando a extração no histórico de consumo do time.", [HISTORY_FILE])
        registrar_historico(params)
        title = f" [BARISTA ENGINE] Sugestão p/ {params['cenario'].upper()}"
        print(f"\n{title}")
        print(f"─" * 45)
        if insight: print(f"💡 {insight}")
        if humor: print(f"🎭 {humor}")
        print(f"─" * 45)
        print(f"Café: {params['cafe_g']}g | Água: {params['volume_ml']}ml")
        print(f"Rendimento: {params['num_pessoas']} pessoa(s) | Moagem: {params['moagem_ideal']}")
        print(f"Temperatura: {params['temp_alvo']}°C")
        if alerts:
            print("\n📋 ALERTAS DO SISTEMA:")
            for a in alerts: print(f"  {a}")
        print(f"─" * 45)

    # → Geração de infográfico visual (Iteracão 3)
    img_path = None
    if args.imagem:
        if args.flow: log_flow("Renderização Visual", "Invocando engine gráfica para gerar infográfico da receita.", ["infografico_engine.py", "assets/"])
        if not check_dependencies():
            raise SystemExit(2)
        try:
            engine_dir = os.path.join(os.path.dirname(__file__))
            sys.path.insert(0, engine_dir)
            from infografico_engine import gerar_infografico
            img_path = gerar_infografico(params, flow=args.flow)
            print(f"\n🖼️  Infográfico gerado: {img_path}")
        except Exception as e:
            print(f"⚠️  Erro ao gerar imagem: {e}")

    # → Geração de Prompt para Imagem Criativa (usando template prompt_imagem_template.md)
    # O modelo de IA pode usar este prompt para gerar a imagem criativa do cenário
    prompt_criativo = gerar_prompt_imagem(params)
    print(f"\n🎨 PROMPT PARA IMAGEM CRIATIVA (use com ferramenta de geração de imagens):")
    print(f"─" * 60)
    print(prompt_criativo)
    print(f"─" * 60)
    if args.flow:
        log_flow("Imagem Criativa", "Prompt gerado conforme template. O modelo de IA deve renderizar usando capacidade nativa.", [".agents/prompt_imagem_template.md"])

    # → Geração de Documento Markdown Portátil (Estratégia Sênior)
    if args.markdown and img_path:
        if args.flow: 
            log_flow("Storytelling Strategy", "Consolidando regras narrativas para geração do contexto visual.", [".agents/prompt_imagem_template.md"])
            log_flow("Empacotamento", "Gerando documento Markdown portátil com imagem embutida em Base64.", [OUTPUT_DIR])
        try:
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            md_filename = f"receita_{params['cenario']}_{timestamp}.md"
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            md_path = os.path.join(OUTPUT_DIR, md_filename)
            
            md_content = f"""# ☕ Protocolo de Café Especial: {params['cenario'].replace('_', ' ').capitalize()}
            
Este documento é uma extensão da inteligência do seu Agente, gerado de forma **autocontida** para levar a experiência do café perfeito para qualquer lugar.

## 🎬 Contexto e Storytelling
{params['story'] if params['story'] else f"{insight}\n\n*{humor}*"}

---

## 🧪 Engenharia de Extração
Aqui estão os parâmetros técnicos calculados para garantir a máxima performance sensorial:

- **Região Selecionada:** {params['regiao'].capitalize()}
- **Perfil Sensorial:** {params['notas']}
- **Receita:** {params['cafe_g']}g de café para {params['volume_ml']}ml de água
- **Rendimento:** {params['num_pessoas']} pessoa(s) (aprox. 150ml p/ pessoa)
- **Temperatura da Água:** {params['temp_alvo']}°C
- **Moagem Sugerida:** {params['moagem_ideal']}

## 📋 Protocolo de Execução (The Golden Path)
1. **Setup Térmico:** Aquecer a água ao alvo ({params['temp_alvo']}°C) e escaldar o filtro de papel para remover resíduos de celulose.
2. **Pré-Infusão (Blooming):** Adicionar {round(params['cafe_g']*2, 1)}ml de água e aguardar 30 segundos. Sinta os gases saindo e preparando o pó.
3. **Extração Primária:** Despejar lentamente 40% da água ({round(params['volume_ml']*0.4, 1)}ml) em movimentos circulares do centro para as bordas.
4. **Finalização:** Adicionar o restante da água e aguardar a drenagem total. Tempo alvo: **3:30 - 4:00 min**.

---

## 🖼️ Infográfico Técnico (Embedded)
![Infográfico](data:image/png;base64,{encoded_string})

---
*Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write(md_content)
            print(f"📄 Documento Markdown portátil gerado: {os.path.abspath(md_path)}")
        except Exception as e:
            print(f"⚠️  Erro ao gerar Markdown: {e}")

    if args.artifacts_json:
        print("\n[ARTIFACTS_JSON]")
        print(json.dumps({
            "technical_infographic_path": os.path.abspath(img_path) if img_path else None,
            "portable_markdown_path": os.path.abspath(md_path) if 'md_path' in locals() and md_path else None,
            "creative_prompt_text": prompt_criativo,
            "params": params,
        }, ensure_ascii=False))

if __name__ == "__main__":
    main()
