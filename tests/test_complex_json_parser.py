import unittest
import json
from llm_output_parser import parse_json


class TestComplexJsonParser(unittest.TestCase):
    def test_nested_json_extraction(self):
        """Test extraction of deeply nested JSON structures."""
        deeply_nested = """
        Here's some text with a deeply nested JSON:
        {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "data": [1, 2, 3, 4, 5],
                                "nested_array": [
                                    {"name": "item1", "value": 100},
                                    {"name": "item2", "value": 200}
                                ],
                                "flag": true
                            }
                        }
                    }
                }
            }
        }
        """
        result = parse_json(deeply_nested)
        self.assertEqual(
            result["level1"]["level2"]["level3"]["level4"]["level5"]["data"][4], 5
        )
        self.assertEqual(
            result["level1"]["level2"]["level3"]["level4"]["level5"]["nested_array"][1][
                "value"
            ],
            200,
        )
        self.assertTrue(
            result["level1"]["level2"]["level3"]["level4"]["level5"]["flag"]
        )

    def test_json_subset_comparison(self):
        """Test cases where one JSON could be a subset of another."""
        text_with_nested_json = """
        This is a partial JSON: {"name": "John"}
        
        And here is a complete one:
        {
            "person": {
                "name": "John",
                "age": 30,
                "details": {
                    "occupation": "Developer",
                    "experience": 5
                }
            }
        }
        """
        result = parse_json(text_with_nested_json)
        # Should extract the larger JSON object
        self.assertIn("person", result)
        self.assertEqual(result["person"]["name"], "John")
        self.assertEqual(result["person"]["details"]["occupation"], "Developer")

        # Test a case with both complete objects and arrays
        mixed_json_types = """
        Small array [1, 2, 3]
        Larger object {"data": [1, 2, 3, 4, 5], "extra": true}
        """
        result = parse_json(mixed_json_types)
        # Should extract the larger JSON (the object)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["data"]), 5)
        self.assertTrue(result["extra"])

    def test_multiple_codeblocks(self):
        """Test extraction from multiple code blocks with different JSONs."""
        multiple_blocks = """
        Here's a small JSON:
        ```json
        {"simple": true}
        ```
        
        And here's a much larger, more comprehensive one:
        ```json
        {
            "config": {
                "server": {
                    "host": "localhost",
                    "port": 8080,
                    "secure": true
                },
                "database": {
                    "url": "mongodb://localhost:27017",
                    "name": "myapp",
                    "collections": ["users", "products", "orders"]
                },
                "features": {
                    "logging": true,
                    "metrics": false,
                    "caching": {
                        "enabled": true,
                        "ttl": 3600
                    }
                }
            }
        }
        ```
        
        And a tiny one at the end:
        ```json
        {"note": "This is the end"}
        ```
        """
        result = parse_json(multiple_blocks)
        # Should extract the most comprehensive JSON (the middle one)
        self.assertIn("config", result)
        self.assertEqual(result["config"]["server"]["port"], 8080)
        self.assertEqual(result["config"]["database"]["collections"][2], "orders")
        self.assertEqual(result["config"]["features"]["caching"]["ttl"], 3600)

    def test_competing_json_structures(self):
        """Test extraction when different methods find different valid JSONs."""
        competing_structures = """
        Small valid JSON at beginning: {"id": 1}
        
        ```json
        {"name": "Code Block JSON", "type": "block"}
        ```
        
        {
            "title": "This is a larger JSON outside a code block",
            "items": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
                {"id": 3, "name": "Item 3"}
            ],
            "metadata": {
                "created": "2023-01-01",
                "author": "Test User"
            }
        }
        
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        """
        result = parse_json(competing_structures)
        # Should extract the largest JSON (the one outside code block)
        self.assertIn("title", result)
        self.assertEqual(len(result["items"]), 3)
        self.assertEqual(result["metadata"]["author"], "Test User")

    def test_json_with_unusual_formatting(self):
        """Test extraction of JSON with unusual formatting."""
        unusual_formatting = """
        Here's a strangely formatted but valid JSON:
        {
    "compacted": {
        "nested": {"value": 42},
        "array": [1, 2, 3]
    },
    "sparse": {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    },
    "unicode": "\u00a9 \u2665 \u266a",
    "very_long_key_that_extends_beyond_normal_line_width_to_test_parsing_capabilities_with_extended_content": true
}

"""
        result = parse_json(unusual_formatting)
        self.assertEqual(result["compacted"]["nested"]["value"], 42)
        self.assertEqual(result["sparse"]["key2"], "value2")
        self.assertEqual(result["unicode"], "© ♥ ♪")
        self.assertTrue(
            result[
                "very_long_key_that_extends_beyond_normal_line_width_to_test_parsing_capabilities_with_extended_content"
            ]
        )

    def test_embedded_json_in_context(self):
        """Test extraction of JSON embedded in conversational text."""
        conversation = """
        User: Can you provide me with the configuration?

        Assistant: Of course! Here's the configuration you requested:
        
        ```json
        {
            "api_key": "sk_test_123456789",
            "endpoints": {
                "production": "https://api.example.com/v1",
                "sandbox": "https://sandbox.api.example.com/v1"
            },
            "timeout": 30,
            "retry": {
                "attempts": 3,
                "backoff": 2
            }
        }
        ```
        
        Let me know if you need anything else!
        
        User: Can you also give me a simpler version?
        
        Assistant: Sure, here's a simplified version:
        
        {
            "api_key": "sk_test_123456789",
            "endpoint": "https://api.example.com/v1"
        }
        """
        result = parse_json(conversation)
        # Should extract the more complex JSON (with endpoints instead of endpoint)
        self.assertIn("endpoints", result)
        self.assertEqual(
            result["endpoints"]["production"], "https://api.example.com/v1"
        )
        self.assertEqual(result["retry"]["attempts"], 3)

    def test_malformed_json_recovery(self):
        """Test extraction when JSON is malformed but recoverable."""
        almost_valid = """
        This JSON has extra commas but our extractor should find it valid after cleaning:
        
        {
            "name": "Test",
            "values": [1, 2, 3,],  // Extra comma
            "settings": {
                "active": true,
                "mode": "advanced",  // Extra comma
            }
        }
        
        """

        expected = {
            "name": "Test",
            "values": [1, 2, 3],
            "settings": {"active": True, "mode": "advanced"},
        }
        result = parse_json(almost_valid)
        # Should extract the valid JSON at the end
        self.assertEqual(result, expected)

    def test_json_within_json(self):
        """Test extraction when JSON contains stringified JSON."""
        json_inception = """
{
    "metadata": {
        "description": "This JSON contains another JSON as a string"
    },
    "rawConfig": "{\\\"server\\\":\\\"localhost\\\",\\\"port\\\":8080}",
    "rawData": "[{\\\"id\\\":1,\\\"name\\\":\\\"Item 1\\\"},{\\\"id\\\":2,\\\"name\\\":\\\"Item 2\\\"}]"
}
"""
        result = parse_json(json_inception)
        # Verify we got the outer JSON object with all properties
        self.assertIn("metadata", result)
        self.assertIn("rawConfig", result)
        self.assertIn("rawData", result)
        self.assertEqual(
            result["metadata"]["description"],
            "This JSON contains another JSON as a string",
        )

        # rawConfig and rawData should be strings, not parsed JSON
        self.assertIsInstance(result["rawConfig"], str)
        self.assertIsInstance(result["rawData"], str)

        # But we can parse them separately
        config = json.loads(result["rawConfig"])
        self.assertEqual(config["port"], 8080)

    def test_json_within_json_complex(self):
        # Test a more complex case with multiple levels of stringified JSON
        nested_inception = """
        {
            "outer": "Simple value",
            "nested": {
                "stringified": "{\\\"deeply\\\": {\\\"nested\\\": \\\"value\\\"}}",
                "array_str": "[1, 2, {\\\"key\\\": \\\"value\\\"}]",
                "normal": {"key": "value"}
            }
        }
        """
        result = parse_json(nested_inception)
        self.assertIn("outer", result)
        self.assertIn("nested", result)
        self.assertIsInstance(result["nested"]["stringified"], str)
        self.assertIsInstance(result["nested"]["array_str"], str)
        self.assertIsInstance(result["nested"]["normal"], dict)

        # Verify the outermost JSON is chosen over any stringified JSON
        deeply_parsed = json.loads(result["nested"]["stringified"])
        self.assertEqual(deeply_parsed["deeply"]["nested"], "value")

    def test_competing_json_priorities(self):
        """Test that we prioritize the most meaningful JSON when multiple valid options exist."""
        competing_jsons = """
        Here's a small array: [1, 2, 3]
        
        Here's an object with a stringified array:
        {
            "name": "Test",
            "data": "[1, 2, 3, 4, 5]"
        }
        
        And here's another array: [1, 2, 3, 4, 5, 6]
        """
        result = parse_json(competing_jsons)
        # Should choose the object as it's more complex than either array
        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["data"], "[1, 2, 3, 4, 5]")

        # Test case where we have objects of similar size but different depth
        depth_vs_size = """
        {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        
        {"x": {"y": {"z": 123}}}
        """
        result = parse_json(depth_vs_size)
        # Should choose the deeper object even though it has fewer keys overall
        expected = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
