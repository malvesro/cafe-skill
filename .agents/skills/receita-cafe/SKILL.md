---
name: receita-cafe
description: >
  Prepara café coado brasileiro seguindo as boas práticas de temperatura,
  proporção e tempo de extração. Use quando o usuário pedir para preparar,
  explicar ou ensinar como fazer um bom café coado. Ideal para demonstrar
  a estrutura de uma Agent Skill de forma didática.
license: MIT
compatibility: Requer coador, filtro de papel, café moído e água quente.
metadata:
  author: professor-senior
  version: "1.0"
  language: pt-BR
  domain: culinaria, cafe, didatico, agentskills
---

# ☕ Receita de Café Coado — SKILL

## 📌 Contexto

Um bom café não é apenas misturar pó com água quente.
**Temperatura, proporção e tempo de extração** fazem toda a diferença
entre um café equilibrado e um amargo ou aguado.

Esta skill garante um café coado brasileiro de qualidade, cobrindo
desde a escolha da temperatura até a técnica de despejo em círculos.

> 💡 Para variações avançadas (espresso, prensa francesa, cold brew,
> moagem e torra), carregue: `references/REFERENCE.md`

---

## 🧪 Ingredientes

| Ingrediente    | Quantidade por xícara |
|----------------|-----------------------|
| Café moído     | 10 g                  |
| Água           | 150 ml                |
| Temperatura    | 90 – 96 °C            |
| Tempo total    | 3 – 4 minutos         |

Use o template em `assets/template-pedido.md` para anotar pedidos
customizados (quantidade de xícaras, força, variação).

---

## 📋 Passo a Passo

1. Aqueça a água entre **90 e 96 °C**
   _(não use água fervente — 100 °C queima o café e extrai amargor)_
2. **Umedeça o filtro** com água quente antes de colocar o pó
   _(remove gosto de papel e pré-aquece o coador)_
3. Adicione o **café moído** no filtro umedecido
4. Despeje **30 ml de água** em movimentos circulares e aguarde **30 segundos**
   _(pré-infusão: libera o CO₂ e prepara os grãos para extração uniforme)_
5. Despeje o **restante da água** lentamente, em movimentos circulares
   _(do centro para as bordas, sem tocar o filtro)_
6. Aguarde a extração completa: **3 a 4 minutos** no total

---

## ⚠️ Gotchas

- **Água fervente (100 °C)** extrai compostos amargos — sempre aguarde 1 minuto após ferver
- **Pular a pré-infusão** resulta em extração desigual — partes do pó ficam sub e superextraídas
- **Filtro sem umedecer** transfere gosto de papel para o café
- **Pó muito fino** entope o filtro e superextrai — resultado amargo
- **Pó muito grosso** deixa o café aguado e sem corpo — subextração
- **Proporção errada** é a causa mais comum de café ruim — respeite os 10 g por 150 ml

---

## ✅ Checklist QA

```
[ ] Temperatura entre 90 e 96 °C (não fervendo)?
[ ] Filtro umedecido antes de adicionar o pó?
[ ] Pré-infusão de 30 ml por 30 segundos realizada?
[ ] Despejo em movimentos circulares do centro para as bordas?
[ ] Tempo total de extração entre 3 e 4 minutos?
[ ] Proporção correta: 10 g de café para 150 ml de água?
```

Valide automaticamente com: `python scripts/validar_cafe.py`

---

## ☕ Exemplo de Saída

Para um pedido de **2 xícaras de café médio**:

```
Ingredientes:
  → 20 g de café moído (médio)
  → 300 ml de água a 93 °C

Tempo de pré-infusão: 30 segundos
Tempo total de extração: 3 min 30 seg

Resultado esperado: café equilibrado, levemente encorpado,
                    sem amargor excessivo.
```
