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
# GOLD LAYER: FINANCE DOMAIN (UPSTREAM: silver_nyctaxi_trips)
# COMMAND ----------

@dlt.table(
    name="gold_integrated_revenue",
    comment="Integrated Revenue Gold Mart for NYC Taxi Trips",
    table_properties={
        "quality": "gold",
        "domain": "finance",
        "pipelines.autoOptimize.managed": "true"
    }
)
def gold_integrated_revenue():
    """
    Gold Layer (Domain: Finance)
    Upstream: silver_nyctaxi_trips 일별 운행 매출 집계 마트
    """
    silver_trips = dlt.read("silver_nyctaxi_trips")
    
    return (
        silver_trips
        .withColumn("trip_date", to_date(col("tpep_pickup_datetime")))
        .groupBy("trip_date", "pickup_zip")
        .agg(
            count("*").alias("total_trips"),
            round(avg("trip_distance"), 2).alias("avg_distance_miles"),
            round(_sum("fare_amount"), 2).alias("total_fare_revenue")
        )
        .orderBy(col("trip_date").desc(), col("total_fare_revenue").desc())
    )
