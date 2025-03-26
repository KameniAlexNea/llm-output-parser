# LLM Output Parser

[![PyPI version](https://badge.fury.io/py/llm-output-parser.svg)](https://badge.fury.io/py/llm-output-parser)
[![GitHub stars](https://img.shields.io/github/stars/KameniAlexNea/llm-output-parser.svg)](https://github.com/KameniAlexNea/llm-output-parser/stargazers)
[![codecov](https://codecov.io/gh/KameniAlexNea/llm-output-parser/branch/main/graph/badge.svg)](https://codecov.io/gh/KameniAlexNea/llm-output-parser)
[![Build Status](https://github.com/KameniAlexNea/llm-output-parser/workflows/CI/badge.svg)](https://github.com/KameniAlexNea/llm-output-parser/actions)

A robust utility for extracting and parsing structured data (JSON and XML) from unstructured text outputs generated by Large Language Models (LLMs).

## Features

- Extracts JSON and XML from plain text, code blocks, and mixed content
- Handles various JSON formats: objects, arrays, and nested structures
- Converts XML to JSON-compatible dictionary format
- Advanced extraction strategies for multiple JSON/XML objects in text
- Provides robust error handling and recovery strategies
- Works with markdown code blocks (``json ... `` and ``xml ... ``)
- Intelligently selects the most comprehensive structure when multiple are found

## Installation

Install from PyPI:

```bash
pip install llm-output-parser
```

Or install from source:

```bash
git clone https://github.com/KameniAlexNea/llm-output-parser.git
cd llm-output-parser
pip install -e .
```

## Usage

### JSON Parsing

```python
from llm_output_parser import parse_json

# Parse JSON from an LLM response
llm_response = """
Here's the data you requested:


{
    "name": "John Doe",
    "age": 30,
    "skills": ["Python", "Machine Learning", "NLP"]
}


Let me know if you need anything else!
"""

data = parse_json(llm_response)
print(data["name"])  # John Doe
print(data["skills"])  # ['Python', 'Machine Learning', 'NLP']
```

### XML Parsing

```python
from llm_output_parser import parse_xml

# Parse XML from an LLM response and convert to JSON
llm_response = """
Here's the user data in XML format:

```xml
<user id="123">
    <name>Jane Smith</name>
    <email>jane@example.com</email>
    <roles>
        <role>admin</role>
        <role>editor</role>
    </roles>
</user>
```

Let me know if you need any other information.
"""

data = parse_xml(llm_response)
print(data["@id"])  # 123
print(data["name"])  # Jane Smith
print(data["roles"]["role"])  # ['admin', 'editor']

```

### Handling Complex Cases

The library can handle various complex scenarios:

#### JSON Within Text

```python
text = 'The user profile is: {"name": "John", "email": "john@example.com"}'
data = parse_json(text)  # -> {"name": "John", "email": "john@example.com"}
```

#### XML Within Text

```python
text = 'The configuration is: <config><server>localhost</server><port>8080</port></config>'
data = parse_xml(text)  # -> {"server": "localhost", "port": "8080"}
```

#### Multiple JSON/XML Objects

When multiple valid objects are present, the parser returns the most comprehensive one:

```python
# For JSON
text = '''
Small object: {"id": 123}

Larger object:
{
    "user": {
        "id": 123,
        "name": "John",
        "email": "john@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": true
        }
    }
}
'''
data = parse_json(text)  # Returns the larger, more complex object

# For XML
text = '''
Simple: <item>value</item>

Complex:
<product category="electronics">
    <name>Smartphone</name>
    <price currency="USD">999.99</price>
    <features>
        <feature>5G</feature>
        <feature>High-res camera</feature>
    </features>
</product>
'''
data = parse_xml(text)  # Returns the more complex XML converted to JSON
```

### XML to JSON Conversion Details

When parsing XML, the library converts it to a JSON-compatible dictionary with the following conventions:

- XML attributes are prefixed with `@` (e.g., `<item id="123">` becomes `{"@id": "123"}`)
- Text content of elements with attributes or children is stored under `#text` key
- Simple elements with only text become key-value pairs
- Repeated elements are automatically converted to arrays

#### Example:

```python
xml_str = '''
<library>
    <book category="fiction">
        <title>The Great Gatsby</title>
        <author>F. Scott Fitzgerald</author>
    </book>
    <book category="non-fiction">
        <title>Sapiens</title>
        <author>Yuval Noah Harari</author>
    </book>
</library>
'''
data = parse_xml(xml_str)
# Results in:
# {
#     "book": [
#         {
#             "@category": "fiction",
#             "title": "The Great Gatsby",
#             "author": "F. Scott Fitzgerald"
#         },
#         {
#             "@category": "non-fiction",
#             "title": "Sapiens",
#             "author": "Yuval Noah Harari"
#         }
#     ]
# }
```

## Error Handling

If no valid structure can be found, a `ValueError` is raised:

```python
try:
    data = parse_json("No JSON here!")
except ValueError as e:
    print(f"Error: {e}")  # "Error: Failed to parse JSON from the input string."

try:
    data = parse_xml("No XML here!")
except ValueError as e:
    print(f"Error: {e}")  # "Error: Failed to parse XML from the input string."
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
