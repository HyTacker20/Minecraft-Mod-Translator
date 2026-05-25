import json
import pytest
from pathlib import Path

from app.parsers.json_parser import parse_json_with_comments
from app.exceptions import FileParsingError


class TestJsonParserEdge:
    def test_parse_json_invalid_syntax(self, tmp_path: Path):
        path = tmp_path / "broken.json"
        path.write_text('{"key": "value", broken}', encoding="utf-8")
        with pytest.raises(FileParsingError):
            parse_json_with_comments(str(path))
