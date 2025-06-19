import unittest

from llm_output_parser import parse_json


class TestNestedJsonStringParsing(unittest.TestCase):
    """Test cases for parsing JSON strings within JSON values."""

    def test_parse_nested_json_strings_basic(self):
        """Test basic nested JSON string parsing."""
        test_input = '{"name": "Test", "data": "[1, 2, 3, 4, 5]"}'

        # Without nested parsing - should remain as string
        result_without = parse_json(test_input)
        self.assertEqual(result_without["name"], "Test")
        self.assertEqual(result_without["data"], "[1, 2, 3, 4, 5]")
        self.assertIsInstance(result_without["data"], str)

        # With nested parsing - should parse the array
        result_with = parse_json(test_input, parse_nested_strings=True)
        self.assertEqual(result_with["name"], "Test")
        self.assertEqual(result_with["data"], [1, 2, 3, 4, 5])
        self.assertIsInstance(result_with["data"], list)

    def test_parse_nested_object_strings(self):
        """Test parsing object strings within JSON."""
        test_input = '{"config": "{\\"timeout\\": 30, \\"retries\\": 3}"}'

        result = parse_json(test_input, parse_nested_strings=True)
        self.assertIsInstance(result["config"], dict)
        self.assertEqual(result["config"]["timeout"], 30)
        self.assertEqual(result["config"]["retries"], 3)

    def test_mixed_nested_strings(self):
        """Test mixed nested strings with both JSON and non-JSON."""
        test_input = """
        {
            "array_string": "[1, 2, 3]",
            "object_string": "{\\"key\\": \\"value\\"}",
            "regular_string": "just a string",
            "number": 42
        }
        """

        result = parse_json(test_input, parse_nested_strings=True)
        self.assertIsInstance(result["array_string"], list)
        self.assertEqual(result["array_string"], [1, 2, 3])

        self.assertIsInstance(result["object_string"], dict)
        self.assertEqual(result["object_string"]["key"], "value")

        self.assertIsInstance(result["regular_string"], str)
        self.assertEqual(result["regular_string"], "just a string")

        self.assertIsInstance(result["number"], int)
        self.assertEqual(result["number"], 42)

    def test_deeply_nested_json_strings(self):
        """Test deeply nested structures with JSON strings."""
        test_input = """
        {
            "level1": {
                "level2": {
                    "data": "[{\\"id\\": 1, \\"name\\": \\"John\\"}, {\\"id\\": 2, \\"name\\": \\"Jane\\"}]"
                }
            }
        }
        """

        result = parse_json(test_input, parse_nested_strings=True)
        nested_data = result["level1"]["level2"]["data"]
        self.assertIsInstance(nested_data, list)
        self.assertEqual(len(nested_data), 2)
        self.assertEqual(nested_data[0]["name"], "John")
        self.assertEqual(nested_data[1]["name"], "Jane")

    def test_invalid_json_strings_ignored(self):
        """Test that invalid JSON strings are left as strings."""
        test_input = """
        {
            "invalid_array": "[1, 2, 3",
            "invalid_object": "{\\"key\\": ",
            "not_json": "hello world",
            "empty": "",
            "valid_array": "[4, 5, 6]"
        }
        """

        result = parse_json(test_input, parse_nested_strings=True)

        # Invalid JSON should remain as strings
        self.assertIsInstance(result["invalid_array"], str)
        self.assertIsInstance(result["invalid_object"], str)
        self.assertIsInstance(result["not_json"], str)
        self.assertIsInstance(result["empty"], str)

        # Valid JSON should be parsed
        self.assertIsInstance(result["valid_array"], list)
        self.assertEqual(result["valid_array"], [4, 5, 6])

    def test_array_with_json_strings(self):
        """Test arrays containing JSON strings."""
        test_input = '["{\\"key\\": \\"value\\"}", "[1, 2, 3]", "regular string"]'

        result = parse_json(test_input, parse_nested_strings=True)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

        # First item should be parsed as object
        self.assertIsInstance(result[0], dict)
        self.assertEqual(result[0]["key"], "value")

        # Second item should be parsed as array
        self.assertIsInstance(result[1], list)
        self.assertEqual(result[1], [1, 2, 3])

        # Third item should remain as string
        self.assertIsInstance(result[2], str)
        self.assertEqual(result[2], "regular string")

    def test_backwards_compatibility(self):
        """Test that normal functionality is unchanged when parse_nested_strings=False."""
        test_cases = [
            '{"name": "John", "age": 30}',
            "[1, 2, 3, 4, 5]",
            '```json\\n{"key": "value"}\\n```',
        ]

        for test_case in test_cases:
            result_default = parse_json(test_case)
            result_explicit = parse_json(test_case, parse_nested_strings=False)
            self.assertEqual(result_default, result_explicit)


if __name__ == "__main__":
    unittest.main()
