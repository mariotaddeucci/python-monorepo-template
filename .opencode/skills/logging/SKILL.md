---
name: logging
description: >
  Padrões e boas práticas para logging Python neste monorepo.
  Use quando precisar configurar loggers, definir níveis, formatar mensagens,
  adicionar contexto estruturado ou testar saída de logs em código de produção.
argument-hint: "[módulo ou funcionalidade que precisa de logging]"
---

# Logging — Python stdlib com contexto e rastreabilidade

Este monorepo usa o módulo **`logging`** da stdlib como padrão. Nenhuma dependência
externa de logging é necessária para o caso geral. O objetivo é sempre: logs que
ajudam a diagnosticar problemas em produção sem precisar reproduzir o erro.

## Princípio central: logger por módulo

Cada módulo declara seu próprio logger no topo do arquivo, usando `__name__`.
Isso cria uma hierarquia automática que segue a estrutura de pacotes e permite
controle granular de nível por namespace.

```python
import logging

logger = logging.getLogger(__name__)
```

Nunca use `logging.info(...)` diretamente — isso escreve no root logger e
polui qualquer aplicação que importe o pacote.

```python
# correto — logger do módulo
logger = logging.getLogger(__name__)
logger.info("processando pedido", extra={"order_id": order_id})

# nunca — root logger em código de biblioteca
logging.info("processando pedido")
```

## Configuração — responsabilidade da aplicação, não da biblioteca

Pacotes de biblioteca **nunca** configuram handlers ou formatters. Isso é
responsabilidade exclusiva da aplicação que consome a biblioteca.
A única exceção é adicionar um `NullHandler` para silenciar avisos.

```python
# em src/<modulo>/__init__.py de um pacote de biblioteca
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
```

Configuração de handlers fica no entrypoint da aplicação:

```python
# em scripts, CLIs ou main.py — nunca dentro de src/
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
```

## Níveis — quando usar cada um

| Nível | Quando usar |
|-------|-------------|
| `DEBUG` | Informação detalhada útil apenas durante desenvolvimento. Valores intermediários, contadores de loop, estado interno. |
| `INFO` | Confirmação de que o fluxo principal está funcionando. Início/fim de operações significativas, resultados esperados. |
| `WARNING` | Algo inesperado aconteceu mas o sistema continua funcionando. Configuração ausente com fallback, deprecação usada. |
| `ERROR` | Uma operação falhou. O erro foi tratado mas a funcionalidade não completou. |
| `CRITICAL` | Falha grave — o sistema não consegue continuar. Use com moderação. |

```python
# DEBUG — detalhes de desenvolvimento
logger.debug("payload recebido: %s", payload)

# INFO — progresso normal do fluxo
logger.info("pedido %s processado com sucesso", order_id)

# WARNING — situação anômala mas recuperável
logger.warning("cache ausente para chave %r, buscando na origem", key)

# ERROR — falha tratada, operação não completou
logger.error("falha ao enviar email para %s: %s", recipient, exc, exc_info=True)

# CRITICAL — sistema comprometido
logger.critical("conexão com banco de dados perdida após %d tentativas", max_retries)
```

## Mensagens com contexto — % formatting, não f-strings

Use sempre `%`-formatting nos argumentos do logger. O Python só interpola a string
se o nível estiver ativo — f-strings são sempre avaliadas, mesmo quando o log
seria descartado.

```python
order_id = "abc-123"
items = [1, 2, 3]

# correto — lazy evaluation
logger.debug("processando pedido %s com %d itens", order_id, len(items))

# evitar — avaliado mesmo se DEBUG estiver desativado
logger.debug(f"processando pedido {order_id} com {len(items)} itens")
```

## `extra` — contexto estruturado

Use `extra` para adicionar campos estruturados à mensagem. Útil com formatters JSON
e sistemas de observabilidade (Datadog, CloudWatch, etc.).

