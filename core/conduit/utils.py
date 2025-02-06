import json
import logging
import re
import requests
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from .models import Service, Endpoint, APIRequestLog

logger = logging.getLogger(__name__)

def handle_external_request(service_name, endpoint_name, method="GET", user=None,
                            param_values=None, request_data=None, headers={}):
    """
    Generic function to handle an external request, logging it in APIRequestLog.
    This is a placeholder stripped of domain-specific logic.
    """
    if param_values is None:
        param_values = {}
    if request_data is None:
        request_data = {}

    service = get_object_or_404(Service, name=service_name)
    endpoint = get_object_or_404(Endpoint, service=service, name=endpoint_name, method=method)

    # Build URL
    url = service.base_url + endpoint.path
    # Possibly handle path_params or query_params here if needed
    query_params = param_values

    if service.auth_method and service.auth_method.lower() == "bearer":
        # For example, read a token from environment or cache
        token = cache.get(f"{service_name}_token", "FAKE-TOKEN")
        headers["Authorization"] = f"Bearer {token}"

    # Execute request
    try:
        if method == "GET":
            res = requests.get(url, params=query_params, headers=headers)
        elif method == "POST":
            res = requests.post(url, json=request_data, headers=headers, params=query_params)
        elif method == "PUT":
            res = requests.put(url, json=request_data, headers=headers, params=query_params)
        elif method == "DELETE":
            res = requests.delete(url, headers=headers, params=query_params)
        else:
            raise ValueError("Unsupported method")

        status_code = res.status_code
        try:
            response_data = res.json()
        except Exception:
            response_data = {"raw": res.text}

        # Log the request
        APIRequestLog.objects.create(
            user=user if user and user.is_authenticated else None,
            service=service,
            endpoint=endpoint,
            full_url=res.url,
            request_data=request_data,
            response_data=response_data,
            status_code=status_code
        )

        return res

    except requests.exceptions.RequestException as e:
        logger.error(f"External request error: {str(e)}")
        raise e


