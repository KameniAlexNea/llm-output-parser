import unittest
from llm_output_parser.xml_parser import parse_xml


class TestXmlParserEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling in XML parsing."""

    def test_empty_string(self):
        """Test that an empty string raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            parse_xml("")
        self.assertIn("Input string is empty", str(context.exception))

    def test_none_input(self):
        """Test that None input raises a TypeError."""
        with self.assertRaises(TypeError) as context:
            parse_xml(None)
        self.assertIn("Input must be a non-empty string", str(context.exception))

    def test_non_string_input(self):
        """Test that non-string input raises a TypeError."""
        with self.assertRaises(TypeError) as context:
            parse_xml(123)
        self.assertIn("Input must be a non-empty string", str(context.exception))

    def test_invalid_xml_input(self):
        """Test that invalid XML raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            parse_xml("This is not XML at all")
        self.assertIn("Failed to parse XML from the input string", str(context.exception))

    def test_malformed_xml(self):
        """Test handling malformed XML."""
        with self.assertRaises(ValueError) as context:
            parse_xml("<root><unclosed>")
        self.assertIn("Failed to parse XML from the input string", str(context.exception))

    def test_broken_xml_in_code_block(self):
        """Test handling broken XML in a code block."""
        text = '''
        ```xml
        <root>
            <broken>
        ```
        '''
        with self.assertRaises(ValueError) as context:
            parse_xml(text)
        self.assertIn("Failed to parse XML from the input string", str(context.exception))

    def test_empty_element(self):
        """Test parsing an empty XML element."""
        result = parse_xml("<root></root>")
        self.assertEqual(result, {})

    def test_self_closing_tags(self):
        """Test parsing self-closing tags."""
        result = parse_xml("<root><item/></root>")
        self.assertEqual(result, {'item': {}})

    def test_xml_with_entity_references(self):
        """Test parsing XML with entity references."""
        result = parse_xml('<root><item>Less than: &lt; Greater than: &gt;</item></root>')
        self.assertEqual(result, {'item': 'Less than: < Greater than: >'})

    def test_xml_with_comments(self):
        """Test parsing XML with comments."""
        xml_str = '''
        <root>
            <!-- This is a comment -->
            <item>value</item>
        </root>
        '''
        result = parse_xml(xml_str)
        self.assertEqual(result, {'item': 'value'})

    def test_xml_structure_depth(self):
        """Test the XML structure depth calculation indirectly through complex parsing."""
        # A deeply nested XML structure
        xml_str = '''
        <level1>
            <level2>
                <level3>
                    <level4>
                        <level5>Deep value</level5>
                    </level4>
                </level3>
            </level2>
        </level1>
        '''
        # A less deeply nested, but longer XML structure
        xml_str2 = '''
        <root>
            <item>1</item>
            <item>2</item>
            <item>3</item>
            <item>4</item>
            <item>5</item>
            <item>6</item>
            <item>7</item>
            <item>8</item>
            <item>9</item>
            <item>10</item>
        </root>
        '''
        
        # When both are present, the deeply nested one should be chosen
        combined = xml_str + "\n\n" + xml_str2
        result = parse_xml(combined)
        
        # The result should match the deeply nested structure, not the longer one
        self.assertIn('level2', result)


if __name__ == '__main__':
    unittest.main()
