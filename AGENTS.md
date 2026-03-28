# GitHub Copilot — Instruções do Workspace

Guidelines para agentes e assistentes de IA trabalhando neste monorepo Python.

## Estrutura do repositório

```
python-monorepo-template/
├── pyproject.toml          # workspace root: ruff, pytest, taskipy
├── uv.lock
└── packages/
    ├── my-sample-package/                     # proxy package — re-exporta todos os providers
    ├── my-sample-package-provider-core/       # Python >=3.11, módulo: core
    ├── my-sample-package-provider-app/        # Python >=3.12, módulo: app
    └── my-sample-package-provider-standalone/ # Python >=3.13, módulo: standalone
```

Cada pacote contém: `src/<module>/`, `tests/`, `pyproject.toml`, `.python-version`, `README.md`.

## Toolchain

- Sempre use `uv` — nunca `pip`, `python -m pip` ou `poetry`.
- Nunca use `uv run --package X task Y` (causa recursão infinita); use `uv run --directory packages/X task Y`.
- Para todos os comandos de build/test/lint, consulte a skill `project-commands` em `.github/skills/project-commands/SKILL.md`.

## Estilo de código

- Comprimento de linha: 120 chars. Indentação: 4 espaços. Aspas: duplas (`"`).
- Anotações de tipo completas em todas as funções e métodos públicos. Use genéricos nativos (`list[str]`, `dict[str, int]`).
- Nomenclatura: `snake_case` para módulos/funções, `PascalCase` para classes, `UPPER_SNAKE` para constantes, `_underscore_inicial` para privados.
- Docstrings no estilo Google em toda API pública. `-> None` obrigatório no `__init__`.
- Levante exceções específicas (`ValueError`, `RuntimeError`, etc.) com mensagens descritivas.
- Nunca `except:` simples. Nunca `assert False` — use `pytest.raises` nos testes.
- Dependências opcionais protegidas com `try/except ImportError`.

## Testes

> Para regras detalhadas de nomenclatura, estilo e boas práticas de testes, consulte obrigatoriamente:
> `.github/instructions/tests.instructions.md`

Resumo rápido:
- Apenas funções (`def test_*`), nunca classes.
- Use `pytest.raises` para exceções esperadas.
- Nomes descrevem comportamento: `test_clamp_above_max`.
- Mínimo de mocks — prefira objetos reais e fixtures leves.

## Versionamento

- Dinâmico via `hatch-vcs`. Nunca fixe versões manualmente.
- Formato de tag: `<package-name>:<version>` — ex.: `my-sample-package-provider-core:1.2.3`.

## Armadilhas comuns

- Nunca edite `src/<module>/_version.py` — gerado automaticamente pelo `hatch-vcs`.
- Dependências de desenvolvimento ficam em `[dependency-groups] dev = [...]` no `pyproject.toml` raiz.

## Agentes disponíveis

Agentes são **personas** — profissionais com nome, valores e domínio de atuação.
Não são wrappers de bibliotecas. Cada agente raciocina, delega e toma decisões.

| Agente | Persona | Arquivo | Responsabilidade |
|--------|---------|---------|-----------------|
| Desenvolvedor Python | Lucas | `.github/agents/desenvolvedor.agent.md` | Generalista Python: implementação, refatoração, bugs, testes. Orquestra os demais agentes. |
| Scraper | Beatriz | `.github/agents/scraper.agent.md` | Extração de dados web: selectolax, BeautifulSoup4, Playwright. Inspeciona antes de codificar. |
| Engenheiro de Dados | Rafael | `.github/agents/engenheiro-dados.agent.md` | Pipelines analíticos com Polars, DuckDB e PySpark. Decide a stack certa para cada escala. |
| Documentador | Ana | `.github/agents/documentador.agent.md` | Documentação MkDocs Material. Consulta docs oficiais via MCP Playwright antes de escrever. |

## Skills disponíveis

Skills são **referências técnicas** de bibliotecas e frameworks — padrões de uso,
armadilhas e exemplos de código que os agentes carregam quando necessário.

| Skill | Arquivo | Quando usar |
|-------|---------|-------------|
| project-commands | `.github/skills/project-commands/SKILL.md` | Build, test, lint, format, docs — comandos uv/taskipy do projeto |
| httpx | `.github/skills/httpx/SKILL.md` | Clientes HTTP com retry, timeout e autenticação |
| polars | `.github/skills/polars/SKILL.md` | Pipelines de dados com Polars lazy evaluation |
| duckdb | `.github/skills/duckdb/SKILL.md` | SQL analítico sobre arquivos Parquet/CSV/JSON |
| pyspark | `.github/skills/pyspark/SKILL.md` | Processamento distribuído para dados >50GB |
| webscraping | `.github/skills/webscraping/SKILL.md` | Extração de dados web: decisão de stack e padrões |
| copilot-project-structure | `.github/skills/copilot-project-structure/SKILL.md` | Filosofia e guia para estruturar projetos com agentes, skills, instruções e prompt files |

## Instruções customizadas por contexto

| Contexto | Arquivo | Aplica-se a |
|----------|---------|-------------|
| Testes | `.github/instructions/tests.instructions.md` | `tests/**/*.py`, `**/test_*.py` |
