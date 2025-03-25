import unittest
import xml.etree.ElementTree as ET
from llm_output_parser.xml_parser import _xml_to_json


class TestXmlToJsonConversion(unittest.TestCase):
    """Tests for XML to JSON conversion logic."""

    def test_element_with_text_only(self):
        """Test converting an element with text only."""
        root = ET.fromstring('<root>Simple text</root>')
        result = _xml_to_json(root)
        self.assertEqual(result, 'Simple text')

    def test_element_with_attributes_only(self):
        """Test converting an element with attributes only."""
        root = ET.fromstring('<root id="1" status="active"></root>')
        result = _xml_to_json(root)
        self.assertEqual(result, {'@id': '1', '@status': 'active'})

    def test_element_with_attributes_and_text(self):
        """Test converting an element with both attributes and text."""
        root = ET.fromstring('<root id="1">Content</root>')
        result = _xml_to_json(root)
        self.assertEqual(result, {'@id': '1', '#text': 'Content'})

    def test_element_with_single_child(self):
        """Test converting an element with a single child element."""
        root = ET.fromstring('<root><child>value</child></root>')
        result = _xml_to_json(root)
        self.assertEqual(result, {'child': 'value'})

    def test_element_with_repeated_children(self):
        """Test converting an element with repeated child elements."""
        root = ET.fromstring('''
        <root>
            <item>first</item>
            <item>second</item>
            <item>third</item>
        </root>
        ''')
        result = _xml_to_json(root)
        self.assertEqual(result, {'item': ['first', 'second', 'third']})

    def test_complex_mixed_content(self):
        """Test converting a complex element with mixed content."""
        root = ET.fromstring('''
        <message type="info">
            <header>Notice</header>
            <body>This is important</body>
            <tags>
                <tag>urgent</tag>
                <tag>notification</tag>
            </tags>
        </message>
        ''')
        result = _xml_to_json(root)
        
        expected = {
            '@type': 'info',
            'header': 'Notice',
            'body': 'This is important',
            'tags': {
                'tag': ['urgent', 'notification']
            }
        }
        
        self.assertEqual(result, expected)

    def test_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        root = ET.fromstring('''
        <root>
            <item>
                Text with whitespace
            </item>
        </root>
        ''')
        result = _xml_to_json(root)
        self.assertEqual(result, {'item': 'Text with whitespace'})

    def test_mixed_content_types(self):
        """Test handling elements with different types of children."""
        root = ET.fromstring('''
        <product id="123">
            <name>Laptop</name>
            <specs>
                <memory unit="GB">16</memory>
                <storage unit="TB">1</storage>
            </specs>
            <features>
                <feature>High performance</feature>
                <feature>Lightweight</feature>
            </features>
            <price currency="USD">999.99</price>
        </product>
        ''')
        result = _xml_to_json(root)
        
        expected = {
            '@id': '123',
            'name': 'Laptop',
            'specs': {
                'memory': {'@unit': 'GB', '#text': '16'},
                'storage': {'@unit': 'TB', '#text': '1'}
            },
            'features': {
                'feature': ['High performance', 'Lightweight']
            },
            'price': {'@currency': 'USD', '#text': '999.99'}
        }
        
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