```python
logger.info(
    "pedido processado",
    extra={
        "order_id": order_id,
        "user_id": user_id,
        "items_count": len(items),
        "duration_ms": elapsed_ms,
    },
)
```

## `exc_info` — incluir stacktrace

Passe `exc_info=True` (ou a exceção diretamente) em `ERROR` e `CRITICAL` para
incluir o traceback completo. Sem isso, o log não tem informação suficiente para
diagnosticar o problema.

```python
try:
    result = process_order(order_id)
except ValueError as exc:
    # erro esperado — loga sem stacktrace se a mensagem já é suficiente
    logger.error("pedido %s inválido: %s", order_id, exc)
    raise
except Exception as exc:
    # erro inesperado — sempre inclui stacktrace
    logger.error("falha inesperada ao processar pedido %s", order_id, exc_info=True)
    raise
```

## Padrão para funções com operações significativas

Logue entrada e saída de operações que podem falhar em produção.
Não logue operações triviais — ruído é tão prejudicial quanto silêncio.

```python
import logging
from typing import Any

logger = logging.getLogger(__name__)


def fetch_order(order_id: str) -> dict[str, Any]:
    """Busca pedido na API externa.

    Args:
        order_id: Identificador do pedido.

    Returns:
        Dados do pedido.

    Raises:
        RuntimeError: Se a API retornar erro.
    """
    logger.debug("buscando pedido %s", order_id)

    try:
        response = client.get(f"/orders/{order_id}")
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "API retornou %d para pedido %s",
            exc.response.status_code,
            order_id,
            exc_info=True,
        )
        raise RuntimeError(f"falha ao buscar pedido {order_id!r}") from exc

    logger.info("pedido %s recuperado com sucesso", order_id)
    return response.json()
```

## Logger com contexto persistente — `LoggerAdapter`

Quando um componente processa sempre com o mesmo contexto (ex: `user_id`, `request_id`),
use `LoggerAdapter` para não repetir o `extra` em cada chamada.

```python
import logging


class OrderLogger(logging.LoggerAdapter):
    """Logger com contexto de pedido pré-fixado."""

    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


def process_order(order_id: str, user_id: str) -> None:
    log = OrderLogger(
        logging.getLogger(__name__),
        {"order_id": order_id, "user_id": user_id},
    )
    log.info("iniciando processamento")  # inclui order_id e user_id automaticamente
    # ...
    log.info("processamento concluído")
```

## Testes — capturar logs com `caplog`

Use a fixture `caplog` do pytest. Nunca teste logs via mock de `logging` —
isso acopla os testes à implementação interna.

```python
import logging
import pytest


def test_fetch_order_logs_error_on_http_failure(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR, logger="meu_modulo.orders"):
        with pytest.raises(RuntimeError):
            fetch_order_with_failing_client("order-999")

    assert any("order-999" in r.message for r in caplog.records)
    assert caplog.records[-1].levelno == logging.ERROR


def test_fetch_order_logs_success_at_info(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="meu_modulo.orders"):
        fetch_order_with_mock_client("order-123")

    assert any("order-123" in r.message for r in caplog.records)
```

## Regras de uso

- `logger = logging.getLogger(__name__)` — sempre, no topo do módulo
- Nunca `logging.info(...)` em código de biblioteca — sempre o logger do módulo
- Nunca `logging.basicConfig(...)` dentro de `src/` — só no entrypoint da aplicação
- `NullHandler` no `__init__.py` de pacotes de biblioteca
- `%`-formatting nos argumentos — nunca f-strings dentro do `logger.*(...)`
- `exc_info=True` em todo `logger.error` de exceções inesperadas
- `extra={}` para campos estruturados que sistemas de observabilidade vão indexar
- `caplog` no pytest — nunca mock de `logging` para testar saída de logs
- Não logue em todo lugar — ruído dificulta diagnóstico tanto quanto silêncio
