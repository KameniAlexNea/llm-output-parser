import unittest
from llm_output_parser import parse_xml


class TestXmlParserExtraction(unittest.TestCase):
    """Tests for extracting XML from various text formats."""

    def test_extract_from_markdown_code_block(self):
        """Test extracting XML from a markdown code block."""
        text = '''
        Here is an XML example:
        
        ```xml
        <root>
            <element>Content</element>
        </root>
        ```
        
        This is how you define XML.
        '''
        
        result = parse_xml(text)
        self.assertEqual(result, {'element': 'Content'})

    def test_extract_without_xml_tag(self):
        """Test extracting XML from a code block without xml tag."""
        text = '''
        Example:
        
        ```
        <person>
            <name>John Doe</name>
            <age>30</age>
        </person>
        ```
        '''
        
        result = parse_xml(text)
        self.assertEqual(result, {'name': 'John Doe', 'age': '30'})

    def test_extract_xml_mixed_with_text(self):
        """Test extracting XML embedded within regular text."""
        text = '''
        Let me show you an example: <user><name>Alice</name><role>Admin</role></user>
        
        This is a simple XML element representing a user.
        '''
        
        result = parse_xml(text)
        self.assertEqual(result, {'name': 'Alice', 'role': 'Admin'})

    def test_extract_with_xml_declaration(self):
        """Test extracting XML with a declaration."""
        text = '''
        An XML document typically starts with:
        
        <?xml version="1.0" encoding="UTF-8"?>
        <root>
            <item>Test</item>
        </root>
        '''
        
        result = parse_xml(text)
        self.assertEqual(result, {'item': 'Test'})

    def test_extract_from_multiple_xml_blocks(self):
        """Test extracting the most complex XML when multiple blocks are present."""
        text = '''
        Simple example: <test>value</test>
        
        More complex:
        <configuration>
            <settings>
                <timeout>30</timeout>
                <retries>3</retries>
            </settings>
            <logging level="debug">
                <file>app.log</file>
            </logging>
        </configuration>
        '''
        
        result = parse_xml(text)
        # Should return the more complex XML structure
        self.assertIn('settings', result)
        self.assertEqual(result['settings'], {'timeout': '30', 'retries': '3'})
        self.assertIn('logging', result)
        self.assertEqual(result['logging'], {'@level': 'debug', 'file': 'app.log'})

    def test_extract_with_cdata(self):
        """Test extracting XML with CDATA sections."""
        text = '''
        XML with CDATA:
        <message>
            <content><![CDATA[<p>This is HTML content & special chars like & < > " '</p>]]></content>
        </message>
        '''
        
        result = parse_xml(text)
        self.assertEqual(result, {'content': '<p>This is HTML content & special chars like & < > " \'</p>'})


if __name__ == '__main__':
    unittest.main()
