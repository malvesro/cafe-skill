---
name: receita-cafe
description: >
  Engine avançada de extração de café. Harmoniza o rigor técnico do 
  padrão Agent Skills com o conhecimento sensorial do barista. 
  Capacidades: Cálculo de extração, Ajuste de Moagem, Perfil de Água, 
  Correção de Erros e Observabilidade de Consumo (Analytics).
version: "3.0.0"
license: MIT
metadata:
  author: coffee-engineer-senior
  domain: culinary, science, automation
  language: pt-BR

interface:
  input:
    type: object
    required: [volume_ml]
    properties:
      volume_ml: { type: integer, minimum: 150 }
      regiao: { type: string, enum: [mogiana, cerrado, sul_de_minas, espirito_santo, mantiqueira, chapada_diamantina, matas_de_minas, alta_mogiana, amazonico, generico] }
      cenario:
        type: string
        enum: [planning, debugging, deploy, code_review, scrum, team_topologies, architecture, security, refactoring, incident, documentation]
        description: Cenário do time de dev para sugestão personalizada.
      intensidade: { type: string, enum: [suave, equilibrado, intenso], default: equilibrado }
      num_pessoas: { type: integer, minimum: 1, default: 1 }
      moagem_ajustavel: { type: boolean, default: true }
      dashboard: { type: boolean, default: false, description: "Gera relatório de analytics" }
      flow: { type: boolean, default: true, description: "Habilita o modo de rastreabilidade didática passo a passo (Ativado por padrão)" }
  output:
    type: object
    properties:
      parametros_finais: { type: object }
      alerta_qa: { type: array, items: { type: string } }
      protocolo_execucao: { type: string }
      image_path:
        type: string
        description: >-
          Caminho absoluto para o PNG do infográfico gerado.
          Preencher quando o agente invocar o modo visual (--imagem).
      markdown_path:
        type: string
        description: Caminho absoluto para o documento Markdown portatil gerado.
      creative_prompt_path:
        type: string
        description: Caminho absoluto para o prompt criativo persistido como artefato rastreavel.
      creative_image_path:
        type: string
        description: Caminho absoluto para a imagem criativa final, quando gerada por ferramenta nativa de imagem.
---

# ☕ Advanced Brazilian Coffee Engine (v3.0)

## 🖼️ Output Visual (Infográfico)

O agente **DEVE** executar o runtime completo quando o usuário solicitar uma receita completa, sugestão de café para um cenário, reunião/time, ou visualização do preparo. Nesses casos, a skill não deve ser usada apenas como base conceitual de resposta: o agente deve invocar a CLI, capturar o Flow Tracer real e entregar os artefatos gerados.

Preferencialmente, invoque o runtime canonico:

```bash
python3 scripts/receita_completa.py --cenario <cenario> --pessoas <num>
```

Se precisar chamar o motor base diretamente, invoque o engine visual com:

```bash
python3 scripts/validar_cafe.py --ml <volume> --cenario <cenario> --pessoas <num> --flow --imagem --markdown
```

O arquivo PNG é salvo em `.ia/output/cafe_<cenario>_<timestamp>.png`, o documento portátil em `.ia/output/receita_<cenario>_<timestamp>.md` e o prompt criativo em `.ia/output/prompt_criativo_<cenario>_<timestamp>.txt` quando o runtime canonico for usado.

### 🛤️ Flow Trace Obrigatório
Toda execução completa da skill **DEVE** emitir telemetria em tempo real e persistida:

- Console em tempo real com `[FLOW]`.
- `.ia/output/flow_trace_<cenario>_<timestamp>.jsonl` para eventos append-only.
- `.ia/output/flow_trace_<cenario>_<timestamp>.json` para auditoria estruturada.
- `.ia/output/flow_trace_<cenario>_<timestamp>.html` para visualização amigável.
- Links para a telemetria no manifesto e no Markdown portátil.

O nível de detalhe pode variar no futuro, mas a existência da telemetria não é opcional nesta skill.

### 🎨 Creative Image Runtime
A imagem criativa é uma fase **agent-native** posterior ao runtime determinístico. Quando o manifesto indicar `creative_image_required: true`, o agente **DEVE**:

1. Ler o `creative_prompt_path`.
2. Chamar a ferramenta nativa de geração de imagem com esse prompt.
3. Copiar a imagem final para `.ia/output/imagem_criativa_<cenario>_<timestamp>.png`.
4. Executar `scripts/finalizar_imagem_criativa.py --manifest <manifest_path> --creative-image-path <png>`.
5. Responder somente depois que `creative_image_path` estiver preenchido no manifesto.

