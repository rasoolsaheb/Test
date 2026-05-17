package com.example.spark;

import java.util.List;
import java.util.Locale;
import java.util.stream.Stream;

public final class WordTokenizer {
    private WordTokenizer() {
    }

    public static List<String> tokenize(String line) {
        if (line == null || line.isBlank()) {
            return List.of();
        }

        return Stream.of(line.toLowerCase(Locale.ROOT).split("\\W+"))
                .filter(token -> !token.isBlank())
                .toList();
    }
}
