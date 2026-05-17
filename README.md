# Spark Java Project

A minimal Apache Spark project written in Java. It includes:

- A batch word-count example.
- A Kafka JSON streaming pipeline that stores raw messages, trusted raw JSON messages, and trusted flattened JSON messages.
- Maven build/test/package commands and sample input files.

## Prerequisites

- Java 17 or newer installed
- Maven 3.9 or newer installed
- Optional: a local Apache Spark installation if you want to run with `spark-submit`
- Kafka broker access for the streaming pipeline

> This project is configured with Apache Spark `3.5.8` and Scala binary version `2.12` through Spark Maven artifacts.

## Project Structure

```text
.
├── pom.xml
├── data/
│   ├── sample.txt
│   └── sample-kafka-message.json
└── src/
    ├── main/java/com/example/spark/KafkaJsonPipelineApp.java
    ├── main/java/com/example/spark/JsonFlattener.java
    ├── main/java/com/example/spark/WordCountApp.java
    ├── main/java/com/example/spark/WordTokenizer.java
    ├── test/java/com/example/spark/JsonFlattenerTest.java
    └── test/java/com/example/spark/WordTokenizerTest.java
```

## Build and Test

Run the unit tests:

```bash
mvn test
```

Create an executable shaded JAR:

```bash
mvn package
```

## Word Count Example

Run the sample word-count job in local mode with Maven:

```bash
mvn exec:java \
  -Dexec.mainClass=com.example.spark.WordCountApp \
  -Dexec.args=data/sample.txt \
  -Dspark.master=local[*]
```

After packaging, run the shaded JAR directly:

```bash
java -Dspark.master=local[*] -jar target/spark-java-project-1.0.0-SNAPSHOT.jar data/sample.txt
```

Or run with `spark-submit`:

```bash
spark-submit \
  --class com.example.spark.WordCountApp \
  --master local[*] \
  target/spark-java-project-1.0.0-SNAPSHOT.jar \
  data/sample.txt
```

## Kafka JSON Raw and Trusted Pipeline

`KafkaJsonPipelineApp` reads Kafka message values as JSON strings and writes three storage zones:

1. **Raw**: every Kafka message is stored exactly as received in `raw_message`, together with Kafka metadata such as topic, partition, offset, key, Kafka timestamp, and ingestion timestamp.
2. **Trusted raw**: only valid JSON messages are stored, while preserving the original `raw_message` payload.
3. **Trusted flatten**: valid JSON messages are flattened and stored in `flattened_values` as a Spark map and in `flattened_json` as a JSON string, while keeping Kafka metadata. Nested JSON keys are joined with underscores. Array indexes are included in the flattened key.

Example input message from `data/sample-kafka-message.json`:

```json
{
  "id": 101,
  "customer": {"name": "Asha", "address": {"city": "Austin"}},
  "items": [{"sku": "A1"}, {"sku": "B2"}],
  "active": true
}
```

Example flattened values in `trusted_flatten`:

```json
{
  "id": "101",
  "customer_name": "Asha",
  "customer_address_city": "Austin",
  "items_0_sku": "A1",
  "items_1_sku": "B2",
  "active": "true"
}
```

### Run the Kafka Pipeline with Maven

```bash
mvn exec:java \
  -Dexec.mainClass=com.example.spark.KafkaJsonPipelineApp \
  -Dexec.args="--bootstrap-servers localhost:9092 --topic input-json --output-base-path data/output/kafka-json-pipeline" \
  -Dspark.master=local[*]
```

### Run the Kafka Pipeline with spark-submit

```bash
spark-submit \
  --class com.example.spark.KafkaJsonPipelineApp \
  --master local[*] \
  target/spark-java-project-1.0.0-SNAPSHOT.jar \
  --bootstrap-servers localhost:9092 \
  --topic input-json \
  --output-base-path data/output/kafka-json-pipeline
```

### Optional Kafka Pipeline Arguments

| Argument | Default | Description |
| --- | --- | --- |
| `--output-base-path` | `data/output/kafka-json-pipeline` | Base folder used when individual output paths are not provided. |
| `--raw-output-path` | `<output-base-path>/raw` | Folder for all Kafka messages exactly as received. |
| `--trusted-raw-output-path` | `<output-base-path>/trusted_raw` | Folder for valid JSON messages with original payload preserved. |
| `--trusted-flatten-output-path` | `<output-base-path>/trusted_flatten` | Folder for flattened valid JSON messages. |
| `--checkpoint-location` | `<output-base-path>/_checkpoint` | Spark Structured Streaming checkpoint folder. |
| `--starting-offsets` | `latest` | Kafka starting offsets, for example `latest` or `earliest`. |
| `--output-format` | `json` | Spark output format such as `json` or `parquet`. |
| `--trigger-interval` | `30 seconds` | Structured Streaming processing trigger interval. |

## Next Steps

- Change `--output-format parquet` for analytics-friendly storage.
- Replace local output paths with cloud/object storage paths when deploying.
- Add schema-specific transformations if downstream trusted tables need fixed columns instead of the generic `flattened_values` map and `flattened_json` payload.
- Add connector dependencies to `pom.xml` if you want to write trusted data into a database, Hive table, Delta table, or warehouse.
