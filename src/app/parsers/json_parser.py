import json
import re
from typing import Any

from ..exceptions import FileParsingError


def remove_comments_from_json(json_str: str) -> str:
    result = re.sub(r"//.*$", "", json_str, flags=re.MULTILINE)
    result = re.sub(r"/\*.*?\*/", "", result, flags=re.DOTALL)
    return result


def parse_json_with_comments(file_path: str) -> dict[str, Any]:
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        clean_content = remove_comments_from_json(content)
        return json.loads(clean_content)
    except json.JSONDecodeError as e:
        raise FileParsingError(f"Invalid JSON in {file_path}: {e}") from e
    except OSError as e:
        raise FileParsingError(f"Cannot read {file_path}: {e}") from e
