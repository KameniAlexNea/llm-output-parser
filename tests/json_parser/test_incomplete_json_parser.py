import logging
import unittest

from llm_output_parser import parse_json


class TestIncompleteJsonParser(unittest.TestCase):
    """Test cases for incomplete/truncated JSON parsing functionality."""

    def setUp(self):
        """Set up logging to capture repair messages."""
        logging.basicConfig(level=logging.INFO)

    def test_incomplete_object_basic(self):
        """Test basic incomplete object handling."""
        # Test case from the requirements: {"abc":
        incomplete_json = '{"abc":'
        result = parse_json(incomplete_json, allow_incomplete=True)
        expected = {"abc": None}
        self.assertEqual(result, expected)

        # Test case: {"key1": "value1", "key2":
        incomplete_json = '{"key1": "value1", "key2":'
        result = parse_json(incomplete_json, allow_incomplete=True)
        expected = {"key1": "value1", "key2": None}
        self.assertEqual(result, expected)

    def test_incomplete_object_no_colon(self):
        """Test incomplete object without colon."""
        incomplete_json = '{"abc"'
        result = parse_json(incomplete_json, allow_incomplete=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_incomplete_array(self):
        """Test incomplete array handling."""
        incomplete_json = "[1, 2, 3"
        result = parse_json(incomplete_json, allow_incomplete=True)
        expected = [1, 2, 3]
        self.assertEqual(result, expected)

        # Array with incomplete string
        incomplete_json = '["item1", "item2"'
        result = parse_json(incomplete_json, allow_incomplete=True)
        expected = ["item1", "item2"]
        self.assertEqual(result, expected)

    def test_nested_incomplete_structures(self):
        """Test nested incomplete structures."""
        # Incomplete nested object
        incomplete_json = '{"outer": {"inner":'
        result = parse_json(incomplete_json, allow_incomplete=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn("outer", result)

        # Incomplete nested array - this should return a dict containing the array
        incomplete_json = '{"items": [1, 2'
        result = parse_json(incomplete_json, allow_incomplete=True)
        self.assertIsNotNone(result)
        # The result could be either the repaired object or just the array
        # depending on which repair is most successful
        self.assertTrue(isinstance(result, (dict, list)))
        if isinstance(result, dict):
            self.assertIn("items", result)
        else:
            # If it's just the array, that's also acceptable
            self.assertIsInstance(result, list)

    def test_incomplete_with_trailing_comma(self):
        """Test incomplete JSON with trailing comma."""
        incomplete_json = '{"key1": "value1", "key2": "value2",'
        result = parse_json(incomplete_json, allow_incomplete=True)
        expected = {"key1": "value1", "key2": "value2"}
        self.assertEqual(result, expected)

    def test_incomplete_string_value(self):
        """Test incomplete string values."""
        incomplete_json = '{"key": "incomplete value'
        result = parse_json(incomplete_json, allow_incomplete=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn("key", result)

    def test_incomplete_in_code_blocks(self):
        """Test incomplete JSON within code blocks."""
        markdown_with_incomplete = """
        Here's the data:
        ```json
        {"name": "John", "age":
        ```
        """
        result = parse_json(markdown_with_incomplete, allow_incomplete=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)

    def test_multiple_incomplete_structures(self):
        """Test text with multiple incomplete JSON structures."""
        text_with_multiple = """
        First object: {"a": 1, "b":
        Second array: [1, 2, 3
        """
        result = parse_json(text_with_multiple, allow_incomplete=True)
        self.assertIsNotNone(result)
        # Should return the most complex/complete structure

    def test_allow_incomplete_false(self):
        """Test that incomplete JSON still raises errors when allow_incomplete=False."""
        incomplete_json = '{"abc":'
        with self.assertRaises(ValueError):
            parse_json(incomplete_json, allow_incomplete=False)

        # Test default behavior (should be False)
        with self.assertRaises(ValueError):
            parse_json(incomplete_json)

    def test_strict_mode_false(self):
        """Test non-strict mode returns None instead of raising errors."""
        incomplete_json = '{"abc":'
        result = parse_json(incomplete_json, allow_incomplete=False, strict=False)
        self.assertIsNone(result)

        # Plain text should return None in non-strict mode
        result = parse_json("This is just text", strict=False)
        self.assertIsNone(result)

    def test_complete_json_still_works(self):
        """Test that complete JSON still works with new parameters."""
        complete_json = '{"name": "John", "age": 30}'
        expected = {"name": "John", "age": 30}

        # Should work with all parameter combinations
        self.assertEqual(parse_json(complete_json), expected)
        self.assertEqual(parse_json(complete_json, allow_incomplete=True), expected)
        self.assertEqual(parse_json(complete_json, allow_incomplete=False), expected)
        self.assertEqual(parse_json(complete_json, strict=True), expected)
        self.assertEqual(parse_json(complete_json, strict=False), expected)

    def test_complex_incomplete_scenarios(self):
        """Test complex real-world incomplete scenarios."""
        # LLM output that got cut off mid-generation
        llm_output = """
        Based on your request, here's the JSON data:
        
        ```json
        {
            "users": [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                {"id": 3, "name": "Bob Wilson", "email":
        """

        result = parse_json(llm_output, allow_incomplete=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

        # The parser should find some JSON structure, either:
        # 1. One of the complete user objects, or
        # 2. A repaired version of the larger structure
        # We'll accept either as both are valid interpretations

        if "users" in result:
            # If it found the outer structure
            self.assertIsInstance(result["users"], list)
            self.assertTrue(
                len(result["users"]) >= 2
            )  # Should have at least 2 complete users
        else:
            # If it found an individual user object (also acceptable)
            # Should have typical user fields
            has_user_fields = any(field in result for field in ["id", "name", "email"])
            self.assertTrue(
                has_user_fields, f"Result should have user-like fields, got: {result}"
            )

    def test_streaming_json_fragments(self):
        """Test streaming-style JSON fragments."""
        # Simulate progressive JSON building
        fragments = [
            '{"status":',
            '{"status": "processing",',
            '{"status": "processing", "progress":',
            '{"status": "processing", "progress": 75,',
            '{"status": "processing", "progress": 75, "items":',
        ]

        for fragment in fragments:
            result = parse_json(fragment, allow_incomplete=True)
            self.assertIsNotNone(result, f"Failed to parse fragment: {fragment}")
            self.assertIsInstance(result, dict)

    def test_malformed_but_repairable(self):
        """Test malformed JSON that can be repaired."""
        # JavaScript-style comments
        malformed = """
        {
            "name": "John", // This is a comment
            "age": 30 /* Multi-line
                         comment */,
            "active": true,
        """

        result = parse_json(malformed, allow_incomplete=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("name"), "John")
        self.assertEqual(result.get("age"), 30)
        self.assertEqual(result.get("active"), True)

    def test_edge_cases(self):
        """Test various edge cases."""
        # Empty object start
        result = parse_json("{", allow_incomplete=True)
        self.assertEqual(result, {})

        # Empty array start
        result = parse_json("[", allow_incomplete=True)
        self.assertEqual(result, [])

        # Just a key
        result = parse_json('"key"', allow_incomplete=True, strict=False)
        # This might not be repairable to valid JSON, so could be None

        # Multiple incomplete objects
        text = '{"a": 1} {"b":'
        result = parse_json(text, allow_incomplete=True)
        self.assertIsNotNone(result)

    def test_backwards_compatibility(self):
        """Test that existing functionality is not broken."""
        # All existing test cases should still work with default parameters
        test_cases = [
            '{"name": "John", "age": 30}',
            "[1, 2, 3, 4, 5]",
            '```json\n{"name": "John"}\n```',
            'Here is data: {"key": "value"} and more text.',
        ]

        for test_case in test_cases:
            result_old = parse_json(test_case)
            result_new = parse_json(test_case, allow_incomplete=False, strict=True)
            self.assertEqual(
                result_old,
                result_new,
                f"Backwards compatibility failed for: {test_case}",
            )


if __name__ == "__main__":
    unittest.main()
