from app.__version__ import __version__, VERSION


class TestVersion:
    def test_version_string(self):
        assert isinstance(__version__, str)
        parts = __version__.split(".")
        assert len(parts) == 3
        for p in parts:
            assert p.isdigit()

    def test_version_tuple(self):
        assert isinstance(VERSION, tuple)
        assert len(VERSION) == 3
        expected = ".".join(map(str, VERSION))
        assert __version__ == expected
