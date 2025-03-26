.. llm-output-parser documentation master file, created by
   sphinx-quickstart on Wed Mar 26 06:28:39 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

LLM Output Parser
================

Welcome to the documentation for the LLM Output Parser library, a powerful tool for parsing, validating, and transforming outputs from Large Language Models (LLMs).

Overview
--------

The LLM Output Parser provides a flexible framework to:

* Parse structured data from raw LLM outputs
* Validate the format and content of LLM responses
* Transform outputs into usable data structures
* Handle different output formats (JSON, XML, and more)

This library addresses the common challenge of extracting structured data from LLM responses that may contain extra text, formatting errors, or inconsistencies.

Supported Formats
----------------

The library currently supports parsing:

* **JSON**: Extract single or multiple JSON objects from text, even with comments or formatting issues
* **XML**: Convert XML content into JSON-compatible dictionaries
* **More formats coming soon!**

Key Features
-----------

* **Robust Parsing**: Multiple fallback strategies to handle imperfect LLM outputs
* **Format Correction**: Automatically fixes common issues like trailing commas or comments
* **Delimiter Detection**: Extracts content from code blocks (```json, ```xml)
* **Nested Structure Support**: Correctly handles deeply nested data structures

This documentation will guide you through installation, basic and advanced usage, and the API reference.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Installation
-----------

You can install LLM Output Parser using pip:

.. code-block:: bash

   pip install llm-output-parser

For more installation options, see the :doc:`installation` page.

Quick Examples
-------------

**Parsing JSON from LLM output:**

.. code-block:: python

   from llm_output_parser import json_parser
   
   llm_response = '''
   I think this should work:
   ```json
   {
     "name": "John Doe",
     "age": 30,
     "is_active": true
   }
   ```
   Let me know if you need anything else!
   '''
   
   result = json_parser.parse_json(llm_response)
   print(result)  # {'name': 'John Doe', 'age': 30, 'is_active': True}

**Parsing multiple JSON objects:**

.. code-block:: python

   from llm_output_parser import jsons_parser
   
   llm_response = '''
   Here are two user profiles:
   {"id": 1, "name": "Alice"}
   {"id": 2, "name": "Bob"}
   '''
   
   results = jsons_parser.parse_jsons(llm_response)
   print(results)  # [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]

**Parsing XML and converting to JSON:**

.. code-block:: python

   from llm_output_parser import xml_parser
   
   llm_response = '''
   <user id="123">
     <name>Alice Smith</name>
     <roles>
       <role>admin</role>
       <role>editor</role>
     </roles>
   </user>
   '''
   
   result = xml_parser.parse_xml(llm_response)
   print(result)  # {'@id': '123', 'name': 'Alice Smith', 'roles': {'role': ['admin', 'editor']}}

API Reference
------------

.. automodule:: llm_output_parser
   :members:

JSON Parser
~~~~~~~~~~

.. automodule:: llm_output_parser.json_parser
   :members:
   :undoc-members:
   :show-inheritance:

Multiple JSON Parser
~~~~~~~~~~~~~~~~~~

.. automodule:: llm_output_parser.jsons_parser
   :members:
   :undoc-members:
   :show-inheritance:

XML Parser
~~~~~~~~~

.. automodule:: llm_output_parser.xml_parser
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

