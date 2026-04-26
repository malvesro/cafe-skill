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
---

# ☕ Advanced Brazilian Coffee Engine (v3.0)

## 🖼️ Output Visual (Infográfico)

O agente **DEVE** gerar um infográfico PNG quando o usuário solicitar uma receita completa ou visualização do preparo. Invoque o engine visual com:

```bash
python3 scripts/validar_cafe.py --ml <volume> --cenario <cenario> --pessoas <num> --imagem --markdown
```

O arquivo PNG é salvo em `output/cafe_<cenario>_<timestamp>.png` e o documento portátil em `output/receita_<cenario>_<timestamp>.md`.

### 📢 Diretrizes de Resposta do Agente
Ao iniciar o atendimento, o Agente **deve**:
1.  **Storytelling & Humor (Intro):** Antes de qualquer dado técnico, imagine e descreva a cena do usuário com um toque de humor "dev-friendly".
2.  **Oferecer Opções de Formato:** Perguntar (ou seguir se já solicitado) se o usuário deseja o resultado no **Chat**, como um **Documento Markdown (.md)** estruturado na pasta `output/`, ou **Ambos**.

Ao finalizar o atendimento, o Agente **deve**:
1.  **Consolidar Entrega:**
    *   **Se Chat:** Exibir o resumo técnico, link absoluto da imagem e renderizar o infográfico (`![Infográfico](caminho)`).
    *   **Se Documento:** Criar um arquivo `output/receita_[cenario]_[timestamp].md` **PORTÁTIL**. Para garantir a renderização, a imagem deve ser incorporada diretamente no Markdown via **Base64 Data URI** (`![Infográfico](data:image/png;base64,...)`).
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


