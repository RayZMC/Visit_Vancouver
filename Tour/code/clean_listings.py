import sys
from pyspark.sql import SparkSession

# Initialize Spark Session
spark = SparkSession.builder.appName('Clean Listings').getOrCreate()

# Set log level to WARN to reduce the amount of logs for readability
spark.sparkContext.setLogLevel('WARN')

# Assertions to ensure correct environment setup
assert sys.version_info >= (3, 5)  # make sure we have Python 3.5+
assert spark.version >= '2.3'      # make sure we have Spark 2.3+


data = spark.read.csv('../data/listings.csv', header=True, inferSchema=True)

# Remove duplicates
data = data.dropDuplicates(['id'])
data = data.drop('host_name')

# Drop missing values
data = data.na.drop(subset=['name', 'price', 'number_of_reviews', 'reviews_per_month'])

# Filter by reviews and ratings
data = data.filter((data['number_of_reviews'] >= 10) & 
                   (data['reviews_per_month'] >= 0.5))

# Minimum nights and availability
data = data.filter((data['minimum_nights'] <= 30) & 
                   (data['availability_365'] >= 30))

data.write.csv('../data/cleaned_listings', header=True, mode='overwrite')
