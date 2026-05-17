package com.example.spark;

import org.apache.spark.api.java.function.FlatMapFunction;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import java.util.Arrays;

import static org.apache.spark.sql.functions.col;

public final class WordCountApp {

    private WordCountApp() {
    }

    public static void main(String[] args) {

        if (args.length < 1) {
            System.err.println(
                    "Usage: spark-submit --class com.example.spark.WordCountApp <jar> <input-path>");
            System.exit(1);
        }

        SparkSession spark = createSparkSession();

        try {

            // Read input text file
            Dataset<String> lines = spark.read().textFile(args[0]);

            // Split lines into words
            Dataset<String> words = lines.flatMap(
                    (FlatMapFunction<String, String>) line ->
                            Arrays.asList(line.split("\\s+")).iterator(),
                    Encoders.STRING()
            );

            // Count words
            Dataset<Row> counts = words.groupBy(col("value").alias("word"))
                    .count()
                    .orderBy(col("count").desc(), col("word"));

            // Display result
            counts.show(false);

        } finally {
            spark.stop();
        }
    }

    private static SparkSession createSparkSession() {

        SparkSession.Builder builder = SparkSession.builder()
                .appName("Spark Java Word Count");

        String master = System.getProperty("spark.master");

        if (master != null && !master.isBlank()) {
            builder.master(master);
        } else {
            // Run locally if no cluster master provided
            builder.master("local[*]");
        }

        return builder.getOrCreate();
    }
}