Se o manifesto retornar `status: "pending_multimodal"` ou `completion_allowed: false`, o agente **NAO PODE** enviar resposta final ao usuário. Ele deve executar imediatamente `agent_next_action`, normalmente gerar a imagem criativa com a ferramenta nativa de imagem e rodar o finalizador.

Se a ferramenta nativa de imagem não estiver disponível, o agente deve declarar a limitação explicitamente e manter o manifesto como multimodal pendente. Esse é o único caso em que uma resposta com pendência é aceitável.

### ✅ Definition of Done do Runtime Completo
Antes de responder como entrega concluída, o agente **DEVE** verificar:

- A CLI da skill foi executada, não apenas consultada.
- O Flow Tracer real apareceu na saída (`[FLOW]`).
- O PNG técnico foi criado em `.ia/output/cafe_<cenario>_<timestamp>.png`.
- O Markdown portátil foi criado em `.ia/output/receita_<cenario>_<timestamp>.md`.
- O Markdown contém o infográfico embutido via `data:image/png;base64`.
- O prompt da imagem criativa foi produzido e informado como artefato rastreável.
- O Flow Trace JSONL foi criado.
- O Flow Trace JSON foi criado.
- O Flow Trace HTML foi criado.
- O Markdown portátil contém links para a telemetria.
- Se `creative_image_required` for `true`, `creative_image_path` deve apontar para um PNG existente.
- `completion_allowed` deve estar `true` antes da resposta final.
- Se a ferramenta nativa de imagem não estiver disponível, a limitação deve ser declarada explicitamente e o manifesto deve permanecer com `multimodal_status: "pending"`.
- Os caminhos finais dos artefatos devem ser apresentados ao usuário.

### 🧭 Runbook de Estados de Execução

- `status: "ok"`: execução determinística + multimodal (quando obrigatório) concluídas.
- `status: "pending_multimodal"`: parte determinística concluída; falta gerar/finalizar imagem criativa.
- `status: "failed"`: falha na execução determinística ou validações obrigatórias.

Campos de apoio para diagnóstico:

- `flow_trace_real_validated`: confirma validação estruturada da telemetria (`jsonl/json/html` + eventos mínimos).
- `completion_block_reason`: motivo explícito para bloqueio de conclusão (`deterministic_runtime_failed`, `creative_image_pending`, etc.).

Regras de saída:

- Se `completion_allowed=false`, a execução deve retornar erro para bloquear conclusão prematura.
- Se `creative_image_required=true`, a resposta final ao usuário só é permitida após `creative_image_path` válido no manifesto.

### 💬 Contrato de Telemetria no Chat

Para melhorar UX e rastreabilidade em tempo real, mensagens de progresso no chat devem seguir o formato:

`[ETAPA][COMPONENTE][ACAO] Mensagem curta e acionável`

Níveis suportados:

- `INFO`: progresso normal do fluxo.
- `WARN`: situação recuperável (fallback, retry, dependência opcional).
- `ERROR`: bloqueio real de execução.

Padrões de uso:

- Sempre incluir `ETAPA` e `COMPONENTE` em caixa alta.
- `ACAO` deve ser verbo curto em PT-BR (`INICIAR`, `EXECUTAR`, `VALIDAR`, `FINALIZAR`, `BLOQUEAR`).
- Mensagem textual deve ter no máximo 1 frase.
- Em `ERROR`, incluir ação recomendada na mesma linha.

Exemplos:

- `[PREPARACAO][ORQUESTRADOR][INICIAR][INFO] Validando parâmetros e ambiente de execução.`
- `[EXECUCAO_DETERMINISTICA][SCRIPT][EXECUTAR][INFO] Executando validar_cafe.py com flow e artefatos visuais.`
- `[FECHAMENTO_MULTIMODAL][PORTAO][DECIDIR][WARN] Ferramenta nativa indisponível; aplicando contorno criativo local.`
- `[FECHAMENTO_MULTIMODAL][FINALIZADOR][BLOQUEAR][ERROR] Fechamento multimodal pendente; gere PNG criativo e finalize manifesto.`
- `[FECHAMENTO_MULTIMODAL][PORTAO][DECIDIR][WARN] estado=pending_multimodal, conclusao_permitida=False, motivo=creative_image_pending, próximo_passo=gerar imagem criativa PNG e finalizar manifesto.`
- `[FECHAMENTO_MULTIMODAL][PORTAO][FALHAR][ERROR] erro=multimodal_pending; causa=fechamento multimodal pendente por ausência de imagem criativa válida; ação_recomendada=Gere/impute imagem criativa PNG e finalize manifesto.`

