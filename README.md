# Spark Java Project

A minimal Apache Spark project written in Java. It includes a Maven build, a runnable word-count example, unit tests, and a small sample input file.

## Prerequisites

- Java 17 or newer installed
- Maven 3.9 or newer installed
- Optional: a local Apache Spark installation if you want to run with `spark-submit`

> This project is configured with Apache Spark `3.5.8` and Scala binary version `2.12` through the `spark-sql_2.12` Maven artifact.

## Project Structure

```text
.
├── pom.xml
├── data/
│   └── sample.txt
└── src/
    ├── main/java/com/example/spark/WordCountApp.java
    ├── main/java/com/example/spark/WordTokenizer.java
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

## Run Locally with Maven

Run the sample word-count job in local mode:

```bash
mvn exec:java \
  -Dexec.mainClass=com.example.spark.WordCountApp \
  -Dexec.args=data/sample.txt \
  -Dspark.master=local[*]
```

If your Maven installation does not automatically resolve the Exec Maven Plugin, use the generated JAR instead.

## Run with Java

After packaging, run the shaded JAR directly:

```bash
java -Dspark.master=local[*] -jar target/spark-java-project-1.0.0-SNAPSHOT.jar data/sample.txt
```

## Run with spark-submit

If Apache Spark is installed locally and `spark-submit` is on your `PATH`:

```bash
spark-submit \
  --class com.example.spark.WordCountApp \
  --master local[*] \
  target/spark-java-project-1.0.0-SNAPSHOT.jar \
  data/sample.txt
```

## Next Steps

- Replace `WordCountApp` with your real Spark job.
- Put larger input files outside the repository and pass their path as the first command-line argument.
- Add more dependencies to `pom.xml` if you need connectors such as Kafka, JDBC, or cloud storage clients.
