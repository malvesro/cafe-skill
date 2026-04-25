# 📖 Guia de Uso: Advanced Brazilian Coffee Engine (v3.1.0)

Esta skill orquestra o preparo de cafés especiais brasileiros, unindo a ciência da extração com a arte do barismo.

## 📥 Pré-requisitos & Instalação

Para que o motor visual e os cálculos técnicos funcionem corretamente, sua estação de trabalho (ou o ambiente do Agente) precisa:

1.  **Python 3.8+** instalado.
2.  **Biblioteca Pillow:** Responsável pela geração dos infográficos.

### ⚡ Auto-Setup (Self-Healing)
A partir da versão 3.1.0, a skill conta com inteligência de auto-inicialização. Na primeira vez que você solicitar um infográfico, o motor técnico:
1.  Verifica se o **Pillow** está presente.
2.  Caso não esteja, realiza a **instalação automática** via `pip`.
3.  Notifica você no terminal sobre o progresso.

Isso garante uma experiência **Zero Friction** e **Plug-and-Play**, ideal para ambientes de agentes autônomos e containers limpos.

---

## 🔄 Fluxo de Inteligência (Engine Lifecycle)

O diagrama abaixo ilustra o ciclo de vida de uma extração. Este formato em **Unicode Art** garante a visualização correta em qualquer editor, terminal ou ambiente Git.

```text
┌────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Pedido Inicial │────▶│ Validação Terroir│────▶│ Sugestão de Setup   │
└────────────────┘     └─────────┬────────┘     └──────────┬──────────┘
                                 │                         │ 
                       (Mogiana/Cerrado)        (Ratio/Moagem/Água)
                                 │                         │
                                 ▼                         ▼
┌────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ ✅ Café Final  │◀────│ Feedback Tempo   │◀────│ Execução Blooming   │
└────────────────┘     └─────────┬────────┘     └─────────────────────┘
                                 │
                        (Lento/Rápido?)
                                 │
                                 ▼
                       [Ajuste de Moagem]
```

---

## ⚙️ Engenharia de Escala (Auto-Scaling Dose)

A versão 3.1.0 introduz a **Engenharia de Escala**, tratando a dose de café como um recurso elástico. O sistema agora gerencia a relação entre o número de pessoas e os insumos técnicos (pó/água).

### 📊 Fluxo de Dados e Cálculo
Para um desenvolvedor júnior, imagine isso como um **Microserviço de Dosagem**:

```text
    USER INPUT                  AGENT REASONING                ENGINE CALC (Python)
  ┌──────────────┐          ┌─────────────────────┐          ┌──────────────────────┐
  │ "Reunião de  │─────────▶│ Inferência:         │─────────▶│ volume = pessoas * 150│
  │  5 pessoas"  │          │ num_pessoas = 5     │          │ pó = volume * ratio  │
  └──────────────┘          └──────────┬──────────┘          └──────────┬───────────┘
                                       │                                │
                                       ▼                                ▼
                            ┌─────────────────────┐          ┌──────────────────────┐
                            │ STORYTELLING ARG:   │◀─────────│ OUTPUTS:             │
                            │ --story "Contexto.."│          │ - Infográfico (PNG)  │
                            └─────────────────────┘          │ - Protocolo (MD)     │
                                                              └──────────────────────┘
```

**Regras de Negócio aplicadas:**
*   **Default Unit:** 150ml por pessoa (uma dose padrão de café especial).
*   **Inferência Inteligente:** Se você disser "Quero um café", o agente assume `1 pessoa`. Se for uma `reunião`, o agente suspende a execução para perguntar o quorum, garantindo que não falte café no seu "deploy".

---

### 🧠 Visão de Estados (Complementar)

Para visualizadores que suportam Mermaid (GitHub/VS Code):