### 🇧🇷 Glossário Oficial de Telemetria (PT-BR)

Use estes termos como padrão em mensagens para chat, manifesto e documentação:

| Termo base | Padrão PT-BR | Observação |
| :--- | :--- | :--- |
| Stage | Etapa | Prefixo de alto nível do fluxo. |
| Component | Componente | Serviço/script responsável pela ação. |
| Action | Ação | Verbo curto de telemetria. |
| Status | Estado | Resultado da etapa (`ok`, `pendente`, `falha`). |
| Fallback | Contorno | Caminho alternativo quando a via principal falha. |
| Block reason | Motivo do bloqueio | Causa explícita para `completion_allowed=false`. |
| Runtime manifest | Manifesto de execução | Contrato final de artefatos e checks. |
| Flow trace | Rastro de execução | Trilha JSONL/JSON/HTML da execução real. |
| Chat timeline | Linha do tempo do chat | Recorte resumido para UX no manifesto. |
| Completion allowed | Conclusão permitida | Indicador de liberação da resposta final. |

### 🔁 Migração de Termos (Antigo -> PT-BR)

| Termo antigo | Termo PT-BR |
| :--- | :--- |
| `PRE-FLIGHT` | `PREPARACAO` |
| `DETERMINISTIC` | `EXECUCAO_DETERMINISTICA` |
| `ARTIFACT_PACKAGING` | `EMPACOTAMENTO_ARTEFATOS` |
| `MULTIMODAL_CLOSURE` | `FECHAMENTO_MULTIMODAL` |
| `FINAL_RESPONSE` | `RESPOSTA_FINAL` |
| `CONFIG` | `CONFIGURACAO` |
| `FLOW_TRACE` | `RASTRO_EXECUCAO` |
| `GATE` | `PORTAO` |
| `FINALIZER` | `FINALIZADOR` |
| `START` | `INICIAR` |
| `EXECUTE` | `EXECUTAR` |
| `VALIDATE` | `VALIDAR` |
| `DECISION` | `DECIDIR` |
| `FINALIZE` | `FINALIZAR` |
| `DONE` | `CONCLUIR` |
| `BLOCK` | `BLOQUEAR` |
| `WARN` | `ALERTAR` |
| `ERROR` | `FALHAR` |

### 🗺️ Mapa Oficial de Etapas (Telemetria)

As mensagens de progresso no chat e os eventos de trace devem seguir esta ordem canônica (interno -> rótulo exibido no chat):

1. `PRE-FLIGHT` -> `PREPARACAO`
Descrição: validação inicial de entradas, ambiente, permissões e diretório de saída.
Saída esperada: parâmetros normalizados e pré-condições confirmadas.

2. `DETERMINISTIC` -> `EXECUCAO_DETERMINISTICA`
Descrição: execução do motor técnico (`validar_cafe.py`) para cálculo, infográfico técnico e markdown portátil.
Saída esperada: artefatos determinísticos e prompt criativo rastreável.

3. `ARTIFACT_PACKAGING` -> `EMPACOTAMENTO_ARTEFATOS`
Descrição: consolidação de artefatos, persistência de manifesto e validação de telemetria real (`jsonl/json/html`).
Saída esperada: manifesto consistente, links de trace e checks técnicos atualizados.

4. `MULTIMODAL_CLOSURE` -> `FECHAMENTO_MULTIMODAL`
Descrição: fechamento da fase criativa (geração de imagem criativa + finalização do manifesto).
Saída esperada: `creative_image_path` válido, `multimodal_status=ok`, `completion_allowed=true`.

5. `FINAL_RESPONSE` -> `RESPOSTA_FINAL`
Descrição: publicação da resposta final ao usuário com resumo objetivo e caminhos de artefatos.
Saída esperada: comunicação clara sem ambiguidade de estado.

### 🎛️ Política de Detalhamento por Modo

Os eventos de telemetria no chat devem respeitar um modo de verbosidade:

1. `resumido`
- Objetivo: reduzir ruído para usuários finais.
- Regra: no máximo 1 mensagem por etapa canônica.
- Conteúdo: apenas marcos e status final (`ok`, `pendente`, `falha`).

2. `normal`
- Objetivo: equilíbrio entre clareza e rastreabilidade.
- Regra: 2 a 4 mensagens por etapa (entrada, decisão, saída).
- Conteúdo: componente executado, decisão tomada e artefatos principais.

3. `detalhado`
- Objetivo: auditoria técnica e troubleshooting.
- Regra: mensagens por subpasso relevante da etapa.
- Conteúdo: arquivos lidos/escritos, comandos executados, resultado e fallback.

