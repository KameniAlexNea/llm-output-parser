import unittest

from llm_output_parser.jsons_parser import parse_jsons


class TestBasicJsonParsing(unittest.TestCase):
    def test_valid_json_object(self):
        """Test parsing a valid JSON object"""
        json_str = '{"name": "John", "age": 30}'
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"name": "John", "age": 30})

    def test_valid_json_array(self):
        """Test parsing a valid JSON array"""
        json_str = "[1, 2, 3, 4, 5]"
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [1, 2, 3, 4, 5])

    def test_empty_input(self):
        """Test that empty input raises ValueError"""
        with self.assertRaises(ValueError) as context:
            parse_jsons("")
        self.assertIn("Input string is empty", str(context.exception))

    def test_none_input(self):
        """Test that None input raises TypeError"""
        with self.assertRaises(TypeError) as context:
            parse_jsons(None)
        self.assertIn("Input must be a non-empty string", str(context.exception))

    def test_non_string_input(self):
        """Test that non-string input raises TypeError"""
        with self.assertRaises(TypeError) as context:
            parse_jsons(123)
        self.assertIn("Input must be a non-empty string", str(context.exception))

    def test_invalid_json(self):
        """Test handling completely invalid JSON"""
        json_str = "This is not JSON at all"
        with self.assertRaises(ValueError) as context:
            parse_jsons(json_str)
        self.assertIn(
            "Failed to parse any JSON from the input string", str(context.exception)
        )

    def test_complex_json_object(self):
        """Test parsing a more complex JSON object with nested structures and various data types"""
        json_str = """
        {
            "id": "b07f5168-1e38-4cd2-9cd8-6d8d6c3f5d5b",
            "created_at": "2023-07-15T09:12:33.001Z",
            "status": "active",
            "metrics": {
                "views": 1205,
                "likes": 360,
                "shares": 124,
                "conversion_rate": 0.0298
            },
            "tags": ["premium", "featured", "seasonal"],
            "availability": true,
            "variants": [
                {"sku": "ABC123", "color": "red", "size": "S", "price": 24.99},
                {"sku": "ABC124", "color": "red", "size": "M", "price": 24.99},
                {"sku": "ABC125", "color": "blue", "size": "M", "price": 26.99}
            ],
            "metadata": {
                "origin": "api",
                "last_updated": "2023-08-01T14:22:10.555Z"
            }
        }
        """
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "b07f5168-1e38-4cd2-9cd8-6d8d6c3f5d5b")
        self.assertEqual(result[0]["metrics"]["conversion_rate"], 0.0298)
        self.assertEqual(len(result[0]["variants"]), 3)
        self.assertEqual(result[0]["variants"][2]["price"], 26.99)
        self.assertEqual(result[0]["tags"][1], "featured")

    def test_unusual_numeric_formats(self):
        """Test parsing JSON with various numeric formats including scientific notation"""
        json_str = """
        {
            "integers": [42, -17, 0, 9223372036854775807],
            "floats": [3.14159, -0.0001, 2.0, 1e-10],
            "scientific": [1e10, -2.5e-5, 6.022e23],
            "special_cases": [0.0, -0.0]
        }
        """
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["integers"][3], 9223372036854775807)
        self.assertAlmostEqual(result[0]["floats"][0], 3.14159)
        self.assertEqual(result[0]["scientific"][0], 1e10)
        self.assertAlmostEqual(result[0]["scientific"][1], -2.5e-5)
        self.assertEqual(result[0]["special_cases"][1], -0.0)

    def test_json_with_string_variations(self):
        """Test parsing JSON with various string formats and special characters"""
        json_str = r"""
        {
            "empty": "",
            "spaces": "   spaced    content   ",
            "quotes": "She said: \"This is in quotes\"",
            "slashes": "Backslashes \\ and more \\\\ and even more \\\\\\",
            "unicode": "Unicode: \u00A9 \u2665 \u263A",
            "control_chars": "Newline: \n Tab: \t Backspace: \b Form feed: \f Carriage return: \r",
            "url": "https://example.com/path?q=test&lang=en#section",
            "multiline": "Line 1\nLine 2\nLine 3"
        }
        """
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["empty"], "")
        self.assertEqual(result[0]["spaces"], "   spaced    content   ")
        self.assertEqual(result[0]["quotes"], 'She said: "This is in quotes"')
        self.assertEqual(
            result[0]["slashes"], "Backslashes \\ and more \\\\ and even more \\\\\\"
        )
        self.assertEqual(result[0]["unicode"], "Unicode: © ♥ ☺")
        self.assertEqual(
            result[0]["control_chars"],
            "Newline: \n Tab: \t Backspace: \b Form feed: \f Carriage return: \r",
        )
        self.assertEqual(
            result[0]["url"], "https://example.com/path?q=test&lang=en#section"
        )
        self.assertEqual(result[0]["multiline"], "Line 1\nLine 2\nLine 3")

    def test_malformed_json_edge_cases(self):
        """Test with JSON strings that are almost valid but have subtle issues"""
        # This test verifies that the parser can handle slightly malformed JSON
        # and either fix it or reject it appropriately
        test_cases = [
            # Missing closing brace - should fail
            ('{"name": "Alice", "age": 30', ValueError),
            # Missing comma - should fail
            ('{"name": "Bob" "age": 25}', ValueError),
            # Single quotes - should fail (JSON requires double quotes)
            ("{'name': 'Charlie'}", ValueError),
            # JavaScript-style object with unquoted keys - should fail
            ("{name: 'David'}", ValueError),
            # Almost JSON - JavaScript notation with unquoted property - should fail
            ("var data = {name: 'Eve'};", ValueError),
        ]

        for json_str, expected_exception in test_cases:
            with self.subTest(json_str=json_str):
                with self.assertRaises(expected_exception):
                    parse_jsons(json_str)

    def test_simultaneous_parsing_approaches(self):
        """Test that the parser tries multiple approaches and uses the most appropriate one"""
        # This tests the parser's ability to choose between different strategies
        test_cases = [
            # Case 1: Clean JSON that should be parsed directly in the first attempt
            ('{"simple": true}', 1),
            # Case 2: JSON with a JavaScript-like comment that needs cleaning
            ('{"commented": true /* with comment */}', 1),
            # Case 3: JSON with trailing commas that needs cleaning
            ('{"items": ["a", "b", "c",]}', 1),
            # Case 4: JSON with control characters that needs special handling
            ('{"text": "Line 1\nLine 2"}', 1),
            # Case 5: Multiple JSONs in one string
            ('{"first": 1} {"second": 2}', 2),
        ]

        for json_str, expected_count in test_cases:
            with self.subTest(json_str=json_str):
                result = parse_jsons(json_str)
                self.assertEqual(
                    len(result),
                    expected_count,
                    f"Expected {expected_count} JSON objects, got {len(result)}",
                )

    def test_parser_resilience(self):
        """Test the parser's resilience to variations in input format"""
        # Test unusual but technically valid JSON formats
        test_cases = [
            # Minimal valid JSON values
            ("true", 1),
            ("false", 1),
            ("null", 1),
            ("42", 1),
            ('"string"', 1),
            # Whitespace variations
            ('   {   "spaced"   :   true   }   ', 1),
            ('\n\n{"newlines":\ntrue\n}\n', 1),
            ('\t{"tabs":\t["a",\t"b"]}\t', 1),
            # Empty structures
            ("{}", 1),
            ("[]", 1),
            ('{"empty":{}}', 1),
            ('{"empty":[]}', 1),
        ]

        for json_str, expected_count in test_cases:
            with self.subTest(json_str=json_str):
                result = parse_jsons(json_str)
                self.assertEqual(len(result), expected_count)


if __name__ == "__main__":
    unittest.main()