```text
                               ESTADOS DA EXTRAÇÃO
      ┌────────────────┐       ┌─────────────────┐       ┌───────────────────┐
  ───▶│      IDLE      │───1──▶│   PREPARAÇÃO    │───2──▶│      BLOOMING     │
      └────────────────┘       └─────────────────┘       └─────────┬─────────┘
              ▲                                                    │
              │                                          (Liberação de CO2 / 30s)
      ┌───────┴────────┐                                           │
      │   AJUSTE DE    │◀──────5───────[ FAIL ]──────────┐         ▼
      │    MOAGEM      │                                 │   ┌───────────────┐
      └────────────────┘                                 └───│      QA       │
              ▲                                              │  (CHECKPOINT) │
              │                                          ┌──▶└───────────────┘
      ┌───────┴────────┐       ┌─────────────────┐       │         │
      │    FINISHED    │◀──4───│    EXTRAÇÃO     │───3───┘      [ PASS ]
      └────────────────┘       └─────────────────┘                 │
                                                                   ▼
                                                            ┌───────────────┐
                                                            │ ✅ CAFÉ PRONTO │
                                                            └───────────────┘

  [1] Iniciar Skill  [2] Despejo (2x pó)  [3] Filtragem  [4] Parâmetros OK  [5] Tempo Errático
```

> 🖼️ **Visual Check:** Se o seu visualizador suportar imagens locais, consulte o infográfico detalhado em: `./assets/flowchart.png`

---

## 🖼️ Galeria de Outputs Visuais (Novo!)

A skill agora conta com um **motor de infográficos criativos** (v3.1). Cada cenário de desenvolvimento possui uma identidade visual única, agora com um layout expandido de **5 métricas**.

**O que há de novo no Infográfico:**
*   **Card de PESSOAS:** Indica claramente para quantos "usuários" a receita foi escalonada.
*   **Grid de 5 Colunas:** Layout otimizado para PESSOAS, CAFÉ, ÁGUA, TEMP e MOAGEM.
*   **Storytelling embutido:** O texto rico e motivacional gerado pela IA agora é injetado no rodapé e no documento Markdown através do parâmetro `--story`.

| Cenário | Preview Visual | Mood / Aplicação |
| :--- | :--- | :--- |
| **Debugging** | `output/cafe_debugging_*.png` | War Room, Tensão, Resiliência. |
| **Deploy** | `output/cafe_deploy_*.png` | Celebração, Vitória, Pipeline Verde. |
| **Team Topologies** | `output/cafe_team_topologies_*.png` | Alinhamento, Fluxos, Estrutura. |
| **Planning** | `output/cafe_planning_*.png` | Foco, Estratégia, Equilíbrio. |
| **Code Review** | `output/cafe_code_review_*.png` | Precisão, Limpeza, Análise Técnica. |
| **Doc Mode** | `output/cafe_documentation_*.png` | Conforto, Contemplação, Foco. |

*Os arquivos são gerados no diretório `/output/` e seguem o padrão de nomenclatura `cafe_[cenario]_[timestamp].png`.*

---

## 📊 Barista Analytics (Observabilidade)

A partir da v4.0.0, sua skill não apenas faz café, ela **observa** seu time. Cada extração bem-sucedida é registrada em um banco de dados local (`data/history.json`).

### O que o Analytics rastreia?
*   **Stress Metrics:** Frequência de cenários como `incident` e `debugging`.
*   **Resource Management:** Total de litros e gramas de café consumidos.
*   **Impacto Humano:** Quantas pessoas foram servidas pelo Agente.

### Como gerar seu Dashboard?
Você pode solicitar um balanço do histórico a qualquer momento. O Agente gerará um infográfico exclusivo de dashboard:

**Comando:**
```bash
python3 scripts/validar_cafe.py --dashboard
```

> 🎭 **Humor Barista:** Se o dashboard apontar muitos `incidents`, o sistema sugerirá automaticamente um grão com maior doçura para acalmar os ânimos!

---

## 🚀 Como Usar (Prompt-First)

A forma recomendada de usar esta skill é através da **interface de chat** com o Agente de IA. O agente utiliza o `SKILL.md` como cérebro para entender seu pedido e o motor Python para gerar o visual.

### 1. Pedido com Visual (Recomendado)
**Prompt:** *"Pode me sugerir um café para debugging e gerar o infográfico de preparo?"*
> O Agente calculará os parâmetros e invocará o motor visual, retornando o caminho da imagem e as instruções.
> 
> ✨ **Novo:** O Agente agora está instruído a incluir automaticamente o link e a renderização da imagem ao final de cada sugestão visual.