Limites recomendados por etapa:
- `PRE-FLIGHT`: 1 (`resumido`), 2 (`normal`), até 5 (`detalhado`)
- `DETERMINISTIC`: 1 (`resumido`), 3 (`normal`), até 8 (`detalhado`)
- `ARTIFACT_PACKAGING`: 1 (`resumido`), 2 (`normal`), até 6 (`detalhado`)
- `MULTIMODAL_CLOSURE`: 1 (`resumido`), 3 (`normal`), até 8 (`detalhado`)
- `FINAL_RESPONSE`: 1 (`resumido`), 1 (`normal`), 2 (`detalhado`)

### 🕒 Timestamp e Correlação de Execução

Toda telemetria de chat deve incluir:

- `timestamp`: formato ISO local `YYYY-MM-DDTHH:MM:SS` (timezone da sessão).
- `run_id`: identificador único do runtime (`YYYYMMDD_HHMMSS`).

Formato recomendado da linha:

`[ETAPA][COMPONENTE][ACAO][NIVEL][timestamp][run_id] mensagem`

Exemplo:

`[EXECUCAO_DETERMINISTICA][SCRIPT][EXECUTAR][INFO][2026-04-28T11:05:12][20260428_110512] Executando validar_cafe.py com artefatos visuais.`

### 🧩 Guidelines de UX Conversacional (Obrigatório)

Objetivo: manter previsibilidade para o usuário sem poluir o chat.

Quando falar:
- Emitir mensagem no início e no fim de cada etapa canônica.
- Emitir mensagem adicional quando houver decisão que mude estado (`completion_allowed`, fallback, bloqueio).
- Em `ERROR`, informar causa e ação recomendada na mesma linha.

Quando resumir:
- Preferir uma frase por evento.
- Evitar repetir detalhes já persistidos no manifesto e no trace.
- Em modo `resumido`, limitar a 1 mensagem por etapa.

Quando bloquear resposta final:
- Se `completion_allowed=false`, não publicar resposta conclusiva ao usuário.
- Se `creative_image_required=true` e `creative_image_path` ausente/inválido, manter estado `pending_multimodal`.
- Informar explicitamente o próximo passo usando `agent_next_action` e `completion_block_reason`.

Regra de ouro:
- Chat, manifesto e Flow Trace devem convergir para o mesmo estado final (`ok`, `pending_multimodal` ou `failed`).

### 📢 Diretrizes de Resposta do Agente
Ao iniciar o atendimento, o Agente **deve**:
1.  **Storytelling & Humor (Intro):** Antes de qualquer dado técnico, imagine e descreva a cena do usuário com um toque de humor "dev-friendly".
2.  **Oferecer Opções de Formato:** Perguntar (ou seguir se já solicitado) se o usuário deseja o resultado no **Chat**, como um **Documento Markdown (.md)** estruturado na pasta `.ia/output/`, ou **Ambos**.

Ao finalizar o atendimento, o Agente **deve**:
1.  **Consolidar Entrega:**
    *   **Se Chat:** Exibir o resumo técnico, link absoluto da imagem e renderizar o infográfico (`![Infográfico](caminho)`).
    *   **Se Documento:** Criar um arquivo `.ia/output/receita_[cenario]_[timestamp].md` **PORTÁTIL**. Para garantir a renderização, a imagem deve ser incorporada diretamente no Markdown via **Base64 Data URI** (`![Infográfico](data:image/png;base64,...)`).
    *   **Se Ambos:** Realizar as duas ações acima.
2.  **Lógica de Volume & Pessoas (Inferência):**
    *   **Pedido Singular:** Se o usuário disser "Quero um café" ou "Faz um café", assumir `num_pessoas: 1`.
    *   **Cenário de Reunião:** Se o cenário envolver reuniões (scrum, planning, topologies) e a quantidade não for dita, o Agente **deve suspender a execução e perguntar** "Para quantas pessoas será o café?".
    *   **Indicação Direta:** Se o usuário disser "Café para 5 pessoas" ou citar os participantes, inferir o número e calcular o volume base de **150ml por pessoa**.
3.  **Contextualizar:** Explicar como o café sugerido resolve as dores do cenário descrito e **declarar explicitamente quantas pessoas a receita atende**.
4.  **Oferta de Analytics:** Periodicamente ou quando o usuário solicitar "histórico" ou "balanço", o Agente deve oferecer a geração do **Dashboard de Analytics** (`--dashboard`) para auditar o nível de stress/café do time.

---

