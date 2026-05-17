package com.example.spark;

import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public final class JsonFlattener {
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private JsonFlattener() {
    }

    public static boolean isValidJson(String json) {
        if (json == null || json.isBlank()) {
            return false;
        }

        try {
            OBJECT_MAPPER.readTree(json);
            return true;
        } catch (JsonProcessingException exception) {
            return false;
        }
    }

    public static Map<String, String> flatten(String json) throws JsonProcessingException {
        JsonNode root = OBJECT_MAPPER.readTree(json);
        Map<String, String> values = new LinkedHashMap<>();
        flattenNode("", root, values);
        return values;
    }

    public static String flattenToJson(String json) throws JsonProcessingException {
        return OBJECT_MAPPER.writeValueAsString(flatten(json));
    }

    private static void flattenNode(String path, JsonNode node, Map<String, String> values) {
        if (node == null || node.isNull()) {
            values.put(path, null);
            return;
        }

        if (node.isObject()) {
            Iterator<Map.Entry<String, JsonNode>> fields = node.fields();
            while (fields.hasNext()) {
                Map.Entry<String, JsonNode> field = fields.next();
                String nextPath = path.isEmpty() ? field.getKey() : path + "_" + field.getKey();
                flattenNode(nextPath, field.getValue(), values);
            }
            return;
        }

        if (node.isArray()) {
            for (int index = 0; index < node.size(); index++) {
                String nextPath = path + "_" + index;
                flattenNode(nextPath, node.get(index), values);
            }
            return;
        }

        values.put(path, node.asText());
    }
}
