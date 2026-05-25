import json
import os
from typing import Any


def load_languages() -> list[dict[str, Any]]:
    path = os.path.join(os.path.dirname(__file__), "languages.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