## 🌟 Contexto Didático
Um café excepcional é a intersecção entre **química e técnica**. Esta skill orquestra as variáveis de temperatura, turbulência e tempo, garantindo que o agente não apenas "informe", mas **garanta a qualidade** do resultado final.

---

## 🗺️ Business Logic & Terroir Matrix (Expandida)

| Região | Ratio | Temp. | Moagem Sugerida | Notas Sensoriais |
| :--- | :--- | :--- | :--- | :--- |
| **Mogiana** | 1:12 | 92°C | Média-Fina | Doçura, Chocolate, Acidez Baixa |
| **Cerrado** | 1:15 | 94°C | Média | Nozes, Caramelo, Corpo Marcante |
| **Sul de Minas** | 1:14 | 90°C | Média-Grossa | Frutas Amarelas, Acidez Cítrica |
| **Espírito Santo** | 1:13 | 91°C | Média | Especiarias, Chocolate Amargo |
| **Mantiqueira** | 1:12 | 92°C | Média-Fina | Aroma Marcante, Frutado, Nozes |
| **Chapada Diamantina**| 1:14 | 93°C | Média | Aveludado, Cítrico, Final Longo |
| **Matas de Minas** | 1:13 | 91°C | Média | Doçura, Caramelo, Chocolate |
| **Alta Mogiana** | 1:12 | 92°C | Média-Fina | Encorpado, Acidez Média, Frutado |
| **Robusta Amazônico**| 1:11 | 94°C | Grossa | Intenso, Amadeirado, Alta Cafeína |

---

## 🧪 Capacidades Avançadas

### 1. Controle Químico da Água
- **Regra:** Utilize água filtrada ou mineral com TDS entre 75-150 ppm.
- **Aviso Técnico:** Água muito pura (destilada) resulta em café "plano" e sem corpo; água muito dura (calcária) neutraliza a acidez e gera amargor.

### 2. Ajuste Dinâmico de Moagem
O agente deve diagnosticar a granulometria baseada nos sintomas observados:
- **Pó muito fino (Fine):** Entope o filtro e causa sobre-extração. *Sintoma: Café amargo, cinza e tempo > 4.5 min.*
- **Pó muito grosso (Coarse):** A água passa sem resistência. *Sintoma: Café aguado, sem corpo, azedo e tempo < 2.5 min.*
- **Moagem Ideal:** Textura de sal de cozinha (médio-fina) para coadores de papel.

---

## 📋 Protocolo de Execução (The "Golden Path")

1. **Setup Térmico:** Aquecer água ao alvo da região (90°C~94°C). *Dica: Se ferver, aguarde 60s antes do uso para evitar a queima térmica.*
2. **Purga Quente:** Escaldar o filtro. *(Remove o gosto de papel e pré-aquece o porta-filtro — ignorar este passo transfere gosto de celulose para a bebida).*
3. **Pré-Infusão (Blooming):** 2x o peso do pó em água. Aguarde 30s. *Dica: A liberação de CO2 prepara os grãos para uma extração uniforme.*
4. **Extração em Pulsos:**
    - Primeiro pulso (40% da água): Foco em extrair acidez e doçura.
    - Segundo pulso (60% restante): Foco em corpo e equilíbrio.

---

## ⚠️ Gotchas & Diagnóstico (QA)

- **Água Fervente (100°C):** Extrai compostos amargos indesejados. Jamais use água borbulhando.
- **Canalização:** Quando a água abre um "caminho fácil". Mantenha despejos circulares do centro para as bordas para evitar.
- **Proporção:** Respeite o ratio da região. Proporções erradas são a causa #1 de café ruim.

## ✅ Checklist de Certificação
- [ ] Temperatura entre 90 e 94 °C (Não fervendo).
- [ ] Filtro umedecido e porta-filtro pré-aquecido.
- [ ] Pré-infusão de 30s realizada (Bloom).
- [ ] Despejo em movimentos circulares (sem tocar o papel).
- [ ] Tempo total de extração entre 3:00 e 4:00 minutos.

---

## ☕ Exemplo de Saída (Pedido Real)

Pedido: **500ml de Café do Cerrado Mineiro**

```text
Configuração de Extração:
  → Café: 33.3g (Moagem Média)
  → Água: 500ml (Temp: 94°C)
  → Região: Cerrado - Notas de Chocolate e Nozes

Protocolo:
  1. Escaldar filtro e pré-aquecer jarra.
  2. Pré-infusão de 65ml por 30 segundos.
  3. Despejos lentos até completar 500ml.
  4. Tempo esperado: 3min 45seg.
```
