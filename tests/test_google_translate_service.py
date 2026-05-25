from app.services.google_service import GoogleService


def _mock_translate_fn(text: str) -> str:
    if text == "fail":
        raise RuntimeError("translation failed")
    return f"tr_{text}"


class TestGoogleService:
    def test_batch_translate_concurrent(self):
        service = GoogleService("en", "uk", capitalize=False)
        with _patch_translate(service, _mock_translate_fn):
            data = {f"key_{i}": f"text_{i}" for i in range(6)}
            result = service.batch_translate(data, total_items=6, max_workers=3)
            assert len(result) == 6
            for i in range(6):
                assert result[f"key_{i}"] == f"tr_text_{i}"

    def test_batch_translate_concurrent_with_errors(self):
        service = GoogleService("en", "uk", capitalize=False)
        with _patch_translate(service, _mock_translate_fn):
            data = {"a": "ok1", "b": "fail", "c": "ok2", "d": "ok3"}
            result = service.batch_translate(data, total_items=4, max_workers=3)
            assert len(result) == 4
            assert result["a"] == "tr_ok1"
            assert result["b"] == "fail"
            assert result["c"] == "tr_ok2"

    def test_batch_translate_max_workers_zero(self):
        service = GoogleService("en", "uk", capitalize=False)
        with _patch_translate(service, _mock_translate_fn):
            data = {"a": "hello", "b": "world"}
            result = service.batch_translate(data, total_items=2, max_workers=0)
            assert result["a"] == "tr_hello"
            assert result["b"] == "tr_world"

    def test_batch_translate_empty_data(self):
        service = GoogleService("en", "uk", capitalize=False)
        result = service.batch_translate({}, max_workers=1)
        assert result == {}

    def test_batch_translate_skip_empty_values(self):
        service = GoogleService("en", "uk", capitalize=False)
        with _patch_translate(service, _mock_translate_fn):
            data = {"a": "text", "b": "", "c": None}
            result = service.batch_translate(data, total_items=3, max_workers=1)
            assert result["a"] == "tr_text"
            assert result["b"] == ""
            assert result["c"] is None

    def test_batch_translate_sequential_error_fallback(self):
        service = GoogleService("en", "uk", capitalize=False)
        with _patch_translate(service, _mock_translate_fn):
            data = {"a": "fail", "b": "ok"}
            result = service.batch_translate(data, total_items=2, max_workers=1)
            assert result["a"] == "fail"
            assert result["b"] == "tr_ok"


def _patch_translate(service, fn):
    from unittest.mock import patch
    return patch.object(service, "translate", side_effect=fn)