def get_coordinates(place_of_birth):
    """
    Get coordinates for a given place of birth using OpenStreetMap's Nominatim API.
    Returns a dictionary with latitude and longitude, or default coordinates if not found.
    """
    def fetch_coordinates(query):
        """Fetch coordinates from OpenStreetMap API."""
        try:
            response = handle_external_request(
                service_name='nominatim',
                endpoint_name='search',
                method='GET',
                param_values={
                    'q': query,
                    'format': 'jsonv2'
                },
                headers={
                    'User-Agent': 'MyGeolocationApp/1.0 (random@gmail.com)'
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        "latitude": float(data[0]["lat"]),
                        "longitude": float(data[0]["lon"])
                    }
            return None

        except Exception as e:
            logger.error(f"Error fetching coordinates for query '{query}': {str(e)}")
            return None

    # Return default coordinates if no place of birth
    if not place_of_birth:
        return {"latitude": 0, "longitude": 0}

    # First, try the full location
    result = fetch_coordinates(place_of_birth)
    if result:
        return result

    # Try with parts of the address
    parts = [part.strip() for part in place_of_birth.split(",")] if "," in place_of_birth else place_of_birth.split()

    # Try with the first part only
    if parts:
        return fetch_coordinates(parts[0]) or {"latitude": 0, "longitude": 0}

    return {"latitude": 0, "longitude": 0}



def get_structure_openai_response(ai_response):
    """
    Attempt to convert any type of string containing JSON-like content into
    a Python dictionary (JSON object). If all parsing attempts fail,
    return the original string for debugging.

    Parameters:
    -----------
    ai_response : str
        A string that (hopefully) contains JSON data.

    Returns:
    --------
    dict or list or str
        A Python object (dict or list) if parsing is successful, otherwise
        the original string.
    """

    # 1) Basic normalization: strip whitespace
    ai_response = ai_response.strip()

    # 2) Remove surrounding triple backticks if present
    #    e.g., ```json ... ```
    #    We'll do a broad strip of any ```...``` fence if found
    fence_pattern = re.compile(r"^```[a-zA-Z]*\s*([\s\S]+?)\s*```$")
    match = fence_pattern.match(ai_response)
    if match:
        ai_response = match.group(1).strip()

    # 3) Remove single or double quotes if they wrap the entire content
    #    e.g., '"{...}"' or "'{...}'"
    #    We'll only remove one pair of quotes if it exactly wraps
    if (ai_response.startswith("'") and ai_response.endswith("'")) or (
        ai_response.startswith('"') and ai_response.endswith('"')
    ):
        # Make sure there's more than just a pair of quotes
        if len(ai_response) > 1:
            ai_response = ai_response[1:-1].strip()

    # 4) Replace Python-specific boolean/null with JSON-compatible ones
    #    (True -> true, False -> false, None -> null)
    ai_response = ai_response.replace("None", "null")
    ai_response = ai_response.replace("True", "true")
    ai_response = ai_response.replace("False", "false")

    # 5) Attempt to fix some typical single-quote usage inside JSON keys/values:
    #    - If there's something like {'key': 'value'}, we'll try to turn that into {"key": "value"}
    #      BUT we must do it carefully. We'll do a quick heuristic:
    #      - Replace single quotes that look like they wrap keys or values with double quotes.
    #      - We do this only for sequences that look like `'some_text':` or `: 'some_text'`
    #    - This step is optional or can be extended for more advanced heuristics.
    #    - We'll also handle common contractions by escaping them, but be careful
    #      not to break valid JSON that already has double quotes.

    # First, a broad approach to single-quoted keys/values -> double-quoted:
    #   pattern: (["{,]\s*)'([^']*)'\s*([:,}\]])
    #   meaning: after a { or comma or "   followed by optional space,
    #            then a single-quoted section,
    #            then a colon/comma/brace/quote afterwards.
    # You can refine or remove this step if it is too broad.
    single_quote_key_value_pattern = re.compile(r"([{\[,]\s*)\'([^\'\r\n]+)\'\s*([},\]:])")
    # Replace iteratively until no more replacements can be made
    while True:
        new_response = single_quote_key_value_pattern.sub(r'\1"\2"\3', ai_response)
        if new_response == ai_response:
            break
        ai_response = new_response

    # 6) Now that keys/values are hopefully using double quotes, we still might
    #    have unescaped double quotes inside the string (like you"re).
    #    JSON requires those inner quotes to be escaped. We'll try a minimal approach:
    #    We'll look for sequences inside a double-quoted string where an unescaped
    #    double quote appears. We can attempt to backslash-escape it.
    #
    #    This is tricky to get 100% correct. We'll do a simplified approach that:
    #    - finds all double-quoted strings using a JSON-like pattern
    #    - escapes any raw double quotes inside those strings
    #      (i.e., an occurrence of `"` that isn't already `\"`).
    #
    #    If your data might contain complicated cases (like backslash sequences),
    #    a more robust state machine or an actual JSON parser with error hooks would be required.

    # A state machine approach is out of scope here, so let's do a simpler approach:
    #   1) Identify double-quoted strings: " ..."
    #   2) Inside them, replace any unescaped `"` with `\"`.
    #
    # We'll skip if there's a preceding backslash, i.e., `\"` is considered escaped.
    #
    # Regex approach: "((?:\\.|[^"\\])*)"
    # Captures any sequence inside double quotes, allowing for escaped characters.
    # Then we re-escape interior quotes in the captured group.

    def escape_inner_quotes(match):
        # The group(1) is the content inside the quotes
        inner = match.group(1)
        # Replace any quote that is not preceded by a backslash
        # with an escaped quote.
        # We can use a lookbehind to find quotes not preceded by backslash:
        # re.sub(r'(?<!\\)"', r'\"', inner)
        escaped_inner = re.sub(r'(?<!\\)"', r"\"", inner)
        return f'"{escaped_inner}"'

    double_quoted_string_pattern = re.compile(r'"((?:\\.|[^"\\])*)"')
    ai_response = double_quoted_string_pattern.sub(escape_inner_quotes, ai_response)

    # 7) Try a direct parse
    try:
        return json.loads(ai_response)
    except Exception:
        pass

    # 8) Fallback: try extracting the substring between the first '{' and the last '}'
    try:
        json_start = ai_response.index("{")
        json_end = ai_response.rfind("}")
        substring = ai_response[json_start : json_end + 1]
        return json.loads(substring)
    except Exception:
        pass

    # 9) If everything fails, return the raw string for debugging
    return ai_response

