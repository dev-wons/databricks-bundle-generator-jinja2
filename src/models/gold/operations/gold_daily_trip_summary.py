# Databricks notebook source
import dlt
from pyspark.sql.functions import (
    col,
    to_date,
    count,
    avg,
    sum as _sum,
    round
)

# COMMAND ----------
# GOLD LAYER: OPERATIONS DOMAIN (UPSTREAM: silver_nyctaxi_trips)
# COMMAND ----------

@dlt.table(
    name="gold_daily_trip_summary",
    comment="Daily Operations Trip Summary Gold Mart (depends on silver_nyctaxi_trips)",
    table_properties={
        "quality": "gold",
        "domain": "operations",
        "pipelines.autoOptimize.managed": "true"
    }
)
def gold_daily_trip_summary():
    """
    Gold Layer (Domain: Operations)
    Upstream: silver_nyctaxi_trips 일별 운행 요약 마트
    """
    silver_trips = dlt.read("silver_nyctaxi_trips")
    
    return (
        silver_trips
        .withColumn("trip_date", to_date(col("tpep_pickup_datetime")))
        .groupBy("trip_date")
        .agg(
            count("*").alias("total_trips"),
            round(avg("trip_duration_minutes"), 2).alias("avg_duration_minutes"),
            round(_sum("fare_amount"), 2).alias("total_fare_revenue")
        )
        .orderBy(col("trip_date").desc())
    )
