import json
import unittest
from llm_output_parser.jsons_parser import parse_jsons

class TestEdgeCases(unittest.TestCase):
    def test_json_with_escaped_characters(self):
        """Test parsing JSON with escaped characters"""
        json_str = r'{"text": "Line 1\nLine 2\tTabbed\r\nCarriage Return"}'
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["text"], "Line 1\nLine 2\tTabbed\r\nCarriage Return")

    def test_json_with_unicode_characters(self):
        """Test parsing JSON with Unicode characters"""
        json_str = '{"message": "こんにちは世界", "emoji": "🚀✨🌟"}'
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["message"], "こんにちは世界")
        self.assertEqual(result[0]["emoji"], "🚀✨🌟")

    def test_json_embedded_in_text(self):
        """Test extracting JSON embedded in regular text"""
        json_str = '''
        Here's some text before the JSON.
        {"result": "success", "count": 42}
        And here's some text after it.
        '''
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"result": "success", "count": 42})

    def test_multiple_json_objects_in_text(self):
        """Test extracting multiple separate JSON objects from text"""
        json_str = '''
        First JSON: {"id": 1}
        Second JSON: {"id": 2}
        Third is an array: [1, 2, 3]
        '''
        result = parse_jsons(json_str)
        self.assertGreaterEqual(len(result), 3)
        self.assertIn({"id": 1}, result)
        self.assertIn({"id": 2}, result)
        self.assertIn([1, 2, 3], result)

    def test_nested_quotes(self):
        """Test JSON with nested quotes"""
        json_str = '{"message": "He said \\"Hello world\\""}'
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["message"], 'He said "Hello world"')

    def test_json_with_special_characters(self):
        """Test JSON with special characters that might cause parsing issues"""
        json_str = '{"url": "https://example.com/path?param=value&other=123"}'
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], "https://example.com/path?param=value&other=123")

    def test_json_with_extremely_long_string(self):
        """Test parsing JSON with an extremely long string value"""
        # Generate a very long string
        long_text = "This is character " + " ".join([f"{i}" for i in range(1, 10001)])
        
        # Create a JSON string with the long text
        json_str = f'{{"long_text": "{long_text}"}}'
        
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["long_text"], long_text)

    def test_json_with_all_escaped_unicode(self):
        """Test parsing JSON where all characters are Unicode escape sequences"""
        # This spells "Hello, World!" using Unicode escape sequences
        json_str = r'{"message": "\u0048\u0065\u006C\u006C\u006F\u002C\u0020\u0057\u006F\u0072\u006C\u0064\u0021"}'
        
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["message"], "Hello, World!")

    def test_json_with_special_whitespace(self):
        """Test parsing JSON with various whitespace characters"""
        # Include various Unicode whitespace characters
        json_str = '''
        {
          "spaces": "normal spaces",
        \t"tabs": "tabbed content",
        \r\n  "newlines": "line breaks",
        \u2003  "em_space": "Unicode space",
        \u2007  "figure_space": "Another Unicode space",
        \u200B  "zero_width_space": "Invisible space",
        \u2028  "line_separator": "Another line break",
          "mixed": "mix\u2003of\u200B\tdifferent   spaces"
        }
        '''
        
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["spaces"], "normal spaces")
        self.assertEqual(result[0]["tabs"], "tabbed content")
        self.assertEqual(result[0]["newlines"], "line breaks")
        self.assertEqual(result[0]["em_space"], "Unicode space")
        self.assertEqual(result[0]["figure_space"], "Another Unicode space")
        self.assertEqual(result[0]["zero_width_space"], "Invisible space")
        self.assertEqual(result[0]["line_separator"], "Another line break")
        self.assertEqual(result[0]["mixed"], "mix\u2003of\u200B\tdifferent   spaces")

    def test_mixed_json_formats_in_markdown(self):
        """Test extracting JSON from a complex Markdown document with various formats"""
        json_str = '''
        # Product Documentation
        
        ## Overview
        
        Our product handles various data formats including JSON. Here are some examples:
        
        ### Basic Configuration
        
        ```json
        {
            "api_key": "your-api-key-here",
            "endpoint": "https://api.example.com/v1",
            "timeout": 30
        }
        ```
        
        ### Response Format
        
        The API returns data in this format:
        
        ```
        {
            "status": "success",
            "code": 200,
            "data": {
                "user_id": 12345,
                "permissions": ["read", "write", "admin"]
            }
        }
        ```
        
        ### Error Example
        
        If something goes wrong, you'll see:
        
        ```javascript
        {
            "status": "error",
            "code": 404,
            "message": "Resource not found"
        }
        ```
        
        ## Additional Examples
        
        Here's an inline example: `{"quick":"example"}` within text.
        
        And a complex nested structure:
        
        {
            "complex": {
                "nested": [
                    {"id": 1, "values": ["a", "b", "c"]},
                    {"id": 2, "values": ["d", "e", "f"]}
                ],
                "metadata": {
                    "generated": true,
                    "timestamp": "2023-08-10T15:42:15Z"
                }
            }
        }
        
        ## CSV Example
        
        We also support CSV:
        
        ```csv
        id,name,value
        1,Item 1,100
        2,Item 2,200
        ```
        
        ## Malformed Example (this shouldn't parse)
        
        ```json
        {
            "incomplete": "missing closing brace"
        ```
        '''
        
        result = parse_jsons(json_str)
        self.assertGreaterEqual(len(result), 4)  # At least 4 valid JSONs should be found
        
        # Check for specific objects
        api_config = {"api_key": "your-api-key-here", "endpoint": "https://api.example.com/v1", "timeout": 30}
        success_response = {"status": "success", "code": 200, "data": {"user_id": 12345, "permissions": ["read", "write", "admin"]}}
        error_example = {"status": "error", "code": 404, "message": "Resource not found"}
        inline_example = {"quick": "example"}
        
        self.assertIn(api_config, result)
        self.assertIn(success_response, result)
        self.assertIn(error_example, result)
        self.assertIn(inline_example, result)
        
        # Check for the complex nested structure
        complex_found = False
        for obj in result:
            if isinstance(obj, dict) and "complex" in obj:
                complex_found = True
                self.assertEqual(len(obj["complex"]["nested"]), 2)
                self.assertEqual(obj["complex"]["nested"][1]["id"], 2)
                self.assertEqual(obj["complex"]["metadata"]["timestamp"], "2023-08-10T15:42:15Z")
        
        self.assertTrue(complex_found, "Failed to find complex nested JSON")

    def test_json_with_pathological_inputs(self):
        """Test the parser with pathological inputs designed to challenge the parser"""
        
        # Test cases that might stress the parser
        test_cases = [
            # Very deeply nested small object - many levels but small payload
            "{" + "".join([f'"level{i}":{{' for i in range(100)]) + '"value":true' + "}"*100,
            
            # Object with many small nested arrays - breadth more than depth
            "{" + ",".join([f'"array{i}":[1,2,3,4,5]' for i in range(100)]) + "}",
            
            # String with many escape sequences
            r'{"escaped":"' + r'\\\\'.join([r'\n\t\r\f\b\"\\' for _ in range(100)]) + r'"}',
            
            # Object with identical keys at different nesting levels
            '{"key":{"key":{"key":{"key":{"key":{"key":"value"}}}}}}',
            
            # JSON with alternating array and object nesting
            '[{"a":[{"b":[{"c":[{"d":[{"e":"deep"}]}]}]}]}]'
        ]
        
        for i, json_str in enumerate(test_cases):
            with self.subTest(f"Pathological case {i+1}"):
                try:
                    result = parse_jsons(json_str)
                    self.assertGreaterEqual(len(result), 1, f"Failed to parse pathological case {i+1}")
                except Exception as e:
                    # Even if it fails, it shouldn't crash but raise a proper exception
                    self.assertIsInstance(e, (ValueError, json.JSONDecodeError), 
                                         f"Unexpected exception type for pathological case {i+1}: {type(e)}")

    def test_json_with_context_clues(self):
        """Test extraction of JSON with context clues that might confuse the parser"""
        json_str = '''
        Here are some tricky cases with context that could confuse extraction:
        
        1. JSON after a colon:
        config: {"debug": true, "verbose": true}
        
        2. JSON in quotes:
        The API returned "{"status": "success", "code": 200}"
        
        3. JSON in angle brackets:
        <div id="data">{"type": "user", "id": 42}</div>
        
        4. JSON with JavaScript prefixes:
        var data = {"name": "John", "active": true};
        const config = {"timeout": 30};
        
        5. JSON in a URL:
        https://example.com/api?data={"query":"test"}
        
        6. JSON after equals sign:
        data={"format":"json", "compression":false}
        '''
        
        result = parse_jsons(json_str)
        self.assertGreaterEqual(len(result), 5)
        
        # Define expected objects
        objects_to_find = [
            {"debug": True, "verbose": True},
            {"status": "success", "code": 200},
            {"type": "user", "id": 42},
            {"name": "John", "active": True},
            {"timeout": 30},
            {"query": "test"},
            {"format": "json", "compression": False}
        ]
        
        # Count how many of our expected objects were found
        found_count = 0
        for expected in objects_to_find:
            for actual in result:
                if actual == expected:
                    found_count += 1
                    break
                    
        # We should find at least 5 of the 7 expected objects
        self.assertGreaterEqual(found_count, 5, 
                              f"Only found {found_count} of the expected objects")

    def test_recovery_from_malformed_json(self):
        """Test the parser's ability to recover usable JSON from malformed input"""
        test_cases = [
            # Case 1: Missing comma - not fixable
            ('{"name": "John" "age": 30}', ValueError),
            
            # Case 2: Extra comma - can be fixed
            ('{"items": ["a", "b", "c",], "count": 3}', 1),
            
            # Case 3: Missing closing brace - not fixable
            ('{"config": {"debug": true', ValueError),
            
            # Case 4: JavaScript comment - can be fixed
            ('{"logging": true, // Enable logging\n"level": "info"}', 1),
            
            # Case 5: Invalid quotes (single quotes) - not fixable
            ("{'name': 'Alice'}", ValueError),
            
            # Case 6: Control characters in string - should be handled
            ('{"message": "Hello\nWorld"}', 1),
            
            # Case 7: Unquoted keys - not fixable
            ('{name: "David"}', ValueError)
        ]
        
        for i, (json_str, expected) in enumerate(test_cases):
            with self.subTest(f"Case {i+1}: {json_str}"):
                if expected == ValueError:
                    with self.assertRaises(ValueError):
                        parse_jsons(json_str)
                else:
                    result = parse_jsons(json_str)
                    self.assertEqual(len(result), expected)

if __name__ == '__main__':
    unittest.main()
