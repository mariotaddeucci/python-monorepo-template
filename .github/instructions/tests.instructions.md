---
name: Testes Python
description: Convenções de nomenclatura, estilo e boas práticas para arquivos de teste pytest neste monorepo.
applyTo: "tests/**/*.py,**/test_*.py"
---

# Regras para arquivos de teste

## Nomenclatura de funções

Use **sempre** funções, nunca classes. O nome deve descrever o comportamento testado em linguagem natural:

```
test_<unidade>_<comportamento_esperado>
test_<unidade>_<comportamento_esperado>_when_<contexto>
test_<unidade>_raises_<excecao>_when_<condicao>
```

Exemplos corretos:
```python
def test_clamp_returns_max_when_value_exceeds_upper_bound(): ...
def test_parse_raises_value_error_when_input_is_empty(): ...
def test_calculate_tax_when_region_is_exempt(): ...
```

Exemplos **incorretos** — nunca use:
```python
class TestClamp:          # nunca classes
    def test_clamp(): ... # nome vago demais

def test_1(): ...         # sem semântica
def test_clamp(): ...     # sem descrição do comportamento
```

## Mínimo de mocks

Prefira objetos reais e fixtures leves. Mocks introduzem acoplamento oculto e fragilidade.

**Use objetos reais quando:**
- O objeto é simples de instanciar
- Não há dependências externas (rede, disco, banco de dados)
- O custo de setup é baixo

**Use mocks apenas quando:**
- A dependência é externa e não-determinística (API, relógio, I/O)
- O teste ficaria lento sem mock (>100ms)
- A dependência dispara efeitos colaterais irreversíveis

```python
# correto — objeto real
def test_add_item_increases_cart_total():
    cart = Cart()
    cart.add(Item(price=10.0))
    assert cart.total == 10.0

# correto — mock justificado (I/O externo)
def test_fetch_user_returns_none_when_api_fails(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **kw: Response(500))
    assert fetch_user(1) is None
```

## Exceções esperadas

Use `pytest.raises` como gerenciador de contexto. Sempre valide a mensagem quando ela for relevante:

```python
def test_divide_raises_zero_division_error_when_divisor_is_zero():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        divide(10, 0)
```

Nunca use `assert False` ou `try/except` em testes.

## Fixtures

- Declare fixtures no arquivo `conftest.py` do pacote quando reutilizadas em múltiplos arquivos
- Fixtures locais (usadas em um único arquivo) ficam no próprio arquivo de teste
- Nomes de fixtures descrevem o estado, não o tipo: `empty_cart`, `authenticated_user`, `parsed_config`

```python
# conftest.py
@pytest.fixture
def empty_cart() -> Cart:
    return Cart()

@pytest.fixture
def cart_with_one_item(empty_cart: Cart) -> Cart:
    empty_cart.add(Item(price=9.99))
    return empty_cart
```

## Parametrize

Use `@pytest.mark.parametrize` para cobrir múltiplos casos sem duplicar código:

```python
@pytest.mark.parametrize(
    ("value", "low", "high", "expected"),
    [
        (5, 0, 10, 5),   # dentro dos limites
        (-1, 0, 10, 0),  # abaixo do mínimo
        (15, 0, 10, 10), # acima do máximo
    ],
)
def test_clamp_returns_bounded_value(value: int, low: int, high: int, expected: int) -> None:
    assert clamp(value, low, high) == expected
```

## Asserções

- Uma asserção principal por teste (regra da responsabilidade única)
- Use comparações diretas — evite boilerplate com `assertTrue(x == y)` estilo unittest
- Adicione mensagens de asserção apenas quando o valor padrão do pytest não for claro o suficiente