### 2. Pedido Baseado em Cenário (Consultoria)
**Prompt:** *"Estou em uma sessão crítica de deploy e preciso de café para 2 pessoas. O que você sugere?"*

### 3. Ajuste de Extração
**Prompt:** *"Meu último café ficou amargo. Como ajusto a moagem para 300ml de Sul de Minas?"*

---

## ✅ Verificação Técnica e Automação

Para desenvolvedores e automações, a skill pode ser invocada via terminal:

**Comando de Validação (Modo Visual):**
```bash
python3 scripts/validar_cafe.py --ml 250 --cenario debugging --imagem
```

**Comando de Validação (Modo JSON):**
```bash
python3 scripts/validar_cafe.py --ml 250 --cenario debugging --json
```

---

## 🤖 O Agente Autônomo: Validação nos Bastidores

Nesta skill, a IA não é apenas um chatbot; ela é um **operador técnico**. Veja como o Agente utiliza o motor de validação de forma autônoma:

### Cenário: "O Sentinela do Café" (Double-Check Automático)

*O desenvolvedor pede um café para uma sessão de debugging, mas menciona que a água acabou de ferver.*

1.  **O Gatilho:** Você diz: *"Barista, vou fazer um café para debugging agora. A água já ferveu, posso colocar?"*
2.  **A Análise Interna:** O Agente lê seu pedido e identifica o risco térmico (água fervente). No `SKILL.md`, ele vê que existe uma ferramenta de validação.
3.  **A Execução Silenciosa (Tool Call):** Antes de te responder, o Agente executa internamente:
    ```bash
    python3 scripts/validar_cafe.py --ml 300 --cenario debugging --temp 100 --json
    ```
4.  **O Processamento do Erro:** O script retorna um JSON informando: `"status": "FAILED", "errors": ["Água fervente detectada..."]`.
5.  **A Resposta Inteligente:** Em vez de apenas dizer "não use água quente", o Agente entrega uma solução embasada:
    > "Espere um momento! Acabei de rodar meu motor de validação e detectamos que 100°C vai queimar seu Cerrado. Deixe a água descansar por 60 segundos para atingirmos os 94°C ideais para o seu debugging. Enquanto isso, prepare os 25g de café."

*Este ciclo demonstra o Agente usando **Raciocínio + Ferramenta** para evitar falhas no mundo real.*

---

## 🎭 A Jornada do Café: O Ciclo de Vida do Desenvolvedor

Na engenharia de software, o café não é apenas energia; é um **estado mental**. Esta skill foi desenhada para acompanhar as flutuações de foco do seu time.

### 🧪 Cenário 1: O Sprint Planning (Equilíbrio e Foco)
*O time está reunido, as tasks ainda são estimativas e o backlog está limpo.*
*   **Necessidade:** Um café que traga clareza mental e doçura para as discussões críticas.
*   **Comando:** `"Barista, prepare uma Mogiana equilibrada para 6 pessoas (900ml)."`
*   **O Agente responde:** 
    > "Iniciando modo Planning. Aplicando Ratio 1:12 para destacar a doçura e notas de chocolate. Vamos calibrar para 75g de café moagem média-fina. Uma base sólida para um sprint promissor."

### 🐛 Cenário 2: O Bug em Produção (Resiliência e Punch)
*São 14h, um erro 500 está subindo nos logs e o time entrou em 'war room'.*
*   **Necessidade:** Intensidade, corpo e resistência. Um café que sustente o raciocínio sob pressão.
*   **Comando:** `"Preciso de um Cerrado intenso, 300ml, moagem para punch extra."`
*   **O Agente responde:**
    > "Modo War Room ativado. Reduzindo ratio para 1:11 e elevando temperatura para 94°C para extrair o máximo de corpo do Cerrado Mineiro. Diagnóstico extra: Verifique o TDS da água para evitar amargor excessivo sob alta temperatura."

