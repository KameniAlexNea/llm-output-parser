import unittest
import xml.etree.ElementTree as ET
from llm_output_parser.xml_parser import parse_xml, _xml_to_json


class TestXmlParserBasic(unittest.TestCase):
    """Basic tests for XML parsing functionality."""

    def test_simple_xml_parsing(self):
        """Test parsing a simple XML string."""
        xml_str = '<root><item>value</item></root>'
        result = parse_xml(xml_str)
        self.assertEqual(result, {'item': 'value'})

    def test_xml_with_attributes(self):
        """Test parsing XML with attributes."""
        xml_str = '<root><item id="1" type="test">value</item></root>'
        result = parse_xml(xml_str)
        self.assertEqual(result, {'item': {'@id': '1', '@type': 'test', '#text': 'value'}})

    def test_nested_xml_structure(self):
        """Test parsing nested XML structure."""
        xml_str = '''
        <root>
            <parent>
                <child>value1</child>
                <child>value2</child>
            </parent>
        </root>
        '''
        result = parse_xml(xml_str)
        self.assertEqual(result, {'parent': {'child': ['value1', 'value2']}})

    def test_complex_nested_xml(self):
        """Test parsing complex nested XML with mixed content."""
        xml_str = '''
        <library>
            <book category="fiction">
                <title>The Great Gatsby</title>
                <author>F. Scott Fitzgerald</author>
                <year>1925</year>
            </book>
            <book category="non-fiction">
                <title>Sapiens</title>
                <author>Yuval Noah Harari</author>
                <year>2011</year>
            </book>
        </library>
        '''
        result = parse_xml(xml_str)
        
        expected = {
            'book': [
                {
                    '@category': 'fiction',
                    'title': 'The Great Gatsby',
                    'author': 'F. Scott Fitzgerald',
                    'year': '1925'
                },
                {
                    '@category': 'non-fiction',
                    'title': 'Sapiens',
                    'author': 'Yuval Noah Harari',
                    'year': '2011'
                }
            ]
        }
        
        self.assertEqual(result, expected)

    def test_xml_to_json_directly(self):
        """Test the _xml_to_json function directly."""
        # Create an XML element tree
        root = ET.Element('root')
        item = ET.SubElement(root, 'item', {'id': '123'})
        item.text = 'test value'
        
        # Convert to JSON
        result = _xml_to_json(root)
        
        self.assertEqual(result, {'item': {'@id': '123', '#text': 'test value'}})

    def test_xml_with_namespaces(self):
        """Test parsing XML with namespaces."""
        xml_str = '''
        <root xmlns:h="http://www.example.org/header">
            <h:header>Header Value</h:header>
            <content>Content Value</content>
        </root>
        '''
        result = parse_xml(xml_str)
        # ElementTree parses namespaces with the full URI in curly braces
        self.assertIn('{http://www.example.org/header}header', result)
        self.assertEqual(result['{http://www.example.org/header}header'], 'Header Value')
        self.assertEqual(result['content'], 'Content Value')


if __name__ == '__main__':
    unittest.main()
