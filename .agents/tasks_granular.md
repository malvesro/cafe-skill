# 📋 Tarefas Granulares: Evolução da Skill receita-cafe

## 🟢 Fase 1: Análise e Fundamentos
### [x] T1: Análise Arquitetural
### [x] T2: Explicação Didática do Padrão

## 🟡 Fase 2: Evolução Técnica (O Coração da Skill)
### [x] T3: Implementação do Log de Execução (Flow Tracer)
### [x] T4: Integração dos Arquivos no Fluxo

## 🔵 Fase 3: Camada Visual e Storytelling
### [x] T5: Template de Prompt para Geração de Imagem
### [x] T6: Geração da Imagem de Demonstração

## 🏁 Fase 4: Entrega Final
### [x] T7: Demonstração Completa (The Perfect Pour)

## 🧼 Fase 5: Harmonização de Ativos (Professionalization)
### [x] T8: Formalização do Contrato (SKILL.md)
### [x] T9: Profundidade de Trace na UI (infografico_engine.py)
### [x] T10: Atualização do Manual de Uso (README.md)
### [x] T11: Teste de Aceitação de Integração (UAT)

## 💎 Fase 6: Polimento e Excelência
### [x] T12: Traceability no Módulo Analytics (analytics_engine.py)
### [x] T13: Log de Aplicação de Storytelling

## 🖼️ Fase 7: Atualização da Vitrine (Root README.md)
### [x] T14: Destaque para a Rastreabilidade Didática
### [x] T15: Seção de Multimodalidade e Storytelling
### [x] T16: Atualização dos Casos de Uso (Modo War Room, Arc, etc)

## 📊 Fase 8: Diagramação Arquitetural (Visual Docs)
### [x] T17: Sequenciamento de Execução (Mermaid Sequence)
### [x] T18: Fluxograma de Decisão (Mermaid Flowchart)
### [x] T19: Explicação Didática dos Componentes

## 🧠 Fase 9: O Dogma da Inteligência Híbrida
### [x] T20: Seção "Heurística vs Determinismo" no README
### [x] T21: Matriz de Responsabilidade (RACI) da Skill

## 🤖 Fase 10: Observabilidade por Padrão (Always-On)
### [x] T22: Default de Fluxo no Orquestrador
### [x] T23: Sincronização do Contrato (Default Flow)
### [x] T24: Simplificação do Guia do Usuário

## 🔡 Fase 11: Documentação das Fronteiras (Interface Dictionary)
### [x] T25: Dicionário Técnico para Humanos
### [x] T26: Destaque Educativo do Parâmetro Flow
- **Status**: ✅ Concluído. Todos os parâmetros estão documentados e o Flow Tracer está estabelecido como o padrão educativo.

## 🧭 Fase 12: Sincronia dos Diagramas com Runtime Atual
### [x] T27: Atualizar diagrama de sequência (README.md) com branch `pending_multimodal` e finalização criativa
### [x] T28: Atualizar fluxograma de decisão (README.md) com gate de conclusão e validação de trace real
### [x] T29: Atualizar diagrama de estados da skill (README da skill) com bypass dev e caminho `--creative-image-path`
### [x] T30: Verificação final de renderização Markdown/Mermaid (fences e sintaxe)

## 🧩 Fase 13: UX Conversacional e Telemetria Narrada (End-to-End)
### [x] T31: Definir contrato de telemetria para chat (`[ETAPA][COMPONENTE][AÇÃO]`) com níveis `INFO|WARN|ERROR`
### [x] T32: Definir mapa oficial de etapas do fluxo (preflight, deterministic, artifact_packaging, multimodal_closure, final_response)
### [x] T33: Definir política de detalhamento por modo (`resumido`, `normal`, `detalhado`) e limites de verbosidade por etapa
### [x] T34: Definir formato de timestamps e correlação por `run_id` em todas as mensagens de telemetria
### [x] T35: Implementar helper de telemetria textual no orquestrador (`receita_completa.py`) com emissão padronizada
### [x] T36: Emitir telemetria de preflight (inputs normalizados, modo dev, validações de segurança, output_dir)
### [x] T37: Emitir telemetria da execução determinística (script chamado, parâmetros efetivos, resultado técnico)
### [x] T38: Emitir telemetria de artefatos (arquivos lidos/escritos/criados com caminho absoluto e timestamp)
### [x] T39: Emitir telemetria do gate multimodal (motivo de bloqueio, `completion_block_reason`, próxima ação)
### [x] T40: Emitir telemetria da decisão de geração criativa (nativa por prompt vs fallback determinístico) com justificativa
### [x] T41: Emitir telemetria da finalização multimodal (validações PNG, manifesto atualizado, checks finais)
### [x] T42: Incluir no manifesto a trilha resumida de execução para UX (`chat_timeline`) sem duplicar todo JSONL
### [x] T43: Adicionar opção de saída amigável para usuário final (`--chat-telemetry`) sem poluir modo técnico
### [x] T44: Garantir ordenação temporal estrita dos eventos (chat, jsonl, json, html) para evitar divergência
### [x] T45: Implementar classificação de erro para UX (dependência ausente, permissão, artefato inválido, multimodal pendente)
### [x] T46: Exibir mensagens de recuperação guiada por erro (ação sugerida curta e acionável)
### [x] T47: Adicionar telemetria explícita de arquivos alterados/criados com checksum opcional (modo detalhado)
### [x] T48: Validar que Flow Trace e telemetria de chat cobrem 100% dos marcos obrigatórios do SKILL.md
### [x] T49: Atualizar README do projeto com seção "Telemetria no Chat" e exemplos reais
### [x] T50: Atualizar README da skill com tabela "Marco -> Mensagem no Chat -> Evento no Trace"
### [x] T51: Atualizar SKILL.md com guidelines de UX (quando falar, quando resumir, quando bloquear resposta)
### [x] T52: Criar smoke test de UX telemetria (ordem de marcos, presença de blocos e motivos de bloqueio)
### [x] T53: Criar smoke test de completude multimodal (sempre fechar com `creative_image_path` válido)
### [x] T54: Revisão final arquitetural (consistência entre chat, manifesto e flow trace) + commit por tema

