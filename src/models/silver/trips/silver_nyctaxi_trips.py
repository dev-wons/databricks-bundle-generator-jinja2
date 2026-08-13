import dlt
from pyspark.sql.functions import col, unix_timestamp, round, when

# COMMAND ----------
# SILVER LAYER: TRIPS DOMAIN (UPSTREAM: bronze_nyctaxi_trips)
# COMMAND ----------

@dlt.table(
    name="silver_nyctaxi_trips",
    comment="Silver cleaned NYC Taxi trips with quality constraints (depends on bronze_nyctaxi_trips)",
    table_properties={
        "quality": "silver",
        "domain": "trips",
        "pipelines.autoOptimize.managed": "true"
    }
)
@dlt.expect("valid_pickup_dropoff", "tpep_pickup_datetime IS NOT NULL AND tpep_dropoff_datetime IS NOT NULL")
@dlt.expect_or_drop("valid_passenger_count", "passenger_count > 0")
@dlt.expect_or_drop("valid_trip_distance", "trip_distance > 0.0")
@dlt.expect_or_drop("valid_fare_amount", "fare_amount >= 0.0")
def silver_nyctaxi_trips():
    """
    Silver Layer (Domain: Trips)
    bronze_nyctaxi_trips 수집 이벤트 발생 시 해당 노드만 반응하여 정제
    """
    bronze_df = dlt.read_stream("bronze_nyctaxi_trips")
    
    return (
        bronze_df
        .withColumn(
            "trip_duration_minutes",
            round((unix_timestamp(col("tpep_dropoff_datetime")) - unix_timestamp(col("tpep_pickup_datetime"))) / 60, 2)
        )
        .withColumn(
            "tip_percentage",
            when(col("fare_amount") > 0, round((col("tip_amount") / col("fare_amount")) * 100, 2)).otherwise(0.0)
        )
    )
