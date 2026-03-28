---
name: polars
description: >
  Padrões e boas práticas para processamento de dados com Polars neste monorepo,
  com foco em lazy evaluation, expressões encadeadas e performance.
  Use quando precisar ler, transformar, agregar ou exportar dados tabulares.
argument-hint: "[transformação ou pipeline de dados a implementar]"
---

# Polars — Processamento de dados com lazy evaluation

Este monorepo usa **Polars** como biblioteca de processamento de dados. Toda manipulação
de dados tabulares deve seguir os padrões abaixo, priorizando o modo lazy.

## Stack obrigatória

```toml
dependencies = [
    "polars>=1.0",
    "pyarrow>=15",   # para I/O Parquet e Arrow
]
```

## Princípio central: sempre lazy

Use `.lazy()` para construir pipelines. Chame `.collect()` apenas no final,
uma única vez. Isso permite ao otimizador de queries do Polars reordenar,
fundir e paralelizar operações.

```python
import polars as pl

# correto — lazy pipeline, collect no final
result = (
    pl.scan_parquet("data/*.parquet")   # lazy por padrão
    .filter(pl.col("status") == "active")
    .with_columns(
        (pl.col("price") * pl.col("quantity")).alias("revenue"),
        pl.col("created_at").dt.year().alias("year"),
    )
    .group_by("year")
    .agg(
        pl.col("revenue").sum().alias("total_revenue"),
        pl.col("id").count().alias("order_count"),
    )
    .sort("year")
    .collect()  # única chamada de materialização
)

# evitar — eager desnecessário no meio do pipeline
df = pl.read_parquet("data/*.parquet")  # materializa tudo
df = df.filter(pl.col("status") == "active")  # re-cria DataFrame
```

## Leitura de dados

Prefira sempre os scanners lazy em vez dos leitores eager.

```python
# preferir
lf = pl.scan_parquet("path/to/file.parquet")
lf = pl.scan_csv("path/to/file.csv", separator=";", infer_schema_length=1000)
lf = pl.scan_ndjson("path/to/file.ndjson")

# usar eager apenas para dados pequenos em memória
df = pl.from_dicts(records)
df = pl.DataFrame({"col_a": [1, 2, 3], "col_b": ["x", "y", "z"]})
```

## Expressões — regras

1. Use `pl.col()` em vez de acesso por string direto onde possível
2. Encadeie expressões dentro de `with_columns` — evite múltiplas chamadas separadas
3. Use `pl.lit()` para valores literais em expressões
4. Use `pl.when().then().otherwise()` para lógica condicional (evite UDFs)

```python
# correto — expressões encadeadas em único with_columns
lf = lf.with_columns(
    pl.col("price").cast(pl.Float64).alias("price_f64"),
    (pl.col("price") * 1.1).alias("price_with_tax"),
    pl.when(pl.col("country") == "BR")
      .then(pl.col("price") * 0.9)
      .otherwise(pl.col("price"))
      .alias("price_local"),
)

# evitar — múltiplos with_columns separados sem necessidade
lf = lf.with_columns(pl.col("price").cast(pl.Float64).alias("price_f64"))
lf = lf.with_columns((pl.col("price_f64") * 1.1).alias("price_with_tax"))
```

## Joins

```python
# join lazy — nunca coleta antes de fazer join
result = (
    orders.lazy()
    .join(customers.lazy(), on="customer_id", how="left")
    .join(products.lazy(), left_on="product_id", right_on="id", how="inner")
    .collect()
)
```

## Agregações

```python
# agg com múltiplas métricas em um único group_by
summary = (
    lf.group_by(["region", "year"])
    .agg(
        pl.col("revenue").sum().alias("total_revenue"),
        pl.col("revenue").mean().alias("avg_revenue"),
        pl.col("revenue").std().alias("std_revenue"),
        pl.col("customer_id").n_unique().alias("unique_customers"),
    )
    .sort(["region", "year"])
    .collect()
)
```

## UDFs — usar com moderação

UDFs Python quebram o paralelismo interno do Polars. Use apenas quando não há expressão nativa equivalente.

```python
# evitar quando há alternativa nativa
df.with_columns(
    pl.col("name").map_elements(lambda x: x.upper(), return_dtype=pl.String)
)

# preferir a expressão nativa
df.with_columns(pl.col("name").str.to_uppercase())
```

## Escrita e exportação

```python
# Parquet particionado — preferido para grandes volumes
df.write_parquet("output/data.parquet", compression="zstd")

# CSV — apenas para interoperabilidade com sistemas legados
df.write_csv("output/data.csv", separator=";")

# sink lazy — sem coletar em memória (Polars >=0.19)
lf.sink_parquet("output/data.parquet", compression="zstd")
```

## Schema e tipos

Declare schemas explícitos ao ler dados externos. Nunca confie cegamente na inferência.

```python
schema = {
    "id": pl.UInt64,
    "name": pl.String,
    "price": pl.Decimal(precision=10, scale=2),
    "created_at": pl.Datetime("us", "UTC"),
    "active": pl.Boolean,
}

lf = pl.scan_csv("data.csv", schema=schema)
```

## Testes com Polars

```python
def test_revenue_pipeline_calculates_correct_total():
    input_df = pl.DataFrame({
        "price": [10.0, 20.0, 30.0],
        "quantity": [2, 1, 3],
        "status": ["active", "inactive", "active"],
    })
    result = calculate_revenue(input_df.lazy()).collect()
    assert result["revenue"].sum() == pytest.approx(110.0)
    assert len(result) == 2  # apenas os "active"
```
