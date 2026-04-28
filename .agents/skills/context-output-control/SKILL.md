---
name: context-output-control
description: >
  Instrui o agente a adotar práticas obrigatórias de controle de output e gestão
  da janela de contexto em todas as tarefas e subtarefas. Use esta skill sempre que
  o agente for executar comandos shell, compilações, buscas, leituras de arquivo,
  testes ou qualquer operação que possa gerar saída longa ou consumo excessivo de
  tokens. A skill garante sessões estáveis, economia de tokens, feedback contínuo
  e evita desconexões prematuras por estouro de contexto.
compatibility: >
  Compatível com qualquer agente de IA com capacidade de execução de comandos shell
  (Bash), leitura de arquivos e raciocínio sequencial. Não requer ferramentas
  específicas além de Bash e Read. Aplicável a projetos em qualquer linguagem ou
  plataforma.
metadata:
  author: ia-especialista
  version: "1.0"
  domain: context-management
  language: pt-BR
  tags: "context-window, output-control, token-economy, estabilidade, shell, performance"
allowed-tools: Bash(tail:*) Bash(head:*) Bash(grep:*) Bash(find:*) Bash(sed:*) Bash(git:*) Read Write
---

# Skill: Controle de Output e Gestão de Contexto

Esta skill estabelece regras obrigatórias para que o agente controle o volume de
output gerado em cada operação, preserve a janela de contexto e mantenha sessões
estáveis com feedback contínuo ao longo de tarefas complexas.

> **Princípio fundamental:** A janela de contexto é um recurso finito e compartilhado
> entre todos os turnos da sessão. Outputs não controlados são a principal causa de
> erros de desconexão, perda de progresso e desperdício de tokens.

---

## Índice

