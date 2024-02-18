from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

from pyspark.sql import SparkSession
import requests
        
# Create a Spark session
spark = SparkSession \
        .builder \
        .appName("Transformation") \
        .config("hive.metastore.uris", "thrift://127.0.0.1:9083") \
        .enableHiveSupport() \
        .getOrCreate()

# Define HDFS input path
hdfs_input_path = "hdfs://127.0.0.1:9000/datalake/transactions"

# Read data from HDFS
df = spark.read.format("parquet").load(hdfs_input_path)

# remove $ sign
df = df.withColumn("Amount", regexp_replace(col("Amount"), "\$", ""))

# convert string to float
df = df.withColumn("Amount", col("Amount").cast("float"))

# Define Hive table name
hive_table_name = "test.transactions"

# write data to console
# df.write.format("console").mode("overwrite").save() 

# Write data to Hive
df.write.format("hive").mode("append").saveAsTable(hive_table_name)

# Stop the Spark session
spark.stop()