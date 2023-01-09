### INITIALIZE SPARK SESSION
# pyspark --packages org.apache.hudi:hudi-spark3.3-bundle_2.12:0.12.0 --conf "spark.serializer"="org.apache.spark.serializer.KryoSerializer" --conf "spark.sql.catalog.spark_catalog"="org.apache.spark.sql.hudi.catalog.HoodieCatalog" --conf "spark.sql.extensions"="org.apache.spark.sql.hudi.HoodieSparkSessionExtension"

### CREATE TABLE
tableName = "hudi_trips_cow"

### DEFINE BASE PATH
basePath = "C:/ApacheHudiDemo/hudi_trips_cow"

### GENERATE DATA
dataGen = sc._jvm.org.apache.hudi.QuickstartUtils.DataGenerator()

### INSERT DATA
inserts = sc._jvm.org.apache.hudi.QuickstartUtils.convertToStringList(dataGen.generateInserts(10))
df = spark.read.json(spark.sparkContext.parallelize(inserts, 2))

hudi_options = {
    'hoodie.table.name': tableName,
    'hoodie.datasource.write.recordkey.field': 'uuid',
    'hoodie.datasource.write.partitionpath.field': 'partitionpath',
    'hoodie.datasource.write.table.name': tableName,
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'ts',
    'hoodie.upsert.shuffle.parallelism': 2,
    'hoodie.insert.shuffle.parallelism': 2
}

df.write.format("hudi").options(**hudi_options).mode("overwrite").save(basePath)

### READ DATA
tripsSnapshotDF = spark.read.format("hudi").load(basePath).createOrReplaceTempView("hudi_trips_snapshot")

### QUERY DATA
spark.sql("select fare, begin_lon, begin_lat, ts from  hudi_trips_snapshot where fare > 20.0").show()
spark.sql("select _hoodie_commit_time, _hoodie_record_key, _hoodie_partition_path, rider, driver, fare from  hudi_trips_snapshot").show()

### TIME TRAVEL QUERY
spark.read.format("hudi").option("as.of.instant", "20210728141108").load(basePath)

### UPDATE DATA
updates = sc._jvm.org.apache.hudi.QuickstartUtils.convertToStringList(dataGen.generateUpdates(10))
df = spark.read.json(spark.sparkContext.parallelize(updates, 2))

df.write.format("hudi").options(**hudi_options).mode("append").save(basePath)

### INCREMENTAL QUERY
spark.read.format("hudi").load(basePath).createOrReplaceTempView("hudi_trips_snapshot")

commits = list(map(lambda row: row[0], spark.sql("select distinct(_hoodie_commit_time) as commitTime from  hudi_trips_snapshot order by commitTime").limit(50).collect()))
beginTime = commits[len(commits) - 2] 

incremental_read_options = {
  'hoodie.datasource.query.type': 'incremental',
  'hoodie.datasource.read.begin.instanttime': beginTime,
}

# RELOAD DATA
tripsIncrementalDF = spark.read.format("hudi").options(**incremental_read_options).load(basePath).createOrReplaceTempView("hudi_trips_incremental")

spark.sql("select `_hoodie_commit_time`, fare, begin_lon, begin_lat, ts from  hudi_trips_incremental where fare > 20.0").show()

### POINT IN TIME QUERY
beginTime = "000"
endTime = commits[len(commits) - 2]

point_in_time_read_options = {
  'hoodie.datasource.query.type': 'incremental',
  'hoodie.datasource.read.end.instanttime': endTime,
  'hoodie.datasource.read.begin.instanttime': beginTime
}

# RELOAD DATA
tripsPointInTimeDF = spark.read.format("hudi").options(**point_in_time_read_options).load(basePath).createOrReplaceTempView("hudi_trips_point_in_time")

spark.sql("select `_hoodie_commit_time`, fare, begin_lon, begin_lat, ts from hudi_trips_point_in_time where fare > 20.0").show()

### SOFT DELETE
from pyspark.sql.functions import lit
from functools import reduce

# RELOAD DATA
spark.read.format("hudi").load(basePath).createOrReplaceTempView("hudi_trips_snapshot")

# BEFORE RESULTS
spark.sql("select uuid, partitionpath from hudi_trips_snapshot").count() #10
spark.sql("select uuid, partitionpath from hudi_trips_snapshot where rider is not null").count() #10

# PREPARE DELETION
soft_delete_ds = spark.sql("select * from hudi_trips_snapshot").limit(2)
meta_columns = ["_hoodie_commit_time", "_hoodie_commit_seqno", "_hoodie_record_key", "_hoodie_partition_path", "_hoodie_file_name"]
excluded_columns = meta_columns + ["ts", "uuid", "partitionpath"]
nullify_columns = list(filter(lambda field: field[0] not in excluded_columns, list(map(lambda field: (field.name, field.dataType), soft_delete_ds.schema.fields))))

hudi_soft_delete_options = {
  'hoodie.table.name': tableName,
  'hoodie.datasource.write.recordkey.field': 'uuid',
  'hoodie.datasource.write.partitionpath.field': 'partitionpath',
  'hoodie.datasource.write.table.name': tableName,
  'hoodie.datasource.write.operation': 'upsert',
  'hoodie.datasource.write.precombine.field': 'ts',
  'hoodie.upsert.shuffle.parallelism': 2, 
  'hoodie.insert.shuffle.parallelism': 2
}

soft_delete_df = reduce(lambda df,col: df.withColumn(col[0], lit(None).cast(col[1])), nullify_columns, reduce(lambda df,col: df.drop(col[0]), meta_columns, soft_delete_ds))
soft_delete_df.write.format("hudi").options(**hudi_soft_delete_options).mode("append").save(basePath)

# RELOAD DATA
spark.read.format("hudi").load(basePath).createOrReplaceTempView("hudi_trips_snapshot")

# AFTER RESULTS 
spark.sql("select uuid, partitionpath from hudi_trips_snapshot").count() #10
spark.sql("select uuid, partitionpath from hudi_trips_snapshot where rider is not null").count() #8