### 🚀 Cenário 3: O Deploy de Sexta (Celebração e Nuances)
*A feature foi lançada, os testes passaram e o merge foi feito. Hora de apreciar a vitória.*
*   **Necessidade:** Complexidade sensorial. Um café ácido e vibrante para um momento de descontração.
*   **Comando:** `"Celebração: Sul de Minas, perfil frutado para um 'Done' bem feito."`
*   **O Agente responde:**
    > "Launch Mode! Aplicando a técnica de Sul de Minas (Ratio 1:15, 90°C). Vamos focar na acidez cítrica e corpo leve. Este é um café para ser apreciado lentamente enquanto os logs estabilizam no dashboard de monitoramento."

---

## 🛠️ Stack Tecnológica & Arquitetura

Esta skill foi construída sob o princípio da **Simplicidade Robusta**, utilizando ferramentas de alta performance e baixa dependência externa para garantir a portabilidade do Agente.

### 🧰 Tecnologias Core
*   **Python 3.x:** A linguagem base da inteligência técnica. Escolhida por sua expressividade em regras de negócio e vasta biblioteca de manipulação de dados.
*   **Pillow (PIL):** Motor de renderização do infográfico. Permite a criação dinâmica de composições 2D (gradientes, tipografia, ícones) sem a necessidade de bibliotecas pesadas de UI.
*   **Argparse & JSON:** Utilizados para criar uma interface de comando (CLI) limpa e permitir que o Agente de IA "converse" com o código de forma estruturada.

### 📂 Anatomia dos Scripts
1.  **`scripts/validar_cafe.py` (O Orquestrador):**
    *   **Papel:** Gerencia o *Business Logic* (matrizes de terroir e ratios).
    *   **Responsabilidade:** Realiza o cálculo de escala (Dose/Volume), validação de QA (alertas térmicos) e a geração do documento Markdown portátil.
2.  **`scripts/infografico_engine.py` (O Motor Visual):**
    *   **Papel:** Responsável pela *Presentation Layer*.
    *   **Responsabilidade:** Transforma o dicionário de parâmetros técnicos em um infográfico PNG com temas dinâmicos por cenário (War Room, Launch Mode, etc).

### 📐 Escolhas Arquiteturais (Design Decisions)
*   **Base64 Image Embedding:** Optamos por embutir as imagens via Base64 no Markdown. **Justificativa:** Isso torna o arquivo `.md` 100% autossuficiente (portátil), permitindo que ele seja compartilhado por e-mail ou Slack sem perder o infográfico.
*   **Isolamento de Responsabilidade:** Separar o cálculo (`validar_cafe.py`) da renderização (`infografico_engine.py`) segue o princípio **SOLID**, facilitando a criação de novos temas visuais sem quebrar a lógica de extração.
*   **Standard Lib First:** Priorizamos bibliotecas nativas do Python para reduzir o *Cold Start* e a necessidade de instalações complexas.

---

## 🏗️ Anatomia da Skill: Mergulho Técnico no `SKILL.md`

Como arquiteto sênior, vou decompor exatamente o que compõe o "cérebro" da nossa **Advanced Brazilian Coffee Engine**. O arquivo `SKILL.md` desta skill não apenas descreve o que ela faz, mas implementa as regras de negócio que o Agente segue rigorosamente.

### 1. O Contrato de Interface (Frontmatter YAML)
O topo do arquivo define a "API" da skill. É aqui que estabelecemos o que o Agente precisa receber (Input) e o que ele promete entregar (Output).

*   **Inputs Estruturados:** Note como definimos `volume_ml` como um inteiro (mínimo 150) e `regiao` como um `enum`. Isso evita que o Agente aceite entradas inválidas como "um pouquinho de café".
*   **Cenários de Negócio:** O campo `cenario` é a nossa "Feature Toggle" contextual. Ele permite que a lógica de preparo mude se você está em um `debugging` tenso ou em um `deploy` festivo.

