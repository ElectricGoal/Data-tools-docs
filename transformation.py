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

# get data from api
url = "https://v6.exchangerate-api.com/v6/63537f7c50eb0d3d3877c1a2/latest/USD"

# get response
response = requests.get(url)

# convert response to json
data = response.json()

# get exchange rate
exchange_rate = data['conversion_rates']['VND']

# select last id from hive table
# check if table is empty
try:
        last_id = spark.sql("select max(id) as last_id from test.transactions").collect()[0]['last_id']
except:
        last_id = 0

print(last_id)

# filter data
df = df.filter(df["id"] > last_id)

# remove $ sign
df = df.withColumn("Amount", regexp_replace(col("Amount"), "\$", ""))

# convert string to float
df = df.withColumn("Amount", col("Amount").cast("float"))

# convert amount to VND
df = df.withColumn("Amount", col("Amount") * exchange_rate)

# Define Hive table name
hive_table_name = "test.transactions"

# write data to console
# df.write.format("console").mode("overwrite").save() 

# Write data to Hive
df.write.format("hive").mode("append").saveAsTable(hive_table_name)

# Stop the Spark session
spark.stop()