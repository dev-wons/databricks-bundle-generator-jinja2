# Databricks notebook source
import dlt
from pyspark.sql.functions import current_timestamp

# COMMAND ----------
# BRONZE LAYER: TRIPS DOMAIN
# COMMAND ----------

@dlt.table(
    name="bronze_nyctaxi_trips",
    comment="Bronze raw NYC Taxi trips data ingested into Bronze layer",
    table_properties={
        "quality": "bronze",
        "domain": "trips",
        "pipelines.autoOptimize.managed": "true"
    }
)
def bronze_nyctaxi_trips():
    """
    Bronze Layer (Domain: Trips)
    Databricks 샘플 데이터셋 수집 및 _ingested_at 메타데이터 추가
    """
    try:
        df = (
            spark.readStream
            .option("skipChangeCommits", "true")
            .table("samples.nyctaxi.trips")
        )
    except Exception:
        df = (
            spark.read
            .format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load("dbfs:/databricks-datasets/nyctaxi/sample/yellow/")
        )
    
    return df.withColumn("_ingested_at", current_timestamp())
