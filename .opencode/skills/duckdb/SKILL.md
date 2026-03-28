---
name: duckdb
description: >
  Padrões e boas práticas para SQL analítico com DuckDB neste monorepo.
  Use quando precisar executar queries SQL sobre arquivos Parquet/CSV/JSON,
  fazer exploração analítica em memória, ou integrar com Polars via Arrow.
argument-hint: "[query ou pipeline analítico a implementar]"
---

# DuckDB — SQL analítico em arquivos e em memória

Este monorepo usa **DuckDB** para queries SQL analíticas sobre arquivos e dados em memória.
DuckDB é a escolha preferida para exploração ad-hoc, joins complexos e agregações sobre
arquivos Parquet/CSV/JSON sem necessidade de servidor.

## Stack obrigatória

```toml
dependencies = [
    "duckdb>=1.0",
    "polars>=1.0",   # integração zero-copy via Arrow
    "pyarrow>=15",   # serialização Arrow
]
```

## Conexão — regras básicas

Use sempre `with duckdb.connect()` como gerenciador de contexto para garantir fechamento
da conexão. Para processamento em memória (padrão), não passe caminho de arquivo.

```python
import duckdb

# em memória — padrão para processamento e testes
with duckdb.connect() as conn:
    result = conn.execute("SELECT 42 AS answer").fetchdf()

# arquivo persistente — apenas quando necessário manter estado entre execuções
with duckdb.connect("analytics.duckdb") as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS orders AS SELECT * FROM 'data/*.parquet'")
```

## Leitura de arquivos

DuckDB lê arquivos diretamente via SQL — sem carregar em memória antes.

```python
import duckdb
import polars as pl

with duckdb.connect() as conn:
    # Parquet — preferido para dados analíticos
    result = conn.execute("""
        SELECT *
        FROM read_parquet('data/orders/*.parquet')
        WHERE status = 'completed'
        LIMIT 100
    """).pl()  # retorna Polars DataFrame diretamente via Arrow

    # CSV com opções
    result = conn.execute("""
        SELECT *
        FROM read_csv('data/users.csv', delim=';', header=true, auto_detect=true)
    """).pl()

    # JSON/NDJSON
    result = conn.execute("""
        SELECT *
        FROM read_json('data/events.ndjson', auto_detect=true)
    """).pl()

    # glob de múltiplos arquivos
    result = conn.execute("""
        SELECT filename, count(*) AS row_count
        FROM read_parquet('data/**/*.parquet', filename=true)
        GROUP BY filename
    """).pl()
```

## Integração com Polars — zero-copy via Arrow

DuckDB e Polars compartilham memória via Arrow. Prefira `.pl()` para retornar Polars
DataFrames e `conn.register()` para passar DataFrames Polars como tabelas virtuais.

```python
import duckdb
import polars as pl

orders = pl.scan_parquet("data/orders/*.parquet").collect()
customers = pl.scan_parquet("data/customers/*.parquet").collect()

with duckdb.connect() as conn:
    # registrar DataFrames Polars como tabelas virtuais
    conn.register("orders", orders)
    conn.register("customers", customers)

    result = conn.execute("""
        SELECT
            c.region,
            year(o.created_at) AS year,
            sum(o.price * o.quantity) AS total_revenue,
            count(DISTINCT o.customer_id) AS unique_customers
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.status = 'completed'
        GROUP BY c.region, year
        ORDER BY c.region, year
    """).pl()
```

## Queries parametrizadas

Nunca use f-strings para interpolar valores de usuário em SQL. Use sempre parâmetros posicionais (`?`) ou nomeados (`$name`).

