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
# GOLD LAYER: FINANCE DOMAIN (UPSTREAM: silver_nyctaxi_trips & silver_vendor_lookup)
# COMMAND ----------

@dlt.table(
    name="gold_integrated_revenue",
    comment="Integrated Revenue Gold Mart joining Trips and Vendor Master",
    table_properties={
        "quality": "gold",
        "domain": "finance",
        "pipelines.autoOptimize.managed": "true"
    }
)
def gold_integrated_revenue():
    """
    Gold Layer (Domain: Finance)
    Upstream: silver_nyctaxi_trips + silver_vendor_lookup 조인 데이터 마트
    """
    silver_trips = dlt.read("silver_nyctaxi_trips")
    silver_vendors = dlt.read("silver_vendor_lookup")
    
    joined_df = silver_trips.join(
        silver_vendors,
        silver_trips.vendor_id == silver_vendors.vendor_id,
        "left"
    )
    
    return (
        joined_df
        .withColumn("trip_date", to_date(col("tpep_pickup_datetime")))
        .groupBy("trip_date", "vendor_name_clean", "default_payment_type")
        .agg(
            count("*").alias("total_trips"),
            round(avg("trip_distance"), 2).alias("avg_distance_miles"),
            round(_sum("fare_amount"), 2).alias("total_fare_revenue"),
            round(_sum("tip_amount"), 2).alias("total_tips"),
            round(avg("tip_percentage"), 2).alias("avg_tip_percentage")
        )
        .orderBy(col("trip_date").desc(), col("total_fare_revenue").desc())
    )
