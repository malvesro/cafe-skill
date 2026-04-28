# ☕ Projeto CAFE: Onde o Código encontra o Terroir
### *(A Demonstração Suprema do Poder das Agent Skills)*

> **"Não é apenas café. É Engenharia de Extração Assistida por IA."**  
> — *Algum Arquiteto Sênior antes de um Deploy às 17h.*

## 📐 Arquitetura Visual e Ciclo de Vida

Para compreender o fluxo de ponta a ponta desta skill, observe como o Agente orquestra cada componente.

### 1. Sequenciamento de Execução
O Agente não atua isolado. Ele utiliza o contrato `SKILL.md` como guia para invocar ferramentas determinísticas.

```mermaid
sequenceDiagram
    participant U as Usuário
    participant A as Agente IA
    participant C as Contract (SKILL.md)
    participant S as Scripts (Python)
    participant O as Outputs (.ia/output)
    participant F as Finalizer (finalizar_imagem_criativa.py)

    U->>A: Pedido (Ex: "Café para Deploy")
    A->>C: Consulta de Regras & Interface
    C-->>A: Parâmetros (Ratio, Terroir, Modo)
    A->>S: Execução via CLI (receita_completa.py)
    Note over S: Flow Tracer Ativado
    S->>S: Cálculo de Scaling & Terroir
    S->>S: Geração de UI (infografico_engine.py)
    S-->>O: Grava PNG/MD/Prompt/Flow Trace + Manifesto
    S-->>A: Retorna [RUNTIME_MANIFEST]
    alt status = pending_multimodal
        A->>A: Gera imagem criativa (tool nativa)
        A->>F: --manifest + --creative-image-path
        F-->>O: Atualiza manifesto + trace (creative_image_finalized)
        F-->>A: completion_allowed = true
    else status = ok
        A->>A: Entrega permitida imediatamente
    end
    A->>U: Resposta Final (somente com completion_allowed=true)
```

### 2. Lógica de Decisão e Auto-Scaling
O motor técnico (`validar_cafe.py`) opera como uma máquina de estados que valida o contexto antes da extração.

```mermaid
graph TD
    A[Início: Comando CLI] --> B{Possui Contexto?}
    B -- Não --> C[Indica Erro / Fallback]
    B -- Sim --> D[Mapear Terroir & Ratio]
    D --> E{Pessoas Definidas?}
    E -- Não --> F[Assumir 1 Pessoa]
    E -- Sim --> G[Escalar Volume e Insumos]
    G --> H[Acionar Flow Tracer]
    H --> I[Gerar Infográfico PNG]
    I --> J[Persistir Histórico JSON]
    J --> K[Gerar Markdown Portátil]
    K --> T[Validar Flow Trace Real]
    T --> U{flow_trace_real = true?}
    U -- Não --> V[Marcar failed + bloquear conclusão]
    U -- Sim --> M{Imagem criativa obrigatória?}
    M -- Não --> N[status ok + completion_allowed true]
    M -- Sim --> O[status pending_multimodal]
    O --> P{creative_image_path válido?}
    P -- Não --> Q[completion_allowed false + aguardar finalização]
    P -- Sim --> R[Finalizar manifesto multimodal]
    R --> N
    N --> L[Fim: Entrega permitida]

    style H fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#bbf,stroke:#333,stroke-width:2px
    style T fill:#ffd9b3,stroke:#333,stroke-width:2px
    style O fill:#ffe4e1,stroke:#333,stroke-width:2px
    style Q fill:#ffe4e1,stroke:#333,stroke-width:2px
```

### 🎓 Guia de Leitura Arquitetural (Para Desenvolvedores)

Se você é novo no projeto, aqui está como interpretar a nossa engenharia baseada nestes diagramas:

