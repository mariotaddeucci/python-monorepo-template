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

| Agente | Arquivo | Responsabilidade |
|--------|---------|-----------------|
| Documentador | `.github/agents/documentador.agent.md` | Gerar e manter documentação MkDocs Material consultando a documentação oficial via Playwright |

## Skills disponíveis

| Skill | Arquivo | Quando usar |
|-------|---------|-------------|
| project-commands | `.github/skills/project-commands/SKILL.md` | Build, test, lint, format, docs |

## Instruções customizadas por contexto

| Contexto | Arquivo | Aplica-se a |
|----------|---------|-------------|
| Testes | `.github/instructions/tests.instructions.md` | `tests/**/*.py`, `**/test_*.py` |