```text
                          O CONTRATO DE INTERFACE
    ┌───────────────────────────┐         ┌───────────────────────────┐
    │   INPUT (Prompt/JSON)     │         │    BUSINESS LOGIC (SKILL) │
    │   - Volume: 150ml+        │────────▶│    - Terroir Matrix       │
    │   - Região: Mogiana...    │         │    - Regras de Barismo    │
    │   - Cenário: Debugging... │         │    - Diagnóstico de QA    │
    └───────────────────────────┘         └─────────────┬─────────────┘
                                                        │
                              ┌─────────────────────────┴────────────────────────┐
                              ▼                                                  ▼
                 [Cerrado + Debugging]                            [Mogiana + Planning]
                 Lógica: 94ºC | 1:15                              Lógica: 92ºC | 1:12
                 Punch & Resiliência                              Foco & Doçura
                              │                                                  │
                              └─────────────────────────┬────────────────────────┘
                                                        ▼
                                          ┌───────────────────────────┐
                                          │   OUTPUT (Resposta IA)    │
                                          │   - Setup de Extração     │
                                          │   - Insight Sensorial     │
                                          └───────────────────────────┘
```

### 2. A Matriz de Decisão (Terroir Matrix)
Diferente de um código `if/else` tradicional, a IA usa a tabela de **Terroir Matrix** no Markdown como um banco de dados de referência rápida:

*   **Lookup Dinâmico:** Se você seleciona **Sul de Minas**, o Agente lê na tabela que a temperatura alvo é **90°C** e a moagem deve ser **Média-Grossa**. Isso democratiza a expertise de barismo para o código.
*   **Notas Sensoriais:** O Agente usa os dados das notas (Chocolate, Nozes, Frutas Amarelas) para construir o insight de humor e motivação que ele entrega no final.

### 3. O Motor de Diagnóstico e QA
Esta skill implementa o que chamamos de **"Self-Healing Instructions"**:

*   **Controle Químico:** O Agente é instruído a verificar o TDS (Total Dissolved Solids) da água (75-150 ppm). Se você reportar um café "plano", ele usará a seção de **Capacidades Avançadas** para diagnosticar que sua água pode estar muito pura.
*   **Detecção de Bugs Físicos:** Através dos sintomas (Amargo/Cinza vs. Aguado/Azedo), o Agente atua como um depurador de moagem em tempo real, sugerindo ajustes granulares.

### 4. Análise Passo a Passo do Protocolo Operacional
O coração operacional do `SKILL.md` é o **Protocolo de Execução**. Como arquitetos, interpretamos esses passos como um algoritmo sequencial de alta precisão:

| Passo | Objetivo Técnico | Lógica do Agente |
| :--- | :--- | :--- |
| **1. Setup Térmico** | Estabilização Térmica | Evita o "Erro de Pirólise" (queima do café) ao impor o limite de 94°C. |
| **2. Purga Quente** | QA de Integridade | Garante que o "Hardware" (filtro) não injete ruído (gosto de papel) no sistema. |
| **3. Blooming** | Hidratação e Purga de CO2 | Um `sleep(30s)` mandatório para permitir que a química da extração ocorra sem interferência de gases. |
| **4. Extração em Pulsos** | Controle de Rendimento | Divide o fluxo em 40/60 para separar a extração de ácidos (Curva A) da extração de açúcares/corpo (Curva B). |

### 5. O Ciclo de Feedback (QA & Diagnóstico)
O `SKILL.md` fecha o loop com uma seção de **Gotchas**. Se o tempo de execução divergir do esperado (3:00 - 4:00 min), o Agente utiliza esta seção para rodar um diagnóstico de causa raiz, geralmente apontando para a granulometria da moagem.

### 🧪 Conclusão para o Dev Júnior:
No `receita-cafe`, o `SKILL.md` é o seu **System Design**. O YAML é o seu **Protocol Buffer/Swagger**, a Matrix de Terroir é o seu **Dataset**, e o Protocolo acima é o seu **Runtime Script/Workflow Logic**.

---

## 🛠️ Manutenção e Expansão

- **Adicionar Regiões:** Edite a matriz `TERROIRS` em `SKILL.md` e `validar_cafe.py`.
- **Ajustar Regras:** As faixas de TDS de água e tempos de extração podem ser calibradas no arquivo `scripts/validar_cafe.py`.
