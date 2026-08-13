import dlt
from pyspark.sql.functions import col, upper, trim

# COMMAND ----------
# SILVER LAYER: VENDORS DOMAIN (UPSTREAM: bronze_vendor_lookup)
# COMMAND ----------

@dlt.table(
    name="silver_vendor_lookup",
    comment="Silver cleaned Vendor Master data (depends on bronze_vendor_lookup)",
    table_properties={
        "quality": "silver",
        "domain": "vendors",
        "pipelines.autoOptimize.managed": "true"
    }
)
@dlt.expect_or_drop("valid_vendor_id", "vendor_id IS NOT NULL")
def silver_vendor_lookup():
    """
    Silver Layer (Domain: Vendors)
    bronze_vendor_lookup 마스터 데이터 수집 이벤트 발생 시 해당 노드만 반응하여 정제
    """
    bronze_df = dlt.read("bronze_vendor_lookup")
    
    return (
        bronze_df
        .withColumn("vendor_name_clean", trim(col("vendor_name")))
        .withColumn("vendor_code_upper", upper(col("vendor_code")))
    )