1.  **O Despachante (Agente IA):** Ele não "inventa" receitas. Ele atua como um gerente de projeto que lê o contrato (`SKILL.md`) e decide quais parâmetros passar para o motor técnico.
2.  **O Flow Tracer (Nó Rosa):** Este é o nosso diferencial didático. Quando ativo, ele obriga o código a revelar seu estado interno e quais arquivos estão sendo acessados. É o equivalente a um modo `DEBUG` que ensina enquanto executa. O caminho recomendado é `scripts/receita_completa.py`, que sempre aciona `--flow --imagem --markdown` e valida a entrega.
3.  **O Rendering Engine (Nó Azul):** Demonstra a separação de responsabilidades. O cálculo técnico é puramente lógico, enquanto a renderização do infográfico é delegada a um módulo especialista em UI.

---

## 🧠 O Cérebro Híbrido: Heurística (IA) vs. Determinismo (Script)

Uma dúvida comum em projetos de IA é: *"Quem realmente decide os parâmetros do café?"*. No padrão Agent Skills, utilizamos uma arquitetura de responsabilidade compartilhada.

| Atividade | Responsável | Tipo de Inteligência | Por que? |
| :--- | :--- | :--- | :--- |
| **Interpretação de Contexto** | Agente IA | **Heurística** (Criativa) | A IA identifica nuances no pedido humano (ex: tensão, deploy, cansaço). |
| **Mapeamento de Cenário** | Agente IA | **Contextual** (Lógica) | A IA escolhe o cenário (`incident`, `planning`) baseado no `SKILL.md`. |
| **Cálculo de Proporção (Ratio)** | Script Python | **Determinística** (Científica) | O código Python garante que a física da extração seja matematicamente correta. |
| **Validação Térmica (QA)** | Script Python | **Determinística** (Lógica) | O script impede que a temperatura fuja dos limites seguros para o grão. |
| **Narrativa e Storytelling** | Agente IA | **Criativa** (Narrativa) | A IA utiliza o `prompt_imagem_template.md` para criar a atmosfera da receita. |

> **Conclusão Didática:** A IA decide o **"O Quê"** e o **"Por Quê"** (Contexto), enquanto o Python garante o **"Como"** (Precisão Técnica). Isso evita alucinações técnicas e garante um café sempre perfeito.

---

## 🚀 Principais Inovações Técnicas (v4.1)

Bem-vindo ao **Projeto CAFE**! Este repositório nasceu para responder a uma pergunta fundamental da era da IA:  
*"Como transformamos um Agente de IA em um especialista técnico capaz de realizar ações reais, precisas e visuais?"*

