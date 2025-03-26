import json
import gradio as gr

from llm_output_parser import parse_json, parse_jsons, parse_xml


def parse_single_json(text):
    """Parse a single JSON object from text."""
    try:
        result = parse_json(text)
        return json.dumps(result, indent=2)
    except (ValueError, TypeError) as e:
        return f"Error parsing JSON: {str(e)}"


def parse_multiple_jsons(text):
    """Parse multiple JSON objects from text."""
    try:
        results = parse_jsons(text)
        formatted_results = []

        for i, result in enumerate(results):
            formatted_results.append(f"JSON {i+1}:\n{json.dumps(result, indent=2)}")

        return "\n\n".join(formatted_results)
    except (ValueError, TypeError) as e:
        return f"Error parsing JSONs: {str(e)}"


def parse_xml_to_json(text):
    """Parse XML from text and convert to JSON format."""
    try:
        result = parse_xml(text)
        return json.dumps(result, indent=2)
    except (ValueError, TypeError) as e:
        return f"Error parsing XML: {str(e)}"


def process_text(text, parser_type):
    """Process text based on selected parser type."""
    if not text.strip():
        return "Please enter some text to parse."

    if parser_type == "Single JSON":
        return parse_single_json(text)
    elif parser_type == "Multiple JSONs":
        return parse_multiple_jsons(text)
    elif parser_type == "XML":
        return parse_xml_to_json(text)
    else:
        return "Invalid parser type selected."


# Example texts for the interface
example_json = """
```json
{
  "name": "John Doe",
  "age": 30,
  "isEmployed": true,
  "address": {
    "street": "123 Main St",
    "city": "Anytown"
  }
}
```
"""

example_multiple_jsons = """
Here are some JSON objects:

```json
{"id": 1, "name": "Product A"}
```

And another one:

```json
{"id": 2, "name": "Product B"}
```
"""

example_xml = """
```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
  <person id="1">
    <name>John Doe</name>
    <age>30</age>
    <address>
      <street>123 Main St</street>
      <city>Anytown</city>
    </address>
  </person>
</root>
```
"""

# Create Gradio interface
with gr.Blocks(title="LLM Output Parser") as demo:
    gr.Markdown("# LLM Output Parser")
    gr.Markdown("Extract structured data from text containing JSON or XML")

    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="Input Text",
                placeholder="Paste text containing JSON or XML here...",
                lines=15,
            )
            parser_type = gr.Radio(
                choices=["Single JSON", "Multiple JSONs", "XML"],
                label="Parser Type",
                value="Single JSON",
            )
            parse_button = gr.Button("Parse", variant="primary")

        with gr.Column():
            output_text = gr.Textbox(label="Parsed Result", lines=15)

    # Examples
    with gr.Accordion("Example Inputs", open=False):
        gr.Examples(
            examples=[
                [example_json, "Single JSON"],
                [example_multiple_jsons, "Multiple JSONs"],
                [example_xml, "XML"],
            ],
            inputs=[input_text, parser_type],
        )

    # Set up event handler
    parse_button.click(
        fn=process_text, inputs=[input_text, parser_type], outputs=output_text
    )

    gr.Markdown(
        "## How to use\n"
        "1. Paste text containing JSON or XML\n"
        "2. Select the parser type\n"
        "3. Click 'Parse' to extract structured data"
    )

if __name__ == "__main__":
    demo.launch()
