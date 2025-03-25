import json
import re


def parse_json(json_str: str):
    """
    Parses a JSON object from a string that may contain extra text.

    This function attempts three approaches to extract JSON:

    1. Directly parsing the entire string.
    2. Extracting JSON enclosed within triple backticks (```json ... ```).
    3. Extracting all valid JSON objects or arrays with balanced delimiters.

    :param json_str: The input string potentially containing a JSON object.
    :type json_str: str
    :return: The parsed JSON object if successfully extracted, otherwise None.
    :rtype: dict or list or None
    """
    if json_str is None or not isinstance(json_str, str):
        raise TypeError("Input must be a non-empty string.")
    if not json_str:
        raise ValueError("Input string is empty.")
    
    # Store all successfully parsed JSON objects
    parsed_jsons = []
    
    # Attempt 1: Try to load the entire string as JSON.
    try:
        parsed = json.loads(json_str)
        parsed_jsons.append((parsed, json_str))
    except json.JSONDecodeError:
        pass

    # Attempt 2: Look for JSON blocks delimited by ```json and ```.
    # Find all code blocks and try to parse each one
    code_block_matches = re.finditer(r"```(?:json)?\s*([\s\S]*?)\s*```", json_str)
    for match in code_block_matches:
        json_block = match.group(1)
        try:
            parsed = json.loads(json_block)
            parsed_jsons.append((parsed, json_block))
        except json.JSONDecodeError:
            pass

    # Attempt 3: Extract JSON objects with balanced delimiters
    extract_json_objects(json_str, '{', '}', parsed_jsons)
    
    # Attempt 4: Extract JSON arrays with balanced delimiters
    extract_json_objects(json_str, '[', ']', parsed_jsons)

    if parsed_jsons:
        # Return the most comprehensive JSON (the one with the longest string representation)
        return max(parsed_jsons, key=lambda x: len(x[1]))[0]
    else:
        raise ValueError("Failed to parse JSON from the input string.")


def extract_json_objects(text, open_delimiter, close_delimiter, results):
    """
    Extracts all valid JSON objects or arrays from the text with properly balanced delimiters.
    
    :param text: The text to search in
    :param open_delimiter: Opening delimiter ('{' or '[')
    :param close_delimiter: Closing delimiter ('}' or ']')
    :param results: List to append results to (tuple of (parsed_json, json_string))
    """
    i = 0
    while i < len(text):
        # Find the next opening delimiter
        start = text.find(open_delimiter, i)
        if start == -1:
            break
            
        # Track balanced delimiters
        balance = 1
        pos = start + 1
        in_string = False
        escape_char = False
        
        # Scan for the matching closing delimiter
        while pos < len(text) and balance > 0:
            char = text[pos]
            
            # Handle string literals (ignore delimiters inside strings)
            if char == '"' and not escape_char:
                in_string = not in_string
            elif not in_string:
                if char == open_delimiter:
                    balance += 1
                elif char == close_delimiter:
                    balance -= 1
            
            # Track escape characters
            if char == '\\' and not escape_char:
                escape_char = True
            else:
                escape_char = False
                
            pos += 1
            
        # If we found a balanced object
        if balance == 0:
            # Extract the object string including delimiters
            json_str = text[start:pos]
            
            # Attempt to parse it
            try:
                parsed = json.loads(json_str)
                results.append((parsed, json_str))
            except json.JSONDecodeError:
                pass
                
        # Move to position after the current match to look for more
        i = pos if balance == 0 else start + 1
