package com.example.spark;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Map;

import org.junit.jupiter.api.Test;

class JsonFlattenerTest {
    @Test
    void flattenCreatesUnderscoreDelimitedKeysForNestedJson() throws Exception {
        Map<String, String> flattened = JsonFlattener.flatten("""
                {
                  "id": 101,
                  "customer": {"name": "Asha", "address": {"city": "Austin"}},
                  "items": [{"sku": "A1"}, {"sku": "B2"}],
                  "active": true
                }
                """);

        assertEquals("101", flattened.get("id"));
        assertEquals("Asha", flattened.get("customer_name"));
        assertEquals("Austin", flattened.get("customer_address_city"));
        assertEquals("A1", flattened.get("items_0_sku"));
        assertEquals("B2", flattened.get("items_1_sku"));
        assertEquals("true", flattened.get("active"));
    }

    @Test
    void validateJsonRejectsInvalidPayloads() {
        assertTrue(JsonFlattener.isValidJson("{\"id\":1}"));
        assertFalse(JsonFlattener.isValidJson("not-json"));
        assertFalse(JsonFlattener.isValidJson("   "));
    }
}
