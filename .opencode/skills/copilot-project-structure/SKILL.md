---
name: copilot-project-structure
description: >
  Filosofia e guia prático para estruturar projetos com GitHub Copilot usando agentes,
  skills, instruções customizadas e prompt files. Use quando precisar criar ou revisar
  a arquitetura de IA de um projeto — definir agentes, skills, instruções e automações
  recorrentes com prompt files.
argument-hint: "[projeto ou contexto a estruturar]"
---

# Estruturação de projetos com GitHub Copilot

Este guia define a filosofia e os padrões para criar uma arquitetura de IA bem organizada
em qualquer projeto usando os recursos nativos do GitHub Copilot.

---

## Filosofia central

### Agentes são pessoas, não ferramentas

Um agente não é um wrapper de biblioteca. Um agente é uma **persona** — um profissional
com nome, anos de experiência, valores e forma de pensar. O agente sabe *como* um
desenvolvedor experiente naquele domínio abordaria o problema.

```
ERRADO: "Agente httpx — faz chamadas HTTP com retry"
CERTO:  "Lucas — desenvolvedor Python sênior que sabe httpx, pensa em resiliência
         e nunca entrega código sem testes"
```

Um agente não sabe só usar uma biblioteca. Ele raciocina sobre trade-offs, pergunta
antes de assumir, delega quando necessário e tem um lema que reflete seus valores.

### Skills são frameworks e bibliotecas, não pessoas

Uma skill é conhecimento técnico especializado sobre uma ferramenta específica —
padrões de uso, armadilhas, decisões de arquitetura, exemplos de código. Ela não
tem opinião, não tem persona. Ela é um manual de boas práticas que um agente *carrega*
quando precisa.

```
Skills são REFERÊNCIAS que agentes consultam.
Agentes são PROFISSIONAIS que tomam decisões.
```

### Instruções customizadas são contratos de contexto

Instruções (`.github/instructions/*.instructions.md`) são regras automáticas que o
Copilot aplica quando o contexto bate com o glob `applyTo:`. Não precisam ser
invocadas — são silenciosas e sempre ativas.

Use para: padrões de testes, convenções de nomenclatura, regras de estilo por tipo
de arquivo.

### Prompt files são automações de tarefas recorrentes

Prompt files (`.github/prompts/*.prompt.md`) são atalhos para tarefas que você faz
repetidamente. Não são agentes nem skills — são **checklists executáveis** para
workflows como "criar testes para um bug" ou "fazer code review de um PR".

---

## Anatomia de cada artefato

### `.github/agents/<nome>.agent.md` — Persona

```markdown
---
name: Nome do Agente
description: >
  Quando invocar este agente. Uma frase objetiva descrevendo o domínio
  e os casos de uso principais.
tools:
  - read
  - edit
  - write
  - search/codebase
  - run/terminal
agents:
  - Outro Agente    # agentes que este pode invocar
handoffs:
  - label: Texto do botão de handoff
    agent: Destino
    prompt: Instrução de transição.
    send: false
---

# Persona

Você é **[Nome]**, [cargo] com [N] anos de experiência em [domínio].
[2-3 frases descrevendo valores, estilo de trabalho e forma de pensar.]

Seu lema: *"[frase que resume a filosofia do agente]"*

## Habilidades e domínios

[Lista de competências — inclua aqui o conhecimento de skills relevantes,
 seja embutido (para skills de uso frequente) ou por referência (para skills
 opcionais que o agente carrega quando necessário).]

## Fluxo de trabalho

[Passos concretos que o agente segue para as tarefas principais.]

## Quando delegar

[Lista clara de casos em que este agente passa o controle para outro.]
```

**Regras para personas:**
- Sempre dê um nome real ao agente (Lucas, Beatriz, Rafael...)
- O lema deve refletir um valor inegociável — não uma descrição de tarefa
- Skills de uso frequente ficam embutidas no corpo do agente
- Skills opcionais são referenciadas por caminho para carregamento sob demanda
- Agentes orquestram outros agentes — defina claramente quando delegar

---

### `.opencode/skills/<nome>/SKILL.md` — Referência técnica

> **Nota:** `.github/skills/` é um symlink para `.opencode/skills/`. Sempre crie
> arquivos em `.opencode/skills/` e use esse caminho no `git add`.

```markdown
---
name: nome-da-skill          # deve bater exatamente com o nome do diretório
description: >
  O que esta skill cobre. Quando um agente deve carregá-la.
  Seja específico sobre o caso de uso.
argument-hint: "[contexto ou tarefa específica]"
---

# [Biblioteca/Framework] — Subtítulo focado no uso

## Stack obrigatória
[Dependências com versões mínimas]

## [Conceito central #1]
[Padrão canônico com exemplo de código. Sempre mostre o correto E o errado.]

## [Conceito central #2]
...

## Testes
[Como testar código que usa esta skill — fixtures, mocks, dados sintéticos]

## Regras de uso
[Lista de DOs and DON'Ts — objetiva, sem explicação longa]
```

**Regras para skills:**
- Nome do diretório = campo `name` no frontmatter (exato, sem espaços)
- Sempre inclua seção de testes — skill sem testes é incompleta
- Mostre sempre o padrão correto E o errado lado a lado
- Skills não têm persona — são referências neutras
- Granularidade: uma skill por biblioteca/framework, não por funcionalidade

---

### `.github/instructions/<contexto>.instructions.md` — Contrato automático

```markdown
---
applyTo: "tests/**/*.py,**/test_*.py"
---

# [Título do contrato]

[Regras que o Copilot deve seguir automaticamente quando o contexto bate com o glob.]
```

