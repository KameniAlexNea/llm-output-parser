import unittest
from llm_output_parser.jsons_parser import parse_jsons

class TestJsonCodeBlocks(unittest.TestCase):
    def test_json_in_code_block(self):
        """Test extracting JSON from a code block with triple backticks"""
        json_str = '''
        Here is a JSON object:
        ```json
        {"name": "Alice", "skills": ["python", "javascript"]}
        ```
        '''
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"name": "Alice", "skills": ["python", "javascript"]})

    def test_json_in_unmarked_code_block(self):
        """Test extracting JSON from a code block without the json marker"""
        json_str = '''
        Here is another JSON object:
        ```
        {"name": "Bob", "active": true}
        ```
        '''
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"name": "Bob", "active": True})

    def test_multiple_code_blocks(self):
        """Test extracting multiple JSON objects from separate code blocks"""
        json_str = '''
        First JSON:
        ```json
        {"id": 1, "type": "user"}
        ```
        
        Second JSON:
        ```json
        {"id": 2, "type": "admin"}
        ```
        '''
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 2)
        self.assertIn({"id": 1, "type": "user"}, result)
        self.assertIn({"id": 2, "type": "admin"}, result)

    def test_json_with_whitespace_in_code_block(self):
        """Test extracting JSON with extra whitespace in code blocks"""
        json_str = '''
        ```json
        
        {
            "name": "Charlie",
            "age": 42
        }
        
        ```
        '''
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"name": "Charlie", "age": 42})

    def test_nested_code_blocks(self):
        """Test parsing with nested code blocks (code blocks inside code blocks)"""
        json_str = '''
        Here's an example of how code blocks might be nested in documentation:
        
        ```markdown
        # JSON Examples
        
        Here's a simple JSON object:
        
        ```json
        {"name": "Nested Example", "type": "complex"}
        ```
        
        And here's an array:
        
        ```json
        [1, 2, 3]
        ```
        ```
        
        And outside the nested blocks, another JSON:
        
        ```json
        {"status": "success"}
        ```
        '''
        
        result = parse_jsons(json_str)
        # The parser should find at least the non-nested JSON
        self.assertGreaterEqual(len(result), 1)
        self.assertIn({"status": "success"}, result)
        # Ideally it would also find the nested JSONs, but that's a bonus

    def test_malformed_code_blocks(self):
        """Test extracting JSON from malformed or incomplete code blocks"""
        json_str = '''
        1. Incomplete closing backticks:
        ```json
        {"incomplete": true}
        ``
        
        2. Extra backticks:
        `````json
        {"extra": "backticks"}
        ```
        
        3. Mismatched language:
        ```python
        {"language": "mismatch"}
        ```
        
        4. No closing backticks at all:
        ```json
        {"never": "closed"}
        
        5. Valid one:
        ```json
        {"valid": true}
        ```
        '''
        
        result = parse_jsons(json_str)
        # Should at least find the valid one
        self.assertGreaterEqual(len(result), 1)
        self.assertIn({"valid": True}, result)
        # Bonus if it can find any of the others

    def test_code_blocks_with_indentation_and_formatting(self):
        """Test JSON in code blocks with various indentation styles and formatting"""
        json_str = '''
        Example with indented code block:
            ```json
            {
                "indented": {
                    "deeply": {
                        "nested": true
                    }
                }
            }
            ```
        
        Example with inline formatting and code block:
        **Bold text** with ```json {"inline": "formatting"}``` and *italic*.
        
        Example with HTML-like formatting:
        <div>
        ```json
        {
            "html": "like",
            "with": ["tags", "around"]
        }
        ```
        </div>
        '''
        
        result = parse_jsons(json_str)
        self.assertGreaterEqual(len(result), 3)
        
        # Check if all expected objects are found
        found_indented = False
        found_inline = False
        found_html = False
        
        for obj in result:
            if isinstance(obj, dict):
                if "indented" in obj and obj["indented"]["deeply"]["nested"] is True:
                    found_indented = True
                if "inline" in obj and obj["inline"] == "formatting":
                    found_inline = True
                if "html" in obj and obj["html"] == "like":
                    found_html = True
        
        self.assertTrue(found_indented, "Failed to find indented JSON")
        self.assertTrue(found_inline, "Failed to find inline JSON")
        self.assertTrue(found_html, "Failed to find HTML-surrounded JSON")

    def test_real_world_llm_complex_response(self):
        """Test with a complex, realistic LLM response containing multiple formats"""
        json_str = '''
        # Analysis of Customer Feedback

        Based on the data you provided, I've analyzed the customer feedback and categorized it:

        ```json
        {
            "sentiment_summary": {
                "positive": 67.5,
                "neutral": 22.3,
                "negative": 10.2
            },
            "top_themes": [
                {"theme": "product_quality", "mentions": 342, "sentiment": 0.78},
                {"theme": "customer_service", "mentions": 271, "sentiment": 0.42},
                {"theme": "pricing", "mentions": 184, "sentiment": -0.15},
                {"theme": "shipping", "mentions": 139, "sentiment": -0.22}
            ],
            "recommendations": [
                "Focus on improving customer service response times",
                "Address shipping delays, especially for international orders",
                "Maintain current product quality standards"
            ]
        }
        ```

        Let me also provide you with the raw NPS scores:

        ```
        [
            {"month": "January", "nps": 42},
            {"month": "February", "nps": 45},
            {"month": "March", "nps": 47},
            {"month": "April", "nps": 43},
            {"month": "May", "nps": 48}
        ]
        ```

        Here's a simple configuration you might use for your dashboard:

        {
            "dashboard": {
                "refresh_rate": 3600,
                "display_modes": ["chart", "table", "summary"],
                "default_view": "summary",
                "alerts_enabled": true,
                "alert_threshold": -0.1
            }
        }

        Let me know if you need any clarification on these insights!
        '''
        
        result = parse_jsons(json_str)
        self.assertGreaterEqual(len(result), 3)
        
        # Check for sentiment analysis
        sentiment_found = False
        nps_found = False
        dashboard_found = False
        
        for obj in result:
            if isinstance(obj, dict) and "sentiment_summary" in obj:
                sentiment_found = True
                self.assertEqual(len(obj["top_themes"]), 4)
                self.assertEqual(obj["top_themes"][0]["theme"], "product_quality")
            
            if isinstance(obj, list) and len(obj) > 0 and "month" in obj[0]:
                nps_found = True
                self.assertEqual(len(obj), 5)
                self.assertEqual(obj[2]["nps"], 47)
            
            if isinstance(obj, dict) and "dashboard" in obj:
                dashboard_found = True
                self.assertTrue(obj["dashboard"]["alerts_enabled"])
        
        self.assertTrue(sentiment_found, "Failed to extract sentiment analysis JSON")
        self.assertTrue(nps_found, "Failed to extract NPS scores JSON")
        self.assertTrue(dashboard_found, "Failed to extract dashboard config JSON")

    def test_ambiguous_code_blocks(self):
        """Test scenarios where code blocks might be parsed ambiguously"""
        json_str = '''
        Here's a tricky example:
        
        ```
        The following isn't a JSON but might be confused for one:
        {not: json}
        ```
        
        But this is valid:
        ```json
        {"valid": true}
        ```
        
        This is also valid but without language marker:
        ```
        {"unmarked": true}
        ```
        
        This is a code block with JavaScript, not JSON:
        ```javascript
        const data = {
            key: "value" // Not valid JSON (unquoted key, comment)
        };
        ```
        
        And an inline code example: `{"inline": true}`
        '''
        
        result = parse_jsons(json_str)
        
        # It should find at least the valid JSON objects
        valid_found = False
        unmarked_found = False
        inline_found = False
        
        for obj in result:
            if isinstance(obj, dict):
                if "valid" in obj and obj["valid"] is True:
                    valid_found = True
                if "unmarked" in obj and obj["unmarked"] is True:
                    unmarked_found = True
                if "inline" in obj and obj["inline"] is True:
                    inline_found = True
        
        self.assertTrue(valid_found, "Failed to find JSON in marked code block")
        self.assertTrue(unmarked_found, "Failed to find JSON in unmarked code block")
        self.assertTrue(inline_found, "Failed to find inline JSON")
        
        # Make sure the non-JSON wasn't incorrectly parsed
        for obj in result:
            if isinstance(obj, dict) and "not" in obj:
                self.fail("Parser incorrectly identified non-JSON as JSON")

    def test_competing_extraction_methods(self):
        """Test a case where multiple extraction methods would find different results"""
        json_str = '''
        # Example with multiple competing extraction methods
        
        Here's a JSON object inside a code block:
        ```json
        {"name": "Code Block JSON", "type": "marked"}
        ```
        
        Here's a JSON object without a code block: {"name": "Raw JSON", "type": "unmarked"}
        
        Here's a JSON array in an unmarked code block:
        ```
        [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"}
        ]
        ```
        
        And here's an example with both, where the outer JSON should be preferred:
        {"outer": {"inner": {"value": 123}}}
        
        With a similar inner piece: {"inner": {"value": 123}}
        '''
        
        result = parse_jsons(json_str)
        
        # Verify all expected objects were found
        code_block_json = {"name": "Code Block JSON", "type": "marked"}
        raw_json = {"name": "Raw JSON", "type": "unmarked"}
        outer_json = {"outer": {"inner": {"value": 123}}}
        inner_json = {"inner": {"value": 123}}
        
        self.assertIn(code_block_json, result)
        self.assertIn(raw_json, result)
        self.assertIn(inner_json, result)
        self.assertIn(outer_json, result)
        
        # Also check for the array
        array_found = False
        for obj in result:
            if isinstance(obj, list) and len(obj) == 2 and obj[0]["id"] == 1 and obj[1]["id"] == 2:
                array_found = True
                break
                
        self.assertTrue(array_found, "Failed to find the JSON array in unmarked code block")

if __name__ == '__main__':
    unittest.main()