## 🇧🇷 Fase 14: Localização PT-BR da Telemetria
### [x] T55: Definir glossário oficial PT-BR para telemetria (termos técnicos permitidos e equivalências)
### [x] T56: Padronizar labels de etapas/componentes no chat para PT-BR (ex.: `PRE-FLIGHT` -> `PREPARACAO`)
### [x] T57: Padronizar ações de telemetria para verbos em PT-BR (`START/EXECUTE/VALIDATE/FINALIZE/BLOCK`)
### [x] T58: Revisar mensagens `INFO` para linguagem clara e objetiva em português do Brasil
### [x] T59: Revisar mensagens `WARN` com orientação de recuperação em português do Brasil
### [x] T60: Revisar mensagens `ERROR` com causa + ação recomendada em português do Brasil
### [x] T61: Uniformizar acentuação e ortografia PT-BR em arquivos de manifesto, trace e chat
### [x] T62: Revisar consistência de termos entre `SKILL.md`, `README.md` do projeto e `README.md` da skill
### [x] T63: Criar tabela "Termo antigo -> termo PT-BR" para rastreabilidade de migração
### [x] T64: Atualizar exemplos de telemetria no `SKILL.md` para PT-BR completo
### [x] T65: Adicionar smoke test de linguagem (detectar termos em inglês não permitidos na telemetria de chat)
### [x] T66: Executar validação final de legibilidade com amostras reais de execução (incident/debugging/planning)

## 📘 Fase 15: UX de README para Parâmetros, Padrões e Prompt-First
### [x] T67: Criar seção no README raiz "Comece por intenção" (chat, CLI rápido, runtime completo, troubleshooting)
### [x] T68: Criar tabela canônica "Parâmetro | Onde aplica | Default | Obrigatório | Exemplo" no README da skill
### [x] T69: Documentar regras de inferência de parâmetros por prompt (singular, reunião, cenário crítico, pedido de imagem)
### [x] T70: Adicionar matriz didática "Tipo de pedido -> parâmetros efetivos" com pelo menos 8 exemplos reais
### [x] T71: Explicar claramente diferenças entre `validar_cafe.py` e `receita_completa.py` (quando usar cada um)
### [x] T72: Documentar opções multimodais (`creative_image_required`, `--creative-image-path`, fallback, finalizer)
### [x] T73: Inserir seção "Padrões e Fallbacks" (pessoas, ml, telemetria, saída em `.ia/output`)
### [x] T74: Adicionar exemplos "Copiar e Rodar" por perfil (iniciante, líder técnico, automação CI)
### [x] T75: Adicionar seção "Como ler o manifesto" com campos mínimos e decisões de bloqueio
### [x] T76: Criar FAQ curta sobre ambiguidades comuns (prompt vs CLI, bypass dev, imagem criativa pendente)
### [x] T77: Revisar consistência de termos entre README raiz, README da skill e SKILL.md para novos blocos
### [x] T78: Verificar renderização Markdown final (tabelas, fences, mermaid) e legibilidade móvel/desktop
### [x] T79: Garantir aviso explícito de artefatos na saída final (markdown, infográfico, imagem criativa)
### [x] T80: Sincronizar READMEs com o bloco obrigatório `[RESUMO_ENTREGA]`
### [x] T81: Atualizar SKILL.md com regra obrigatória de exibição do `[RESUMO_ENTREGA]`