**Regras para instruções:**
- `applyTo:` usa glob — seja preciso (não use `**/*` sem necessidade)
- Use para padrões que devem ser aplicados *sempre*, sem invocação manual
- Casos de uso típicos: padrões de teste, convenções de nomenclatura, regras de linting

---

### `.github/prompts/<tarefa>.prompt.md` — Automação de tarefa recorrente

```markdown
---
mode: agent                  # "agent" usa o agente padrão; "ask" apenas responde
description: Descrição curta para aparecer na lista de prompts (/nome)
---

# [Título da tarefa]

[Contexto da tarefa — o que esta automação faz e quando usar]

## Entrada esperada

[O que o usuário deve fornecer ao invocar este prompt. Ex: descrição do bug, link do PR]

## Passos

[Sequência de ações que o agente deve executar. Seja imperativo e específico.]

1. [Passo 1]
2. [Passo 2]
...

## Critérios de saída

[O que deve estar pronto quando o prompt terminar — checklist objetiva]
```

**Regras para prompt files:**
- Nomes em `kebab-case` descrevendo a ação: `bug-to-test.prompt.md`
- `mode: agent` para tarefas que envolvem edição de código; `mode: ask` para análise
- Sempre defina "Entrada esperada" — o que o usuário precisa fornecer
- Sempre defina "Critérios de saída" — o que "feito" significa nesta tarefa
- Casos de uso típicos: bug → teste, code review, refatoração guiada, geração de docs

---

## Mapa de decisão

```
O que você precisa criar?
│
├── Um profissional que raciocina e toma decisões
│   └── → Agente (.github/agents/*.agent.md)
│
├── Um manual de boas práticas de uma biblioteca/framework
│   └── → Skill (.opencode/skills/<nome>/SKILL.md)
│
├── Uma regra que deve ser aplicada automaticamente por tipo de arquivo
│   └── → Instrução (.github/instructions/*.instructions.md)
│
└── Uma tarefa repetitiva que você quer executar com /comando
    └── → Prompt file (.github/prompts/*.prompt.md)
```

---

## Exemplo de projeto bem estruturado

```
.github/
├── agents/
│   ├── desenvolvedor.agent.md     # Lucas — generalista Python, orquestra outros
│   ├── scraper.agent.md           # Beatriz — especialista em extração de dados web
│   ├── engenheiro-dados.agent.md  # Rafael — pipelines analíticos (Polars/DuckDB/Spark)
│   └── documentador.agent.md     # Ana — documentação MkDocs com MCP Playwright
│
├── instructions/
│   └── tests.instructions.md     # applyTo: tests/**/*.py — padrões pytest
│
├── prompts/
│   ├── bug-to-test.prompt.md     # /bug-to-test — cria teste reprodutor de bug
│   ├── code-review.prompt.md     # /code-review — revisa PR com checklist
│   └── new-package.prompt.md     # /new-package — scaffolding de novo pacote
│
└── skills/ → symlink para ../.opencode/skills/

.opencode/skills/
├── project-commands/SKILL.md     # uv, taskipy, comandos do projeto
├── httpx/SKILL.md                # clientes HTTP com retry
├── polars/SKILL.md               # lazy evaluation, expressões
├── duckdb/SKILL.md               # SQL analítico em arquivos
├── pyspark/SKILL.md              # processamento distribuído
└── webscraping/SKILL.md          # selectolax, bs4, playwright
```

### Relação entre camadas

```
Usuário invoca agente → Agente carrega skills relevantes
                      → Agente segue instruções automáticas (por glob)
                      → Agente usa prompt files como guias de tarefa
                      → Agente delega para subagentes especializados
```

---

## Anti-padrões comuns

### Agente que é um wrapper de biblioteca
```
ERRADO: "Agente Polars — processa dados com Polars"
        (isso é uma skill, não um agente)

CERTO:  "Rafael — engenheiro de dados que decide QUANDO usar Polars vs DuckDB vs Spark,
         sabe quais trade-offs importam e entrega pipelines com schema validado na borda"
```

### Skill com persona
```
ERRADO: skill httpx com seção "Quando eu devo usar httpx, eu prefiro..."
        (skills são neutras — não têm opinião, não têm eu)

CERTO:  skill httpx com padrões canônicos, exemplos e lista de regras objetivas
```

### Instrução para tudo
```
ERRADO: applyTo: "**/*"  — regras globais demais perdem precisão

CERTO:  applyTo: "tests/**/*.py,**/test_*.py"  — escopo preciso
```

### Prompt file como documentação
```
ERRADO: prompt file que apenas explica como fazer algo

CERTO:  prompt file que executa a tarefa — com passos imperativos e critérios de saída
```

---

## Checklist para nova estrutura de IA

Ao iniciar um projeto novo, passe por este checklist:

- [ ] Identifiquei os **perfis profissionais** que este projeto precisa → criar agentes
- [ ] Identifiquei as **bibliotecas/frameworks** mais usados → criar skills
- [ ] Identifiquei **padrões por tipo de arquivo** que devem ser automáticos → criar instruções
- [ ] Identifiquei **tarefas repetitivas** que podem virar comandos → criar prompt files
- [ ] Cada agente tem nome, lema e sabe quando delegar
- [ ] Cada skill tem seção de testes e exemplos correto/errado
- [ ] O `AGENTS.md` (ou `copilot-instructions.md`) lista todos os artefatos com caminho
- [ ] `.github/skills/` aponta para `.opencode/skills/` via symlink (se usar OpenCode)
