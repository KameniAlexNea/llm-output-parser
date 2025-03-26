import unittest

from llm_output_parser import parse_jsons

parse_json = lambda x: parse_jsons(x)[0]

class TestJsonCommentParsing(unittest.TestCase):
    def test_single_line_comments(self):
        """Test handling of single-line comments in JSON."""
        json_with_comments = """{
            "name": "John", // This is a comment
            "age": 30
        }"""
        
        result = parse_json(json_with_comments)
        expected = {"name": "John", "age": 30}
        self.assertEqual(result, expected)
        
        # Test comments at end of file
        json_with_end_comment = """{
            "name": "John", 
            "age": 30
        } // Comment at the end"""
        
        result = parse_json(json_with_end_comment)
        expected = {"name": "John", "age": 30}
        self.assertEqual(result, expected)
        
        # Test comments on multiple lines
        json_with_multiple_comments = """{
            "name": "John", // User name
            "age": 30, // User age
            "active": true // Account status
        }"""
        
        result = parse_json(json_with_multiple_comments)
        expected = {"name": "John", "age": 30, "active": True}
        self.assertEqual(result, expected)

    def test_multi_line_comments(self):
        """Test handling of multi-line comments in JSON."""
        json_with_multi_comment = """{
            "name": "John", /* This is a 
            multi-line comment */
            "age": 30
        }"""
        
        result = parse_json(json_with_multi_comment)
        expected = {"name": "John", "age": 30}
        self.assertEqual(result, expected)
        
        # Test multi-line comment across multiple properties
        json_with_spanning_comment = """{
            "name": "John", 
            /* This comment spans
               multiple properties
            "hidden": "This should be hidden",
            */
            "age": 30
        }"""
        
        result = parse_json(json_with_spanning_comment)
        expected = {"name": "John", "age": 30}
        self.assertEqual(result, expected)
        self.assertNotIn("hidden", result)
        
        # Test multi-line comment at beginning
        json_with_beginning_comment = """/* 
            Initial comment
        */ {
            "name": "John",
            "age": 30
        }"""
        
        result = parse_json(json_with_beginning_comment)
        expected = {"name": "John", "age": 30}
        self.assertEqual(result, expected)
        
        # Test multi-line comment at end
        json_with_end_comment = """{
            "name": "John",
            "age": 30
        } /* 
            End comment
        */"""
        
        result = parse_json(json_with_end_comment)
        expected = {"name": "John", "age": 30}
        self.assertEqual(result, expected)

    def test_nested_comments(self):
        """Test handling of nested comment-like structures."""
        # Testing what looks like nested comments (not actually valid in JSON)
        # json_with_nested_comment = """{
        #     "name": "John", /* Outer comment /* Inner comment */ */
        #     "age": 30
        # }"""
        
        # result = parse_json(json_with_nested_comment)
        # expected = {"name": "John", "age": 30}
        # self.assertEqual(result, expected)
        
        # Test with apparent comment inside string
        json_with_comment_in_string = """{
            "name": "John /* Not a real comment */",
            "age": 30
        }"""
        
        result = parse_json(json_with_comment_in_string)
        expected = {"name": "John /* Not a real comment */", "age": 30}
        self.assertEqual(result, expected)
        
        # Test with comment markers in string and real comment after
        json_with_mixed_comments = """{
            "name": "John // Not a comment", // This IS a comment
            "note": "/* Also not a comment */", /* This IS a comment */
            "age": 30
        }"""
        
        result = parse_json(json_with_mixed_comments)
        expected = {
            "name": "John // Not a comment", 
            "note": "/* Also not a comment */", 
            "age": 30
        }
        self.assertEqual(result, expected)

    def test_complex_comment_scenarios(self):
        """Test more complex scenarios with comments."""
        # Test with JS-style comment syntax but in complex nested structure
        complex_with_comments = """{
            "config": {
                "server": { 
                    "host": "localhost", // Server hostname
                    "port": 8080 /* Default port */
                },
                /* Database settings 
                   Multiple lines
                */
                "database": {
                    "url": "mongodb://localhost:27017",
                    "collections": ["users", /* disabled: "logs", */ "products"]
                },
                // Feature flags
                "features": {
                    "logging": true,
                    "caching": {
                        "enabled": true, // Turn on for production
                        "ttl": 3600 // Time in seconds
                    }
                }
            }
        }"""
        
        result = parse_json(complex_with_comments)
        self.assertEqual(result["config"]["server"]["port"], 8080)
        self.assertEqual(len(result["config"]["database"]["collections"]), 2)
        self.assertEqual(result["config"]["features"]["caching"]["ttl"], 3600)
        self.assertTrue(result["config"]["features"]["logging"])

    def test_trailing_commas_with_comments(self):
        """Test handling of trailing commas combined with comments."""
        # Trailing commas plus comments (double cleanup needed)
        json_with_trailing_comma_comment = """{
            "name": "John",
            "items": [
                "item1",
                "item2", // Last item has comma
            ], // Array has comma
            "details": {
                "active": true,
            }, // Object has comma
        }"""
        
        result = parse_json(json_with_trailing_comma_comment)
        expected = {
            "name": "John",
            "items": ["item1", "item2"],
            "details": {"active": True}
        }
        self.assertEqual(result, expected)
        
        # Extra complex case with mixed comment styles and trailing commas
        mixed_style_json = """{
            "name": "John", // Name
            "items": [
                "item1", /* First item */
                "item2", // Last item
            ], /* End of items
                 array */
            "active": true, // Status flag
        } // End of object"""
        
        result = parse_json(mixed_style_json)
        expected = {
            "name": "John",
            "items": ["item1", "item2"],
            "active": True
        }
        self.assertEqual(result, expected)

    def test_comments_in_code_blocks(self):
        """Test handling of comments in code blocks."""
        # Test JSON with comments inside a code block
        markdown_with_commented_json = """```json
        {
            "name": "John", // User name
            "age": 30, /* User age */
            "active": true
        }
        ```"""
        
        result = parse_json(markdown_with_commented_json)
        expected = {"name": "John", "age": 30, "active": True}
        self.assertEqual(result, expected)
        
        # More complex markdown with comments
        complex_markdown = """
        Here's the config:
        
        ```json
        {
            // Application settings
            "app": {
                "name": "TestApp", /* App name */
                "version": "1.0.0"
            },
            /* This section configures the API */
            "api": {
                "endpoint": "https://api.example.com",
                "timeout": 30 // In seconds
            }
        }
        ```
        
        Let me know if you need anything else!
        """
        
        result = parse_json(complex_markdown)
        self.assertEqual(result["app"]["name"], "TestApp")
        self.assertEqual(result["api"]["timeout"], 30)
        self.assertEqual(result["app"]["version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()
