from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# spark streaming read data from kafka 
spark = SparkSession \
    .builder \
    .appName("Ingestion") \
    .getOrCreate()

# read data from csv file
df = spark \
    .read \
    .format("csv") \
    .option("header", "true") \
    .load("/home/playground/document/data/transactions.csv")

# # convert binary to string key and value
# df1 = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# # define schema for data
# schema = StructType(
#     [
#         StructField("User", StringType(), True),
#         StructField("Card", StringType(), True),
#         StructField("Year", StringType(), True),
#         StructField("Month", StringType(), True),
#         StructField("Day", StringType(), True),
#         StructField("Time", StringType(), True),
#         StructField("Amount", StringType(), True),
#         StructField("Use Chip", StringType(), True),
#         StructField("Merchant Name", StringType(), True),
#         StructField("Merchant City", StringType(), True),
#         StructField("Merchant State", StringType(), True),
#         StructField("Zip", StringType(), True),
#         StructField("Errors?", StringType(), True),
#         StructField("Is Fraud?", StringType(), True),
#         StructField("id", IntegerType(), True),
#     ]
# )

# # convert json to dataframe
# df2 = df1.select(from_json(col("value"), schema).alias("data"))

# # select columns
# df3 = df2.select("data.User", "data.Card", "data.Year", "data.Month", "data.Day", "data.Time", "data.Amount", "data.Use Chip", "data.Merchant Name", "data.Merchant City", "data.Merchant State", "data.Zip", "data.Errors?", "data.Is Fraud?", "data.id")

# # filter column "Is Fraud?" = "No"
# df3 = df3.filter(df3["Is Fraud?"] == "No")

# # convert one digit month to two digits
# df3 = df3.withColumn("Month", lpad("Month", 2, "0"))
# # convert one digit day to two digits
# df3 = df3.withColumn("Day", lpad("Day", 2, "0"))

# # combine datetime columns to dd/mm/yyyy hh:mm:ss
# df3 = df3.withColumn("datetime", concat(col("Year"), lit("-"), col("Month"), lit("-"), col("Day"), lit(" "), col("Time"), lit(":00")))

# # convert datetime to timestamp
# df3 = df3.withColumn("Created_at", to_timestamp(col("datetime"), "yyyy-MM-dd HH:mm:ss"))

# # select columns
# df3 = df3.select("id", "User", "Card", "Created_at", "Amount", "Use Chip", "Merchant Name", "Merchant City")
df.show()

saving_location = "hdfs://127.0.0.1:9000/datalake/transactions"

# write datafram to parquet file in hdfs
df.write \
    .mode("overwrite") \
    .format("parquet") \
    .option("path", saving_location) \
    .save()

# stop the Spark session
spark.stop()