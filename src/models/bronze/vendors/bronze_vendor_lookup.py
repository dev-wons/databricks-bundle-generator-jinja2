# Databricks notebook source
import dlt
from pyspark.sql.functions import current_timestamp

# COMMAND ----------
# BRONZE LAYER: VENDORS DOMAIN
# COMMAND ----------

@dlt.table(
    name="bronze_vendor_lookup",
    comment="Bronze raw Vendor master lookup data",
    table_properties={
        "quality": "bronze",
        "domain": "vendors",
        "pipelines.autoOptimize.managed": "true"
    }
)
def bronze_vendor_lookup():
    """
    Bronze Layer (Domain: Vendors)
    택시 운행업체/결제수단 마스터 데이터 수집
    """
    data = [
        (1, "Creative Mobile Technologies, LLC", "CMT", "Credit Card"),
        (2, "VeriFone Inc.", "VTS", "Cash"),
        (3, "Digital Dispatch Systems", "DDS", "No Charge"),
        (4, "Dispatched Taxi", "DIS", "Dispute")
    ]
    columns = ["vendor_id", "vendor_name", "vendor_code", "default_payment_type"]
    
    df = spark.createDataFrame(data, columns)
    return df.withColumn("_ingested_at", current_timestamp())