| #   | Seção                                                            | Descrição                                           |
| --- | ---------------------------------------------------------------- | --------------------------------------------------- |
| 1   | [Análise Prévia de Tarefa](#1-análise-prévia-de-tarefa)          | Planejamento obrigatório antes de qualquer execução |
| 2   | [Regra Geral de Output](#2-regra-geral-de-output)                | Princípio universal de limitação de saída           |
| 3   | [Limites por Categoria](#3-limites-por-categoria-de-comando)     | Tabela de limites obrigatórios por tipo de comando  |
| 4   | [Padrões de Execução](#4-padrões-de-execução)                    | Exemplos corretos e incorretos por categoria        |
| 5   | [Leitura de Arquivos](#5-leitura-controlada-de-arquivos)         | Técnicas de leitura parcial e incremental           |
| 6   | [Decomposição de Tarefas](#6-decomposição-e-feedback-de-tarefas) | Como dividir tarefas longas com checkpoints         |
| 7   | [Economia de Tokens](#7-economia-de-tokens)                      | Estratégias para reduzir consumo desnecessário      |
| 8   | [Sinais de Alerta](#8-sinais-de-alerta)                          | Quando pausar e reportar ao usuário                 |

---

## 1. Análise Prévia de Tarefa

**Antes de executar qualquer tarefa ou subtarefa**, o agente DEVE realizar uma
análise técnica e estratégica respondendo às seguintes perguntas:

### Checklist de Pré-Execução

- [ ] **Volume de output**: Este comando pode gerar saída longa? (>50 linhas)
- [ ] **Complexidade**: Esta tarefa tem mais de 3 etapas encadeadas?
- [ ] **Duração estimada**: A execução pode demorar mais de 30 segundos?
- [ ] **Dependências**: Existe alguma saída anterior que precisa ser preservada no contexto?
- [ ] **Atomicidade**: Posso dividir esta tarefa em unidades menores com feedback entre elas?

### Protocolo de Decisão

SE (volume de output provável > 50 linhas)
→ Aplicar limite obrigatório (seção 3)

SE (tarefa tem > 3 etapas encadeadas)
→ Decompor em subtarefas com checkpoint (seção 6)

SE (duração estimada > 30s sem feedback)
→ Inserir ponto de relatório intermediário

SE (contexto atual > 60% da janela estimada)
→ Resumir contexto antes de continuar (seção 7)

---

## 2. Regra Geral de Output

> **Toda execução de comando que possa gerar saída longa DEVE ser encadeada com
> `| tail -N`, `| head -N`, `--tail=N` ou equivalente antes de ser executada.**

Esta regra não tem exceções. Outputs de comandos não limitados são injetados
diretamente na janela de contexto ativa e podem:

- Causar desconexão prematura da sessão
- Esgotar o orçamento de tokens antes da conclusão da tarefa
- Forçar compactação automática, perdendo contexto útil de turnos anteriores
- Tornar o agente incapaz de raciocinar sobre respostas anteriores

**Em caso de dúvida, sempre prefira menos output e mais iterações.**

---

## 3. Limites por Categoria de Comando

| Categoria             | Comando típico                                 | Limite obrigatório          |
| --------------------- | ---------------------------------------------- | --------------------------- |
| Build / compilação    | `mvn compile`, `gradle build`, `npm run build` | `2>&1 \| tail -30`          |
| Testes                | `mvn test`, `pytest`, `npm test`, `go test`    | `2>&1 \| tail -50`          |
| Logs de aplicação     | `cat *.log`, `journalctl`, `less`              | `\| tail -100`              |
| Grep / busca em texto | `grep -r`, `ag`, `rg`                          | `\| head -30`               |
| Listagem de arquivos  | `ls -la`, `tree`, `find` sem filtro            | `\| head -50`               |
| Docker / container    | `docker logs`, `kubectl logs`, `podman logs`   | `--tail=50`                 |
| Git log / diff        | `git log`, `git diff`, `git show`              | `\| head -80`               |
| Dependências          | `npm list`, `mvn dependency:tree`, `pip list`  | `\| head -40`               |
| Banco de dados        | Queries sem `LIMIT`, exports de tabelas        | `LIMIT 50` ou `\| head -50` |
| Variáveis de ambiente | `env`, `printenv`, `set`                       | `\| head -30`               |

---

## 4. Padrões de Execução

### Builds e Compilações

```bash
# ✅ Correto
mvn compile -q 2>&1 | tail -30
gradle build --quiet 2>&1 | tail -30
npm run build 2>&1 | tail -30
go build ./... 2>&1 | tail -30

# ❌ Nunca fazer
mvn compile
gradle build
npm run build
```

### Testes — Capturar Apenas Falhas

```bash
# ✅ Correto — foco em erros e sumário
mvn test 2>&1 | grep -E "ERROR|FAIL|Exception|Tests run" | head -30
pytest --tb=short -q 2>&1 | tail -50
npm test 2>&1 | tail -50
go test ./... 2>&1 | grep -E "FAIL|ok" | head -30

# ❌ Nunca fazer
mvn test
pytest
npm test
```

### Logs de Aplicação

```bash
# ✅ Correto
tail -100 application.log
journalctl -u meu-servico --no-pager | tail -100
tail -50 /var/log/nginx/error.log

# ❌ Nunca fazer
cat application.log
journalctl -u meu-servico
less application.log
```

### Busca e Grep

```bash
# ✅ Correto — escopo restrito e resultado limitado
grep -r "NomeClasse" src/main/java/com/empresa/ | head -30
find . -name "*.java" -type f -maxdepth 4 | head -40
rg "padrão" src/ --max-count=30

# ❌ Nunca fazer
grep -r "texto" .
find . -type f
rg "padrão"
```

### Containers e Orquestração

```bash
# ✅ Correto
docker logs meu-container --tail=50
kubectl logs pod/meu-pod --tail=50 -n meu-namespace
podman logs --tail=50 meu-container

# ❌ Nunca fazer
docker logs meu-container
kubectl logs pod/meu-pod
```

### Git

```bash
# ✅ Correto
git log --oneline -20
git diff HEAD~1 | head -80
git show HEAD --stat | head -40

# ❌ Nunca fazer
git log
git diff
git show
```

### Banco de Dados

```sql
-- ✅ Correto
SELECT * FROM tabela WHERE status = 'ATIVO' LIMIT 50;
SELECT COUNT(*), status FROM tabela GROUP BY status;

-- ❌ Nunca fazer
SELECT * FROM tabela;
```

---

## 5. Leitura Controlada de Arquivos

### Regras para Leitura de Arquivos

**Nunca use `cat` em arquivos com mais de 100 linhas.** Prefira sempre:

```bash
# Ler as primeiras N linhas
head -50 arquivo.java

# Ler as últimas N linhas
tail -50 arquivo.java

# Ler uma faixa específica de linhas
sed -n '100,200p' arquivo.java

# Contar linhas antes de ler
wc -l arquivo.java

# Verificar tamanho antes de ler
ls -lh arquivo.java
```

### Estratégia de Leitura Incremental

Para arquivos grandes, siga este protocolo:

1. **Verificar tamanho**: `wc -l arquivo` e `ls -lh arquivo`
2. **Ler cabeçalho**: `head -30 arquivo` para entender a estrutura
3. **Buscar seções relevantes**: `grep -n "método\|classe\|função" arquivo | head -20`
4. **Ler faixas específicas**: `sed -n 'N,Mp' arquivo` conforme necessário
5. **Nunca ler o arquivo inteiro** de uma vez se > 200 linhas

---

## 6. Decomposição e Feedback de Tarefas

### Princípio de Atomicidade

Toda tarefa complexa DEVE ser decomposta em unidades atômicas que:

- Completam em menos de 5 etapas de execução
- Produzem um resultado verificável ao final
- Permitem feedback ao usuário entre as etapas

### Protocolo de Checkpoint

INÍCIO DE TAREFA COMPLEXA:

1. Listar subtarefas identificadas
2. Estimar volume de output por subtarefa
3. Executar subtarefa 1
4. → CHECKPOINT: Reportar resultado e confirmar continuidade
5. Executar subtarefa 2
6. → CHECKPOINT: Reportar resultado e confirmar continuidade
   ... repetir até conclusão

NUNCA executar N subtarefas encadeadas sem reportar progresso.

### Formato de Relatório de Checkpoint

Ao atingir um checkpoint, reportar de forma compacta:

✅ Subtarefa [N/Total] concluída: [descrição em 1 linha]
📊 Resultado: [dado ou artefato gerado]
⏭️ Próxima etapa: [descrição]
❓ Continuar? [ou aguardar confirmação se necessário]

---

## 7. Economia de Tokens

### Estratégias de Redução de Consumo

**Prefira flags de modo silencioso:**

```bash
mvn -q              # Maven silencioso
gradle --quiet      # Gradle silencioso
git --no-pager      # Git sem paginador
npm --silent        # npm silencioso
```

**Filtre antes de exibir — nunca exiba para filtrar depois:**

```bash
# ✅ Filtrar na fonte
mvn test 2>&1 | grep -E "ERROR|FAIL" | head -20

# ❌ Exibir tudo e analisar depois (desperdiça tokens)
mvn test  # depois analisar output completo
```

**Sumarize contexto acumulado quando necessário:**

Quando a sessão estiver longa e com múltiplos artefatos discutidos:

- Crie um resumo compacto dos pontos-chave já decididos
- Descarte detalhes de execução já processados
- Mantenha apenas referências (nomes de arquivo, IDs, resultados)

**Evite repetição de contexto:**

- Não repita blocos de código já exibidos no turno anterior
- Referencie por nome: "o arquivo `Config.java` discutido acima"
- Use resumos em vez de transcrever outputs anteriores

### Indicadores de Alerta de Consumo

| Sinal                                     | Ação imediata                                                   |
| ----------------------------------------- | --------------------------------------------------------------- |
| Resposta do agente começa a truncar       | Parar, resumir contexto, continuar em nova sessão se necessário |
| Tarefa com > 10 etapas sem checkpoint     | Decompor e reportar progresso                                   |
| Output de comando > 100 linhas sem filtro | Cancelar, reaplicar com limite                                  |
| Arquivo lido com `cat` > 200 linhas       | Reler com `sed` ou `head`/`tail`                                |

---

## 8. Sinais de Alerta

O agente DEVE pausar e reportar ao usuário nas seguintes situações:

### Situações de Pausa Obrigatória

- **Output inesperadamente grande**: comando retornou volume muito além do esperado
- **Erro de execução**: falha que requer decisão humana antes de continuar
- **Ambiguidade de escopo**: tarefa pode ser interpretada de múltiplas formas
- **Dependência bloqueante**: subtarefa depende de dado ou decisão externa
- **Risco de perda de dados**: operação destrutiva (delete, truncate, overwrite)

### Formato de Alerta

⚠️ PAUSA — [motivo em 1 linha]

Situação: [descrição objetiva do que foi encontrado]
Risco: [impacto potencial se continuar sem intervenção]
Opções:
A) [ação segura]
B) [ação alternativa]
C) Aguardar instrução

---

## Referências

- [Agent Skills — Specification](https://agentskills.io/specification)
- [Agent Skills — Home](https://agentskills.io/home)
  
  
