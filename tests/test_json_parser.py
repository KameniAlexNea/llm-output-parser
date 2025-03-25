import unittest
import json
from llm_output_parser import parse_json


class TestJsonParser(unittest.TestCase):
    def test_direct_json_parsing(self):
        """Test direct parsing of valid JSON strings."""
        # Test simple object
        simple_json = '{"name": "John", "age": 30}'
        expected = {"name": "John", "age": 30}
        self.assertEqual(parse_json(simple_json), expected)
        
        # Test nested object
        nested_json = '{"person": {"name": "John", "age": 30}, "location": {"city": "New York", "zip": "10001"}}'
        expected = {"person": {"name": "John", "age": 30}, "location": {"city": "New York", "zip": "10001"}}
        self.assertEqual(parse_json(nested_json), expected)
        
        # Test array
        array_json = '[1, 2, 3, 4, 5]'
        expected = [1, 2, 3, 4, 5]
        self.assertEqual(parse_json(array_json), expected)
        
        # Test complex object with arrays
        complex_json = '{"name": "John", "hobbies": ["reading", "coding", "hiking"], "addresses": [{"type": "home", "address": "123 Main St"}, {"type": "work", "address": "456 Market St"}]}'
        expected = {
            "name": "John", 
            "hobbies": ["reading", "coding", "hiking"], 
            "addresses": [
                {"type": "home", "address": "123 Main St"}, 
                {"type": "work", "address": "456 Market St"}
            ]
        }
        self.assertEqual(parse_json(complex_json), expected)

    def test_backtick_json_extraction(self):
        """Test extraction of JSON from backtick code blocks."""
        # Basic code block
        markdown_json = '```json\n{"name": "John", "age": 30}\n```'
        expected = {"name": "John", "age": 30}
        self.assertEqual(parse_json(markdown_json), expected)
        
        # Code block with surrounding text
        text_with_json = 'Here is the data:\n```json\n{"name": "John", "age": 30}\n```\nAs you can see above.'
        expected = {"name": "John", "age": 30}
        self.assertEqual(parse_json(text_with_json), expected)
        
        # Code block without json specifier
        plain_block = '```\n{"name": "John", "age": 30}\n```'
        expected = {"name": "John", "age": 30}
        self.assertEqual(parse_json(plain_block), expected)
        
        # Multiple code blocks (should take the first one)
        multiple_blocks = '```json\n{"name": "John"}\n```\nAnd another:\n```json\n{"name": "Jane"}\n```'
        expected = {"name": "John"}
        self.assertEqual(parse_json(multiple_blocks), expected)
        
        # Code block with extra whitespace
        whitespace_block = '```json  \n  {"name": "John", "age": 30}  \n   ```'
        expected = {"name": "John", "age": 30}
        self.assertEqual(parse_json(whitespace_block), expected)

    def test_braces_extraction(self):
        """Test extraction of JSON from braces in text."""
        # Simple text with JSON object
        text_with_json = 'Here is the data: {"name": "John", "age": 30} - end of data.'
        expected = {"name": "John", "age": 30}
        self.assertEqual(parse_json(text_with_json), expected)
        
        # Text with multiple JSON objects (should extract the complete outer one)
        nested_text = 'Start {"outer": {"inner": {"value": 42}}, "data": [1,2,3]} End'
        expected = {"outer": {"inner": {"value": 42}}, "data": [1,2,3]}
        self.assertEqual(parse_json(nested_text), expected)
        
        # Text with array
        array_text = 'Here is an array: [1, 2, {"name": "item"}] and more text.'
        expected = [1, 2, {"name": "item"}]
        self.assertEqual(parse_json(array_text), expected)

    def test_multiline_json(self):
        """Test extraction of multiline JSON."""
        # Multiline direct JSON
        multiline_json = '''{
            "name": "John",
            "age": 30,
            "hobbies": [
                "reading",
                "coding",
                "hiking"
            ]
        }'''
        expected = {
            "name": "John",
            "age": 30,
            "hobbies": ["reading", "coding", "hiking"]
        }
        self.assertEqual(parse_json(multiline_json), expected)
        
        # Multiline JSON in code block
        multiline_block = '''```json
        {
            "name": "John",
            "age": 30,
            "hobbies": [
                "reading",
                "coding",
                "hiking"
            ]
        }
        ```'''
        expected = {
            "name": "John",
            "age": 30,
            "hobbies": ["reading", "coding", "hiking"]
        }
        self.assertEqual(parse_json(multiline_block), expected)
        
        # Multiline JSON in text
        multiline_text = '''Here is the data: 
        {
            "name": "John",
            "age": 30,
            "hobbies": [
                "reading",
                "coding",
                "hiking"
            ]
        }
        End of data.'''
        expected = {
            "name": "John",
            "age": 30,
            "hobbies": ["reading", "coding", "hiking"]
        }
        self.assertEqual(parse_json(multiline_text), expected)

    def test_edge_cases(self):
        """Test edge cases and potential issues."""
        # Empty object
        empty_obj = '{}'
        self.assertEqual(parse_json(empty_obj), {})
        
        # Empty array
        empty_arr = '[]'
        self.assertEqual(parse_json(empty_arr), [])
        
        # Object with unicode characters
        unicode_json = '{"name": "José", "city": "São Paulo", "symbol": "€"}'
        expected = {"name": "José", "city": "São Paulo", "symbol": "€"}
        self.assertEqual(parse_json(unicode_json), expected)
        
        # Object with escaped quotes and backslashes
        escaped_json = '{"text": "He said, \\"Hello\\"", "path": "C:\\\\Users\\\\John"}'
        expected = {"text": 'He said, "Hello"', "path": 'C:\\Users\\John'}
        self.assertEqual(parse_json(escaped_json), expected)
        
        # Object with null, boolean and number types
        mixed_types = '{"name": null, "active": true, "count": 42, "ratio": 3.14}'
        expected = {"name": None, "active": True, "count": 42, "ratio": 3.14}
        self.assertEqual(parse_json(mixed_types), expected)
        
        # Very large nested structure
        large_json = '{' + '"level1": {' * 10 + '"value": 42' + '}' * 10 + '}'
        result = parse_json(large_json)
        self.assertIsNotNone(result)
        
        # JSON with comments-like text (not valid JSON but our parser might handle it)
        pseudo_comments = '''
        {
            "name": "John" /* This is the name */,
            "age": 30 // This is the age
        }
        '''
        partial = parse_json(pseudo_comments)
        assert partial is not None

    def test_error_cases(self):
        """Test cases that should raise errors."""
        # No valid JSON in text
        with self.assertRaises(ValueError):
            parse_json("This is just plain text.")
        
        # Incomplete JSON object
        with self.assertRaises(ValueError):
            parse_json('{"name": "John", "age":')
        
        # Malformed JSON with syntax error
        partial = parse_json('{"name": "John", "age": 30,}')
        assert partial is not None
        
        # Invalid JSON type (JavaScript function)
        with self.assertRaises(ValueError):
            parse_json('{"func": function() { return true; }}')
            
        # Empty string
        with self.assertRaises(ValueError):
            parse_json("")
            
        # None input (different from the function specification but good to test)
        with self.assertRaises(TypeError):
            parse_json(None)


if __name__ == "__main__":
    unittest.main()
