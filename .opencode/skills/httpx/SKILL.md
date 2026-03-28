---
name: httpx
description: >
  Padrões e boas práticas para HTTP com httpx, httpx-retries e tenacity neste monorepo.
  Use quando precisar criar clientes HTTP, configurar retry/backoff, timeouts, autenticação,
  streaming de respostas ou testar código que faz requisições externas.
argument-hint: "[endpoint ou funcionalidade a implementar]"
---

# httpx — HTTP moderno com retry e resiliência

Este monorepo usa **httpx** como cliente HTTP padrão. Toda comunicação com APIs externas
deve seguir os padrões abaixo.

## Stack obrigatória

```toml
# pyproject.toml do pacote
dependencies = [
    "httpx>=0.27",
    "httpx-retries>=0.4",   # retry nativo para httpx
    "tenacity>=9",           # retry de alto nível com backoff
]
```

## Cliente síncrono padrão

Use sempre `httpx.Client` como gerenciador de contexto. Nunca instancie sem `with`.

```python
import httpx
from httpx_retries import RetryTransport, Retry

def build_client(base_url: str, timeout: float = 10.0) -> httpx.Client:
    """Cria cliente HTTP com retry e timeout configurados."""
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist={429, 500, 502, 503, 504},
        raise_on_status=False,
    )
    transport = RetryTransport(retry=retry)
    return httpx.Client(
        base_url=base_url,
        timeout=httpx.Timeout(timeout, connect=5.0),
        transport=transport,
        headers={"User-Agent": "my-package/1.0"},
    )

# uso
with build_client("https://api.example.com") as client:
    response = client.get("/users/1")
    response.raise_for_status()
    data = response.json()
```

## Cliente assíncrono padrão

```python
import httpx
from httpx_retries import AsyncRetryTransport, Retry

def build_async_client(base_url: str, timeout: float = 10.0) -> httpx.AsyncClient:
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist={429, 500, 502, 503, 504})
    transport = AsyncRetryTransport(retry=retry)
    return httpx.AsyncClient(
        base_url=base_url,
        timeout=httpx.Timeout(timeout, connect=5.0),
        transport=transport,
    )

async def fetch_user(user_id: int) -> dict:
    async with build_async_client("https://api.example.com") as client:
        response = await client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()
```

## Retry com tenacity (lógica de negócio)

Use `tenacity` quando a lógica de retry depende do conteúdo da resposta, não só do status HTTP.

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    reraise=True,
)
def call_with_business_retry(client: httpx.Client, path: str) -> dict:
    response = client.get(path)
    response.raise_for_status()
    return response.json()
```

## Timeouts

Sempre use `httpx.Timeout` com valores explícitos. Nunca use `None` (sem timeout).

```python
# correto — valores separados por fase
timeout = httpx.Timeout(read=30.0, write=10.0, connect=5.0, pool=5.0)

# aceitável — timeout global
timeout = httpx.Timeout(10.0)

# nunca — sem timeout
timeout = None
```

## Tratamento de erros

```python
try:
    response = client.get("/endpoint")
    response.raise_for_status()
except httpx.HTTPStatusError as exc:
    # erro HTTP (4xx, 5xx)
    raise RuntimeError(f"HTTP {exc.response.status_code}: {exc.response.text}") from exc
except httpx.TimeoutException as exc:
    raise RuntimeError("Timeout ao conectar com a API") from exc
except httpx.RequestError as exc:
    raise RuntimeError(f"Erro de rede: {exc}") from exc
```

## Testes — MockTransport

Nunca faça requisições reais nos testes. Use `httpx.MockTransport` ou `respx`.

```python
import httpx
import pytest

def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/users/1":
        return httpx.Response(200, json={"id": 1, "name": "Alice"})
    return httpx.Response(404)

def test_fetch_user_returns_name():
    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport, base_url="https://api.example.com") as client:
        response = client.get("/users/1")
        assert response.json()["name"] == "Alice"
```

## Regras de uso

- Nunca use `requests` — use sempre `httpx`
- Nunca faça `httpx.get(url)` diretamente em produção — use um cliente com retry configurado
- Rate limit (429) deve sempre estar em `status_forcelist`
- Logue o `request_id` do header de resposta quando disponível para rastreabilidade
- Use `httpx.URL` para construir URLs dinamicamente, nunca f-strings com partes de URL
