# Plano de Implementação: Barista Analytics (v4.0.0)

Este plano descreve a evolução da skill para suportar observabilidade de consumo e dashboards de alto impacto.

## 🎯 Objetivo
Transformar a skill em um sistema com memória, capaz de rastrear o consumo de café por cenário e gerar dashboards visuais (infográficos de histórico) com insights humorísticos e técnicos.

## 🛠️ Fases e Tarefas

### Fase 1: Persistência (A Memória)
- [ ] **Tarefa 1.1:** Criar diretório `data/` para armazenamento persistente.
- [ ] **Tarefa 1.2:** Modificar `validar_cafe.py` para salvar cada extração em `data/history.json`.
- [ ] **Tarefa 1.3:** Garantir que o registro inclua: data, cenário, região, volume e número de pessoas.

### Fase 2: Motor de Analytics
- [ ] **Tarefa 2.1:** Criar `scripts/analytics_engine.py` para processar o JSON.
- [ ] **Tarefa 2.2:** Calcular estatísticas:
    - Cenário mais frequente.
    - Total de litros produzidos.
    - Total de gramas de café consumidos.
    - "Nível de Stress do Time" (baseado na frequência de cenários `debugging` e `incident`).

### Fase 3: Dashboard Visual (High Impact)
- [ ] **Tarefa 3.1:** Implementar `gerar_dashboard_visual` em `infografico_engine.py`.
- [ ] **Tarefa 3.2:** Design do Dashboard:
    - Gráfico de pizza ou barras (simulado/visual) para cenários.
    - Badges de conquista (ex: "Master of Debugging", "Deploy King").
    - Frases de impacto com humor barista-dev.

### Fase 4: Integração e Documentação
- [ ] **Tarefa 4.1:** Atualizar `SKILL.md` com o novo comando/cenário para gerar o dashboard.
- [ ] **Tarefa 4.2:** Atualizar `README.md` com a seção "Barista Analytics".

## 🚀 Próximos Passos
Iniciaremos agora com a **Fase 1 (Persistência)**.
