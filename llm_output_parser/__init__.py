# Import the XML parser functionality
from .xml_parser import parse_xml
from .json_parser import parse_json
from .jsons_parser import parse_jsons

# Make parse_xml available when importing the package
__all__ = ["parse_json", "parse_xml", "parse_jsons"]
