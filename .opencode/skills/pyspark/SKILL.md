---
name: pyspark
description: >
  Padrões e boas práticas para processamento distribuído com PySpark neste monorepo.
  Use quando os dados não cabem em um único nó (>50GB tipicamente) ou quando o ambiente
  de execução é um cluster Spark. Para dados menores, prefira Polars ou DuckDB.
argument-hint: "[pipeline distribuído ou transformação em larga escala a implementar]"
---

# PySpark — Processamento distribuído em larga escala

Este monorepo usa **PySpark** exclusivamente para workloads que excedem a capacidade de
um único nó. Para dados que cabem em memória, use Polars. Para queries SQL ad-hoc sobre
arquivos, use DuckDB.

## Quando usar PySpark

```
Dados < 50GB em um nó → Polars (transformações) ou DuckDB (SQL)
Dados > 50GB ou cluster obrigatório → PySpark
```

## Stack obrigatória

```toml
dependencies = [
    "pyspark>=3.5",
    "delta-spark>=3.0",   # formato Delta Lake (opcional, para transações ACID)
    "pyarrow>=15",         # serialização Arrow para toPandas/Polars
]
```

## SparkSession — criação padronizada

Nunca acesse `SparkContext` diretamente. Use sempre `SparkSession.builder`.

```python
from pyspark.sql import SparkSession


def build_spark_session(app_name: str, local: bool = False) -> SparkSession:
    """Cria SparkSession configurada para produção ou testes locais."""
    builder = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.adaptive.enabled", "true")          # AQE — otimização automática
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.parquet.compression.codec", "zstd")
    )
    if local:
        builder = builder.master("local[2]")
    return builder.getOrCreate()
```

## DataFrame API — nunca RDD

Use sempre a DataFrame/Dataset API. RDDs são mais lentos e não se beneficiam do
Catalyst optimizer.

```python
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F

spark = build_spark_session("orders-pipeline")

# correto — DataFrame API com Catalyst optimizer
result = (
    spark.read.parquet("s3://bucket/orders/")
    .filter(F.col("status") == "completed")
    .withColumn("revenue", F.col("price") * F.col("quantity"))
    .withColumn("year", F.year("created_at"))
    .groupBy("year")
    .agg(
        F.sum("revenue").alias("total_revenue"),
        F.countDistinct("customer_id").alias("unique_customers"),
    )
    .orderBy("year")
)

# evitar — RDD quebra o optimizer
rdd = spark.sparkContext.textFile("s3://bucket/orders/")
```

## Leitura de dados

```python
# Parquet — preferido
df = spark.read.parquet("s3://bucket/data/")

# Parquet com schema explícito — evita inferência cara
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

schema = StructType([
    StructField("id", StringType(), nullable=False),
    StructField("status", StringType(), nullable=True),
    StructField("price", DoubleType(), nullable=True),
    StructField("created_at", TimestampType(), nullable=True),
])
df = spark.read.schema(schema).parquet("s3://bucket/data/")

# CSV
df = spark.read.option("header", "true").option("delimiter", ";").csv("s3://bucket/data.csv")

# Delta Lake
df = spark.read.format("delta").load("s3://bucket/delta/orders/")
```

## Transformações — boas práticas

```python
# correto — encadear transformações em um único pipeline
result = (
    df
    .filter(F.col("status").isin(["completed", "shipped"]))
    .withColumn("revenue", F.col("price") * F.col("quantity"))
    .withColumn(
        "revenue_tier",
        F.when(F.col("revenue") >= 1000, "high")
         .when(F.col("revenue") >= 100, "medium")
         .otherwise("low")
    )
    .drop("internal_field", "deprecated_field")
)

# evitar — múltiplas ações intermediárias desnecessárias
df1 = df.filter(F.col("status") == "completed")
df1.show()   # ação — força materialização desnecessária
df2 = df1.withColumn("revenue", F.col("price") * F.col("quantity"))
df2.count()  # outra ação — relê os dados
```

## Cache e persist

Use `cache()`/`persist()` apenas quando o mesmo DataFrame é consumido múltiplas vezes
em ações diferentes. Cache desnecessário desperdiça memória do cluster.

