package com.example.spark;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import static org.apache.spark.sql.functions.col;

public final class WordCountApp {
    private WordCountApp() {
    }

    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Usage: spark-submit --class com.example.spark.WordCountApp <jar> <input-path>");
            System.exit(1);
        }

        SparkSession spark = createSparkSession();

        try {
            Dataset<String> lines = spark.read().textFile(args[0]);
            Dataset<String> words = lines.flatMap(
                    line -> WordTokenizer.tokenize(line).iterator(),
                    Encoders.STRING());

            Dataset<Row> counts = words.groupBy(col("value").alias("word"))
                    .count()
                    .orderBy(col("count").desc(), col("word"));

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
        }

        return builder.getOrCreate();
    }
}