A resposta? **[Agent Skills](https://agentskills.io/home)**.

Este projeto não é apenas um "gerador de receitas". É um **Proof of Concept (PoC)** de alta fidelidade que demonstra como estender as capacidades de uma IA de forma modular, segura e profissional.

---

## 🧠 A Estrela do Show: Skill `receita-cafe`

Nossa flagship skill, a `receita-cafe`, é o exemplo perfeito de como uma "Skill" deve ser estruturada. Ela não apenas dá conselhos; ela orquestra variáveis complexas de barismo e engenharia de software simultaneamente.

### ✨ Superpoderes da Skill:
*   **Auto-Scaling de Dose:** Precisa de café para uma pessoa ou para uma reunião de 15 líderes? A IA infere o volume e aplica o *Ratio* técnico correto.
*   **Runtime Previsível:** A skill valida dependências antes da renderização visual e falha rápido com instruções claras de instalação (sem auto-instalação em runtime).
*   **Observabilidade (Barista Analytics):** Um sistema de telemetria que rastreia o consumo por cenário e gera dashboards de estresse do time.
*   **Rastreabilidade Didática (Flow Tracer):** O fim da "caixa-preta". A skill detalha cada decisão técnica em tempo real, do contrato ao PNG.
*   **Output Multimodal:** Gera documentos Markdown portáteis e infográficos visuais de alto impacto prontos para apresentação.
*   **Runtime Canônico:** O wrapper `scripts/receita_completa.py` impede execução apenas conceitual, valida PNG/Markdown/telemetria e bloqueia conclusão prematura quando a fase criativa estiver pendente.
*   **Creative Image Runtime:** A imagem criativa é tratada como fase agent-native: o Agente usa o prompt gerado, salva o PNG em `.ia/output/imagem_criativa_[cenario]_[timestamp].png` e finaliza o manifesto com `scripts/finalizar_imagem_criativa.py`.
*   **Flow Trace UX:** Cada execução completa gera console em tempo real, `flow_trace_*.jsonl`, `flow_trace_*.json` e uma timeline HTML amigável para ensinar cada decisão, arquivo e artefato da skill.

---

## 🔡 Dicionário Técnico da Interface (`SKILL.md`)

Para que o Agente opere com precisão cirúrgica, ele utiliza a interface definida no contrato YAML. Abaixo, detalhamos cada parâmetro técnico para facilitar a sua compreensão do "Cérebro" da Skill:

### 📥 Parâmetros de Entrada (Input)

| Propriedade YAML | Tipo | Padrão (Default) | Descrição Didática |
| :--- | :--- | :--- | :--- |
| **`volume_ml`** | `integer` | *Obrigatório* | O volume de água total. Mínimo de 150ml (uma dose padrão). |
| **`regiao`** | `enum` | `generico` | A origem botânica. Define a **Matriz Termodinâmica** (Razão/Temperatura/Moagem). |
| **`cenario`** | `enum` | `planejamento` | O contexto do time. Influencia o **Storytelling** e o visual do infográfico. |
| **`intensidade`** | `enum` | `equilibrado` | Opções: `suave`, `equilibrado`, `intenso`. Ajusta the ratio para mais ou menos corpo. |
| **`num_pessoas`** | `integer` | `1` | O multiplicador de escala. Aciona a **Engine de Auto-Scaling** de insumos. |
| **`moagem_ajustavel`** | `boolean` | `true` | Permite que o sistema sugira correções baseadas em sintomas de extração. |
| **`dashboard`** | `boolean` | `false` | Se `true`, invoca a a engine de **Barista Analytics** em vez de uma receita. |
| **`flow`** | `boolean` | **`true`** | **O Modo Didático.** Exibe a rastreabilidade passo a passo. Mantido ativo para fins educativos. |

### 📤 Estrutura de Saída (Output)

O sistema não entrega apenas texto, ele entrega um **Objeto de Conhecimento**:
*   **`parametros_finais`**: O JSON calculado com as gramas exatas de café e temperatura.
*   **`alerta_qa`**: Um array de strings com avisos técnicos (ex: dependência de água mineral, alerta térmico).
*   **`image_path`**: O caminho absoluto para o arquivo PNG do infográfico gerado na pasta `.ia/output`.

---

## 🏗️ Por que "Agent Skills"?

As Agent Skills representam uma mudança de paradigma. Em vez de prompts soltos, temos:
1.  **Contratos Claros (`SKILL.md`):** O Agente sabe exatamente o que pode e o que não pode fazer.
2.  **Lógica Isolada (`scripts/`):** O código técnico é separado da conversação.
3.  **Memória e Persistência (`data/`):** O Agente aprende com o histórico.
4.  **Storytelling Visual:** Integração com IAs gerativas para criar cenas narrativas que conectam o café ao seu momento de dev (Deploy, War Room, Planning).

---

## 📖 Mergulhe na Documentação Técnica

Se você é um desenvolvedor, arquiteto ou um entusiasta de automação, o verdadeiro "ouro" está nos detalhes. Confira a especificação completa da nossa skill principal:

👉 **[Documentação Técnica: Skill Receita-Café](.agents/skills/receita-cafe/README.md)**

---

## 🎭 Storytelling: A Jornada do Barista-Dev

Neste projeto, tratamos cada xícara como um **Release Note**.
*   Um bug em produção? Ativamos o **Modo War Room** (Cerrado Intenso).
*   Um alinhamento de times? Ativamos o **Modo Team Topologies** (Chapada Diamantina).
*   Um deploy de sucesso? É hora do **Modo Launch** (Sul de Minas Frutado).

Aqui, a cafeína é o combustível e as **Agent Skills** são o motor que garante que cada gota seja extraída com precisão de microssegundos.

---

## 🛠️ Como rodar a demonstração?

### Comece por Intenção (Guia Rápido)
Use este atalho para escolher o melhor caminho sem precisar decorar parâmetros:

| Sua intenção | Caminho recomendado | Exemplo |
| :--- | :--- | :--- |
| Quero só uma sugestão no chat | Prompt natural para o agente | `"Sugira um café para reunião de arquitetura com 6 pessoas."` |
| Quero entrega completa com rastreabilidade | `receita_completa.py` (recomendado) | `python3 scripts/receita_completa.py --cenario planning --pessoas 6` |
| Quero testar cálculo técnico isolado | `validar_cafe.py` | `python3 scripts/validar_cafe.py --cenario debugging --pessoas 2 --flow --imagem --markdown` |
| Quero fechar multimodal pendente | `finalizar_imagem_criativa.py` | `python3 scripts/finalizar_imagem_criativa.py --manifest <manifesto> --creative-image-path <png>` |

Regra prática:
1. Use `receita_completa.py` como padrão para execução fim a fim.
2. Use `validar_cafe.py` quando o foco for apenas cálculo/artefato técnico.
3. Só finalize resposta ao usuário quando o manifesto tiver `completion_allowed=true`.

Referência detalhada:
1. Parâmetros e defaults: `.agents/skills/receita-cafe/README.md` na seção `Parâmetros Canônicos (CLI)`.
2. Prompt -> parâmetros: seção `Matriz Didática: Tipo de Pedido -> Parâmetros Efetivos`.
3. Decisão final por manifesto: seção `Como Ler o Manifesto (Guia Rápido)`.

Se você já tem o Agente configurado, basta um pedido simples e natural para ver a magia acontecer:

> *"Barista, preciso de um café intenso para uma **War Room de incidente crítico** com 8 pessoas!"*

*(O Agente entenderá automaticamente que deve escalar a receita para o grupo, aplicar os parâmetros de resiliência e executar o runtime completo com **Flow Tracer**, PNG técnico, Markdown portátil, prompt criativo rastreável e manifesto de runtime).*

Execução direta recomendada:

```bash
cd .agents/skills/receita-cafe
python3 scripts/receita_completa.py --cenario incident --pessoas 8
```

Ao final, o wrapper imprime e persiste um manifesto JSON (`[RUNTIME_MANIFEST]`) com os caminhos finais e os checks da Definition of Done, incluindo os caminhos de telemetria `flow_trace_*.jsonl`, `flow_trace_*.json` e `flow_trace_*.html` em `.ia/output`. Se `creative_image_required` for `true`, o wrapper retorna `status: "pending_multimodal"` e `completion_allowed: false` (com exit code diferente de zero); o Agente deve gerar a imagem criativa, copiá-la para `suggested_creative_image_path` e finalizar o manifesto antes de considerar a entrega multimodal concluída.

### Telemetria no Chat (UX)
Além do Flow Trace técnico, o orquestrador agora emite telemetria amigável no chat para reduzir ambiguidade de estado durante a execução.

Formato padrão (friendly, sem colchetes):

`Info: Preparação | Orquestrador | Iniciar | Mensagem... (run_id=..., seq=...)`

Exemplos reais:

- `Info: Preparação | Orquestrador | Iniciar | Inicializando execução canônica da skill. (run_id=..., seq=1)`
- `Info: Empacotamento de artefatos | Rastro_execucao | Validar | Rastro de execução real validado=sim. (run_id=..., seq=9)`
- `Aviso: Fechamento multimodal | Portao | Decidir | estado=pending_multimodal, conclusao_permitida=False, motivo=creative_image_pending, próximo_passo=gerar imagem criativa PNG e finalizar manifesto. (run_id=..., seq=12)`
- `Info: Resposta final | Orquestrador | Concluir | Resposta final liberada (status=ok). (run_id=..., seq=16)`

Formato técnico opcional (com colchetes):
- Ative com `--chat-telemetry-style technical` quando quiser depuração detalhada no próprio chat.

---
*Este projeto foi criado para inspirar. Se você achava que Agentes de IA eram apenas sobre texto, pegue uma xícara de café e explore o código. O futuro é modular.* 🚀☕

---
*Desenvolvido seguindo os padrões de [AgentSkills.io](https://agentskills.io/specification)*
