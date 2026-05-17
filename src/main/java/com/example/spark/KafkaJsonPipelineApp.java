package com.example.spark;

import java.util.HashMap;
import java.util.Map;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.api.java.UDF1;
import org.apache.spark.sql.streaming.StreamingQuery;
import org.apache.spark.sql.streaming.Trigger;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.storage.StorageLevel;

import static org.apache.spark.sql.functions.callUDF;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.current_timestamp;
import static org.apache.spark.sql.functions.expr;

public final class KafkaJsonPipelineApp {
    private KafkaJsonPipelineApp() {
    }

    public static void main(String[] args) throws Exception {
        PipelineConfig config = PipelineConfig.fromArgs(args);

        SparkSession spark = SparkSession.builder()
                .appName("Kafka JSON Raw Trusted Pipeline")
                .getOrCreate();

        registerJsonFunctions(spark);

        Dataset<Row> kafkaMessages = spark.readStream()
                .format("kafka")
                .option("kafka.bootstrap.servers", config.bootstrapServers())
                .option("subscribe", config.topic())
                .option("startingOffsets", config.startingOffsets())
                .load()
                .select(
                        col("topic"),
                        col("partition"),
                        col("offset"),
                        col("timestamp").alias("kafka_timestamp"),
                        expr("CAST(key AS STRING)").alias("message_key"),
                        expr("CAST(value AS STRING)").alias("raw_message"),
                        current_timestamp().alias("ingestion_timestamp"));

        StreamingQuery query = kafkaMessages.writeStream()
                .queryName("kafka-json-raw-trusted-pipeline")
                .option("checkpointLocation", config.checkpointLocation())
                .trigger(Trigger.ProcessingTime(config.triggerInterval()))
                .foreachBatch((batch, batchId) -> writeBatch(batch, config))
                .start();

        query.awaitTermination();
    }

    private static void registerJsonFunctions(SparkSession spark) {
        spark.udf().register(
                "is_valid_json",
                (UDF1<String, Boolean>) JsonFlattener::isValidJson,
                DataTypes.BooleanType);
        spark.udf().register(
                "flatten_json",
                (UDF1<String, String>) JsonFlattener::flattenToJson,
                DataTypes.StringType);
        spark.udf().register(
                "flatten_map",
                (UDF1<String, Map<String, String>>) JsonFlattener::flatten,
                DataTypes.createMapType(DataTypes.StringType, DataTypes.StringType));
    }

    private static void writeBatch(Dataset<Row> batch, PipelineConfig config) {
        Dataset<Row> cachedBatch = batch.persist(StorageLevel.MEMORY_AND_DISK());
        try {
            if (cachedBatch.count() == 0) {
                return;
            }

            cachedBatch.write()
                    .mode("append")
                    .format(config.outputFormat())
                    .save(config.rawOutputPath());

            Dataset<Row> trustedRows = cachedBatch
                    .withColumn("is_valid_json", callUDF("is_valid_json", col("raw_message")))
                    .filter(col("is_valid_json"))
                    .drop("is_valid_json");

            trustedRows.write()
                    .mode("append")
                    .format(config.outputFormat())
                    .save(config.trustedRawOutputPath());

            trustedRows
                    .withColumn("flattened_values", callUDF("flatten_map", col("raw_message")))
                    .withColumn("flattened_json", callUDF("flatten_json", col("raw_message")))
                    .drop("raw_message")
                    .write()
                    .mode("append")
                    .format(config.outputFormat())
                    .save(config.trustedFlattenOutputPath());
        } finally {
            cachedBatch.unpersist();
        }
    }

    record PipelineConfig(
            String bootstrapServers,
            String topic,
            String rawOutputPath,
            String trustedRawOutputPath,
            String trustedFlattenOutputPath,
            String checkpointLocation,
            String startingOffsets,
            String outputFormat,
            String triggerInterval) {
        static PipelineConfig fromArgs(String[] args) {
            Map<String, String> options = parseArgs(args);
            String bootstrapServers = required(options, "bootstrap-servers");
            String topic = required(options, "topic");
            String outputBasePath = options.getOrDefault("output-base-path", "data/output/kafka-json-pipeline");

            return new PipelineConfig(
                    bootstrapServers,
                    topic,
                    options.getOrDefault("raw-output-path", outputBasePath + "/raw"),
                    options.getOrDefault("trusted-raw-output-path", outputBasePath + "/trusted_raw"),
                    options.getOrDefault("trusted-flatten-output-path", outputBasePath + "/trusted_flatten"),
                    options.getOrDefault("checkpoint-location", outputBasePath + "/_checkpoint"),
                    options.getOrDefault("starting-offsets", "latest"),
                    options.getOrDefault("output-format", "json"),
                    options.getOrDefault("trigger-interval", "30 seconds"));
        }

        private static Map<String, String> parseArgs(String[] args) {
            Map<String, String> options = new HashMap<>();
            for (int index = 0; index < args.length; index++) {
                String arg = args[index];
                if (!arg.startsWith("--")) {
                    throw new IllegalArgumentException("Unexpected argument: " + arg);
                }
                String name = arg.substring(2);
                if (index + 1 >= args.length || args[index + 1].startsWith("--")) {
                    throw new IllegalArgumentException("Missing value for --" + name);
                }
                options.put(name, args[++index]);
            }
            return options;
        }

        private static String required(Map<String, String> options, String name) {
            String value = options.get(name);
            if (value == null || value.isBlank()) {
                throw new IllegalArgumentException("Missing required argument --" + name + "\n" + usage());
            }
            return value;
        }

        private static String usage() {
            return "Usage: spark-submit --class com.example.spark.KafkaJsonPipelineApp <jar> "
                    + "--bootstrap-servers <host:port> --topic <topic> "
                    + "[--output-base-path <path>] [--checkpoint-location <path>] "
                    + "[--starting-offsets latest|earliest] [--output-format json|parquet]";
        }
    }
}
