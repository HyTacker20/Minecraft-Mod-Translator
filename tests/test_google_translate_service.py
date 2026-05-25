from unittest.mock import MagicMock, patch

from app.services.google_translate import batch_translate_google, _batch_translate_sequential, _batch_translate_concurrent


def _mock_translate_fn(text: str) -> str:
    if text == "fail":
        raise RuntimeError("translation failed")
    return f"tr_{text}"


class TestGoogleTranslateService:
    def test_batch_translate_concurrent(self):
        data = {f"key_{i}": f"text_{i}" for i in range(6)}
        result = batch_translate_google(data, _mock_translate_fn, total_items=6, max_workers=3)
        assert len(result) == 6
        for i in range(6):
            assert result[f"key_{i}"] == f"tr_text_{i}"

    def test_batch_translate_concurrent_with_errors(self):
        data = {"a": "ok1", "b": "fail", "c": "ok2", "d": "ok3"}
        result = batch_translate_google(data, _mock_translate_fn, total_items=4, max_workers=3)
        assert len(result) == 4
        assert result["a"] == "tr_ok1"
        assert result["b"] == "fail"
        assert result["c"] == "tr_ok2"

    def test_batch_translate_max_workers_zero(self):
        data = {"a": "hello", "b": "world"}
        result = batch_translate_google(data, _mock_translate_fn, total_items=2, max_workers=0)
        assert result["a"] == "tr_hello"
        assert result["b"] == "tr_world"

    def test_batch_translate_empty_data(self):
        result = batch_translate_google({}, _mock_translate_fn, max_workers=1)
        assert result == {}

    def test_batch_translate_skip_empty_values(self):
        data = {"a": "text", "b": "", "c": None}
        result = batch_translate_google(data, _mock_translate_fn, total_items=3, max_workers=1)
        assert result["a"] == "tr_text"
        assert result["b"] == ""
        assert result["c"] is None

    def test_batch_translate_sequential_error_fallback(self):
        data = {"a": "fail", "b": "ok"}
        result = batch_translate_google(data, _mock_translate_fn, total_items=2, max_workers=1)
        assert result["a"] == "fail"
        assert result["b"] == "tr_ok"