```python
from pyspark import StorageLevel

# correto — persist antes de múltiplos consumos
enriched = (
    raw_df
    .join(lookup_df, "product_id", "left")
    .withColumn("revenue", F.col("price") * F.col("quantity"))
    .persist(StorageLevel.MEMORY_AND_DISK)
)

count = enriched.count()             # primeira ação — materializa e guarda em cache
summary = enriched.groupBy("year").agg(F.sum("revenue")).collect()  # usa cache
enriched.unpersist()                 # libera memória explicitamente

# evitar — persist em DataFrames usados uma única vez
df.persist()
result = df.count()  # única ação — persist desperdiça memória
df.unpersist()
```

## Joins — evitar skew

```python
# join padrão
result = orders.join(customers, orders.customer_id == customers.id, "left")

# broadcast join para tabelas pequenas (< 100MB) — elimina shuffle
from pyspark.sql.functions import broadcast

result = orders.join(broadcast(lookup_small), "product_id", "inner")

# salted join para skew extremo
orders_salted = orders.withColumn("salt", (F.rand() * 10).cast("int"))
customers_exploded = customers.withColumn("salt", F.explode(F.array([F.lit(i) for i in range(10)])))
result = orders_salted.join(customers_exploded, ["customer_id", "salt"], "inner")
```

## Escrita de dados

```python
# Parquet particionado — padrão para grandes volumes
result.coalesce(10).write.mode("overwrite").parquet("s3://bucket/output/")

# com particionamento por coluna
result.write.mode("overwrite").partitionBy("year", "region").parquet("s3://bucket/output/")

# Delta Lake com merge
result.write.format("delta").mode("overwrite").save("s3://bucket/delta/output/")

# coalesce antes de writes — evita muitos arquivos pequenos
# regra: ~128MB por arquivo
result.coalesce(20).write.mode("overwrite").parquet("s3://bucket/output/")
```

## Window functions

```python
from pyspark.sql.window import Window

window = Window.partitionBy("product_id").orderBy("sale_date")

result = df.withColumns({
    "cumulative_revenue": F.sum("revenue").over(
        window.rowsBetween(Window.unboundedPreceding, Window.currentRow)
    ),
    "revenue_delta": F.col("revenue") - F.lag("revenue").over(window),
    "rank": F.dense_rank().over(window),
})
```

## Integração com Polars

Para pós-processamento local de resultados Spark, converta via Arrow — mais eficiente
que `.toPandas()`.

```python
import polars as pl

# correto — via PyArrow (zero-copy quando possível)
arrow_table = result.limit(100_000).toArrow()
polars_df = pl.from_arrow(arrow_table)

# aceitável — via Pandas (mais lento, cópia extra)
pandas_df = result.limit(100_000).toPandas()
polars_df = pl.from_pandas(pandas_df)
```

## Testes com PySpark

Use `SparkSession` local com `master("local[2]")`. Dados sintéticos via `createDataFrame`.
Evite testes que dependem de S3 ou cluster real — use fixtures leves.

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from datetime import datetime


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """SparkSession local para testes — reutilizada em todos os testes da sessão."""
    return (
        SparkSession.builder
        .appName("test-session")
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "2")  # reduz overhead em testes
        .getOrCreate()
    )


def test_revenue_pipeline_filters_cancelled_orders(spark: SparkSession) -> None:
    input_data = [
        ("completed", 100.0, 2, datetime(2024, 1, 1)),
        ("cancelled", 50.0,  1, datetime(2024, 1, 2)),
        ("completed", 200.0, 1, datetime(2024, 1, 3)),
    ]
    schema = ["status", "price", "quantity", "created_at"]
    df = spark.createDataFrame(input_data, schema)

    result = (
        df
        .filter(F.col("status") == "completed")
        .withColumn("revenue", F.col("price") * F.col("quantity"))
    )

    rows = result.collect()
    total = sum(r["revenue"] for r in rows)
    assert total == pytest.approx(400.0)
    assert len(rows) == 2
```

## Regras de uso

- Nunca use RDD — use sempre DataFrame/Dataset API
- Nunca chame ações (`.count()`, `.collect()`, `.show()`) no meio de um pipeline sem necessidade
- `persist()` apenas quando o mesmo DataFrame é consumido em múltiplas ações
- `coalesce()` antes de writes para controlar o número de arquivos de saída
- Schema explícito ao ler dados externos — nunca confie em `inferSchema=True` em produção
- `broadcast()` para joins com tabelas pequenas — elimina shuffle caro
- Ative AQE (`spark.sql.adaptive.enabled = true`) — otimização automática de joins e partições
- Testes usam `local[2]` com `shuffle.partitions=2` para velocidade