```python
import duckdb

def fetch_orders_by_status(status: str, min_value: float) -> pl.DataFrame:
    with duckdb.connect() as conn:
        # correto — parâmetros posicionais
        return conn.execute("""
            SELECT *
            FROM read_parquet('data/orders/*.parquet')
            WHERE status = ?
              AND price * quantity >= ?
        """, [status, min_value]).pl()

# nunca — SQL injection via f-string
def fetch_orders_unsafe(status: str) -> pl.DataFrame:
    with duckdb.connect() as conn:
        return conn.execute(f"SELECT * FROM orders WHERE status = '{status}'").pl()  # ERRADO
```

## Agregações e window functions

DuckDB suporta SQL analítico completo, incluindo window functions e funções de tempo.

```python
with duckdb.connect() as conn:
    conn.register("sales", sales_df)

    result = conn.execute("""
        SELECT
            product_id,
            sale_date,
            revenue,
            sum(revenue) OVER (
                PARTITION BY product_id
                ORDER BY sale_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative_revenue,
            revenue - lag(revenue) OVER (
                PARTITION BY product_id ORDER BY sale_date
            ) AS revenue_delta
        FROM sales
        ORDER BY product_id, sale_date
    """).pl()
```

## EXPLAIN ANALYZE — diagnóstico de performance

```python
with duckdb.connect() as conn:
    # ver plano de execução otimizado
    plan = conn.execute("""
        EXPLAIN ANALYZE
        SELECT region, sum(revenue) AS total
        FROM read_parquet('data/*.parquet')
        GROUP BY region
    """).fetchall()
    for row in plan:
        print(row[1])
```

## Criação de tabelas e persistência

```python
with duckdb.connect("warehouse.duckdb") as conn:
    # criar tabela a partir de Parquet
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders AS
        SELECT * FROM read_parquet('data/orders/*.parquet')
    """)

    # inserção incremental
    conn.execute("""
        INSERT INTO orders
        SELECT * FROM read_parquet('data/new_orders.parquet')
        WHERE id NOT IN (SELECT id FROM orders)
    """)

    # exportar resultado para Parquet
    conn.execute("""
        COPY (
            SELECT region, sum(revenue) AS total_revenue
            FROM orders
            GROUP BY region
        ) TO 'output/revenue_by_region.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
```

## Testes com DuckDB

Use sempre conexão `:memory:` nos testes. Insira dados sintéticos inline via `VALUES` ou
registre DataFrames Polars pequenos.

```python
import duckdb
import polars as pl
import pytest

def test_revenue_aggregation_sums_completed_orders_only():
    input_df = pl.DataFrame({
        "order_id": [1, 2, 3],
        "status": ["completed", "cancelled", "completed"],
        "price": [100.0, 50.0, 200.0],
        "quantity": [2, 1, 1],
    })

    with duckdb.connect() as conn:
        conn.register("orders", input_df)
        result = conn.execute("""
            SELECT sum(price * quantity) AS total_revenue
            FROM orders
            WHERE status = 'completed'
        """).pl()

    assert result["total_revenue"][0] == pytest.approx(400.0)


def test_top_customers_returns_correct_ranking():
    with duckdb.connect() as conn:
        result = conn.execute("""
            WITH data AS (
                SELECT * FROM (VALUES
                    (1, 'Alice', 500.0),
                    (2, 'Bob',   200.0),
                    (3, 'Carol', 800.0)
                ) AS t(id, name, revenue)
            )
            SELECT name, revenue
            FROM data
            ORDER BY revenue DESC
            LIMIT 2
        """).pl()

    assert result["name"].to_list() == ["Carol", "Alice"]
```

## Regras de uso

- Prefira DuckDB para queries SQL sobre arquivos — é mais rápido que carregar em Polars para queries ad-hoc
- Use `.pl()` para retornar Polars DataFrames — evita cópias desnecessárias via Arrow
- Nunca use f-strings para valores dinâmicos — sempre parâmetros posicionais
- Use `conn.register()` para passar DataFrames existentes sem serialização
- `EXPLAIN ANALYZE` antes de otimizar — não assuma gargalos
- Conexões em memória para testes, arquivos `.duckdb` apenas quando persistência é necessária
