import json
import re
import logging


def parse_json(json_str: str, allow_incomplete: bool = False, strict: bool = True):
    """
    Parses a JSON object from a string that may contain extra text.

    This function attempts multiple approaches to extract JSON:

    1. Directly parsing the entire string.
    2. Extracting JSON enclosed within triple backticks (```json ... ```).
    3. Extracting all valid JSON objects or arrays with balanced delimiters.
    4. If allow_incomplete=True, attempts to repair incomplete/truncated JSON.

    :param json_str: The input string potentially containing a JSON object.
    :type json_str: str
    :param allow_incomplete: Whether to attempt repairing incomplete JSON.
    :type allow_incomplete: bool
    :param strict: Whether to raise errors on failures (when False, returns None on failure).
    :type strict: bool
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
    _extract_json_objects(json_str, "{", "}", parsed_jsons)

    # Attempt 4: Extract JSON arrays with balanced delimiters
    _extract_json_objects(json_str, "[", "]", parsed_jsons)

    # Attempt 5: If allow_incomplete is True, try to repair incomplete JSON
    if allow_incomplete:
        repaired_jsons = _attempt_json_repair(json_str)
        parsed_jsons.extend(repaired_jsons)

    if parsed_jsons:
        # Sort by complexity with improved criteria
        def sort_key(item):
            parsed_obj, json_str = item
            # Calculate various metrics for sorting
            str_len = len(json_str)
            depth = _json_structure_depth(parsed_obj)
            element_count = _count_json_elements(parsed_obj)
            
            # Prioritize objects that contain arrays (likely more complete data)
            has_arrays = _contains_arrays(parsed_obj)
            
            # Prioritize larger structures, but weight element count heavily
            return (element_count * 10, has_arrays, depth, str_len)
        
        sorted_jsons = sorted(parsed_jsons, key=sort_key, reverse=True)
        return sorted_jsons[0][0]
    else:
        if strict:
            raise ValueError("Failed to parse JSON from the input string.")
        else:
            return None


def _json_structure_depth(obj):
    """
    Calculate the depth of a JSON structure.

    :param obj: The JSON object (dict or list)
    :return: The maximum nesting depth
    """
    if isinstance(obj, dict):
        if not obj:
            return 1
        return 1 + max(_json_structure_depth(v) for v in obj.values())
    elif isinstance(obj, list):
        if not obj:
            return 1
        return 1 + max(_json_structure_depth(item) for item in obj)
    else:
        return 0


def _extract_json_objects(
    text: str, open_delimiter: str, close_delimiter: str, results: list
):
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
            if char == "\\" and not escape_char:
                escape_char = True
            else:
                escape_char = False

            pos += 1

        # If we found a balanced object
        if balance == 0:
            # Extract the object string including delimiters
            json_str = text[start:pos]

            # Try multiple parsing approaches
            _try_parse_with_approaches(json_str, results)

        # Move to position after the current match to look for more
        i = pos if balance == 0 else start + 1


def _try_parse_with_approaches(json_str: str, results: list):
    """
    Attempts to parse a JSON string using multiple approaches.

    :param json_str: The JSON string to parse
    :param results: List to append results to
    """
    # Approach 1: Direct parsing
    try:
        parsed = json.loads(json_str)
        if isinstance(parsed, (dict, list)):
            results.append((parsed, json_str))
        return  # Successfully parsed, no need to try other approaches
    except json.JSONDecodeError:
        pass

    # Approach 2: Clean up common formatting issues
    try:
        # Remove JavaScript-style comments (improved for multi-line handling)
        uncleaned = json_str

        # First, handle multi-line comments (/* ... */)
        # This pattern uses a non-greedy match to properly handle nested structures
        cleaned = re.sub(r"/\*[\s\S]*?\*/", "", uncleaned, flags=re.DOTALL)

        # Then handle single-line comments
        cleaned = re.sub(r"//.*?(?:\n|$)", "", cleaned, flags=re.MULTILINE)

        # Remove trailing commas in objects and arrays
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

        parsed = json.loads(cleaned)
        if isinstance(parsed, (dict, list)):
            results.append((parsed, cleaned))
        return  # Successfully parsed after cleaning
    except json.JSONDecodeError:
        pass

    # Approach 3: More aggressive cleaning if the above failed
    try:
        # Try a more comprehensive cleaning approach
        # First remove all comments completely
        aggressive_cleaned = _remove_comments_comprehensive(json_str)

        # Then fix trailing commas
        aggressive_cleaned = re.sub(r",\s*([\]}])", r"\1", aggressive_cleaned)

        parsed = json.loads(aggressive_cleaned)
        if isinstance(parsed, (dict, list)):
            results.append((parsed, aggressive_cleaned))
        return  # Successfully parsed after aggressive cleaning
    except json.JSONDecodeError:
        pass

    # Approach 4: Manual handling of control characters
    try:
        # Replace literal control characters with their proper JSON escape sequences
        control_char_map = {
            "\b": "\\b",  # backspace
            "\f": "\\f",  # form feed
            "\n": "\\n",  # line feed
            "\r": "\\r",  # carriage return
            "\t": "\\t",  # tab
        }

        # First, unescape any already escaped sequences to avoid double escaping
        unescaped = json_str
        for char, escape in control_char_map.items():
            # Replace the escaped version with a placeholder
            placeholder = f"__PLACEHOLDER_{ord(char)}__"
            unescaped = unescaped.replace(escape, placeholder)

        # Then replace actual control characters with proper escapes
        for char, escape in control_char_map.items():
            unescaped = unescaped.replace(char, escape)

        # Restore placeholders to their proper escaped form
        for char, escape in control_char_map.items():
            placeholder = f"__PLACEHOLDER_{ord(char)}__"
            unescaped = unescaped.replace(placeholder, escape)

        # Apply all cleanings together as a last resort
        unescaped = _remove_comments_comprehensive(unescaped)
        unescaped = re.sub(r",\s*([\]}])", r"\1", unescaped)

        parsed = json.loads(unescaped)
        if isinstance(parsed, (dict, list)):
            results.append((parsed, unescaped))
    except (json.JSONDecodeError, Exception):
        # If all approaches fail, don't add anything to results
        pass


def _remove_comments_comprehensive(text):
    """
    Comprehensively removes both single-line and multi-line JavaScript style comments.
    Handles complex cases like nested comments and comments inside strings.

    :param text: The JSON text to clean
    :return: Text with all comments removed
    """
    # Process the string character by character to properly handle comments vs strings
    result = []
    i = 0
    in_string = False
    in_single_comment = False
    in_multi_comment = False
    escape_next = False

    while i < len(text):
        char = text[i]
        next_char = text[i + 1] if i + 1 < len(text) else ""

        # Handle string literals
        if (
            char == '"'
            and not escape_next
            and not in_single_comment
            and not in_multi_comment
        ):
            in_string = not in_string
            result.append(char)

        # Handle escape character within strings
        elif char == "\\" and in_string and not escape_next:
            escape_next = True
            result.append(char)

        # Handle start of single-line comment
        elif (
            char == "/"
            and next_char == "/"
            and not in_string
            and not in_single_comment
            and not in_multi_comment
        ):
            in_single_comment = True
            i += 1  # Skip the next '/' character

        # Handle end of single-line comment
        elif char == "\n" and in_single_comment:
            in_single_comment = False
            result.append(char)  # Keep the newline

        # Handle start of multi-line comment
        elif (
            char == "/"
            and next_char == "*"
            and not in_string
            and not in_single_comment
            and not in_multi_comment
        ):
            in_multi_comment = True
            i += 1  # Skip the next '*' character

        # Handle end of multi-line comment
        elif char == "*" and next_char == "/" and in_multi_comment:
            in_multi_comment = False
            i += 1  # Skip the next '/' character

        # Add character to result if not in a comment
        elif not in_single_comment and not in_multi_comment:
            result.append(char)

        # Reset escape flag
        if escape_next:
            escape_next = False

        i += 1

    return "".join(result)


def _attempt_json_repair(json_str: str):
    """
    Attempts to repair incomplete or truncated JSON strings.

    :param json_str: The potentially incomplete JSON string
    :return: List of tuples (parsed_json, repaired_string)
    """
    repaired_jsons = []

    # Try repairing incomplete objects and arrays in code blocks first
    code_block_matches = re.finditer(r"```(?:json)?\s*([\s\S]*?)\s*```", json_str)
    for match in code_block_matches:
        json_block = match.group(1)
        repaired = _repair_incomplete_json(json_block)
        if repaired:
            repaired_jsons.extend(repaired)

    # Try repairing the entire string
    repaired = _repair_incomplete_json(json_str)
    if repaired:
        repaired_jsons.extend(repaired)

    return repaired_jsons


def _repair_incomplete_json(json_str: str):
    """
    Attempts various repair strategies for incomplete JSON.

    :param json_str: The JSON string to repair
    :return: List of tuples (parsed_json, repaired_string)
    """
    results = []

    # Clean the input string
    cleaned = json_str.strip()
    if not cleaned:
        return results

    # Strategy 1: Try to complete incomplete objects
    if cleaned.startswith("{"):
        repaired_obj = _repair_incomplete_object(cleaned)
        if repaired_obj:
            results.extend(repaired_obj)

    # Strategy 2: Try to complete incomplete arrays
    if cleaned.startswith("["):
        repaired_arr = _repair_incomplete_array(cleaned)
        if repaired_arr:
            results.extend(repaired_arr)

    # Strategy 3: Look for partial JSON structures within the text
    results.extend(_extract_and_repair_partial_json(cleaned))

    return results


def _repair_incomplete_object(json_str: str):
    """
    Attempts to repair incomplete JSON objects.

    :param json_str: JSON string starting with '{'
    :return: List of tuples (parsed_json, repaired_string)
    """
    results = []

    # Remove comments and clean
    cleaned = _remove_comments_comprehensive(json_str)
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)  # Remove trailing commas

    # Count open and close braces to determine if incomplete
    open_braces = cleaned.count("{")
    close_braces = cleaned.count("}")

    if open_braces > close_braces:
        # Try different repair strategies

        # Strategy 1: Complete unfinished key-value pairs
        repaired = _complete_unfinished_pairs(cleaned, "}")
        if repaired:
            try:
                parsed = json.loads(repaired)
                if isinstance(parsed, dict):
                    results.append((parsed, repaired))
                    logging.info(
                        f"Successfully repaired incomplete JSON object: {repaired[:100]}..."
                    )
            except json.JSONDecodeError:
                pass

        # Strategy 2: Just close all open braces
        simple_repair = cleaned + "}" * (open_braces - close_braces)
        try:
            parsed = json.loads(simple_repair)
            if isinstance(parsed, dict):
                results.append((parsed, simple_repair))
                logging.info(
                    f"Successfully repaired JSON by closing braces: {simple_repair[:100]}..."
                )
        except json.JSONDecodeError:
            pass

    return results


def _repair_incomplete_array(json_str: str):
    """
    Attempts to repair incomplete JSON arrays.

    :param json_str: JSON string starting with '['
    :return: List of tuples (parsed_json, repaired_string)
    """
    results = []

    # Remove comments and clean
    cleaned = _remove_comments_comprehensive(json_str)
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)  # Remove trailing commas

    # Count open and close brackets
    open_brackets = cleaned.count("[")
    close_brackets = cleaned.count("]")

    if open_brackets > close_brackets:
        # Strategy 1: Complete unfinished elements
        repaired = _complete_unfinished_pairs(cleaned, "]")
        if repaired:
            try:
                parsed = json.loads(repaired)
                if isinstance(parsed, list):
                    results.append((parsed, repaired))
                    logging.info(
                        f"Successfully repaired incomplete JSON array: {repaired[:100]}..."
                    )
            except json.JSONDecodeError:
                pass

        # Strategy 2: Just close all open brackets
        simple_repair = cleaned + "]" * (open_brackets - close_brackets)
        try:
            parsed = json.loads(simple_repair)
            if isinstance(parsed, list):
                results.append((parsed, simple_repair))
                logging.info(
                    f"Successfully repaired JSON by closing brackets: {simple_repair[:100]}..."
                )
        except json.JSONDecodeError:
            pass

    return results


def _complete_unfinished_pairs(json_str: str, close_char: str):
    """
    Attempts to complete unfinished key-value pairs or array elements.

    :param json_str: The JSON string to repair
    :param close_char: The closing character ('}' or ']')
    :return: Repaired JSON string or None
    """
    # Look for common incomplete patterns
    patterns_and_replacements = [
        # Incomplete key without value: {"key":
        (r'("[^"]*")\s*:\s*$', r'\1: null'),
        # Incomplete key without colon: {"key"
        (r'("[^"]*")\s*$', r'\1: null'),
        # Incomplete key without quotes: {"key
        (r'\{\s*"?([^",:}]+)"?\s*$', r'{"key": null'),
        # Trailing comma: {"key": "value",
        (r',\s*$', ''),
        # Incomplete nested object: {"key": {
        (r':\s*\{\s*$', ': {}'),
        # Incomplete nested array: {"key": [
        (r':\s*\[\s*$', ': []'),
        # Incomplete string value: {"key": "value
        (r':\s*"([^"]*)\s*$', r': "\1"'),
    ]

    repaired = json_str.rstrip()

    for pattern, replacement in patterns_and_replacements:
        if re.search(pattern, repaired):
            repaired = re.sub(pattern, replacement, repaired)
            break

    # Add closing character if needed
    if close_char == "}":
        open_count = repaired.count("{")
        close_count = repaired.count("}")
    else:  # close_char == ']'
        open_count = repaired.count("[")
        close_count = repaired.count("]")

    if open_count > close_count:
        repaired += close_char * (open_count - close_count)

    return repaired if repaired != json_str else None


def _extract_and_repair_partial_json(text: str):
    """
    Extracts and attempts to repair partial JSON structures from text.

    :param text: Text that may contain partial JSON
    :return: List of tuples (parsed_json, repaired_string)
    """
    results = []

    # Look for potential JSON start patterns
    json_start_patterns = [
        r"\{[^}]*$",  # Object that doesn't close
        r"\[[^\]]*$",  # Array that doesn't close
    ]

    for pattern in json_start_patterns:
        matches = re.finditer(pattern, text, re.DOTALL)
        for match in matches:
            partial = match.group(0)
            if partial.startswith("{"):
                repaired = _repair_incomplete_object(partial)
                results.extend(repaired)
            elif partial.startswith("["):
                repaired = _repair_incomplete_array(partial)
                results.extend(repaired)

    return results


def _count_json_elements(obj):
    """
    Count the total number of elements in a JSON structure.
    
    :param obj: The JSON object (dict or list)
    :return: Total count of elements
    """
    if isinstance(obj, dict):
        count = len(obj)
        for value in obj.values():
            count += _count_json_elements(value)
        return count
    elif isinstance(obj, list):
        count = len(obj)
        for item in obj:
            count += _count_json_elements(item)
        return count
    else:
        return 1


def _contains_arrays(obj):
    """
    Check if a JSON structure contains arrays, which often indicates more complete data.
    
    :param obj: The JSON object (dict or list)
    :return: Boolean indicating if arrays are present
    """
    if isinstance(obj, list):
        return True
    elif isinstance(obj, dict):
        for value in obj.values():
            if _contains_arrays(value):
                return True
    return False
