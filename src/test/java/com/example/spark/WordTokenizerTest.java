package com.example.spark;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;

import org.junit.jupiter.api.Test;

class WordTokenizerTest {
    @Test
    void tokenizeNormalizesTextIntoWords() {
        assertEquals(
                List.of("hello", "spark", "hello", "java"),
                WordTokenizer.tokenize("Hello, Spark! Hello Java."));
    }

    @Test
    void tokenizeIgnoresBlankInput() {
        assertEquals(List.of(), WordTokenizer.tokenize("   "));
    }
}
