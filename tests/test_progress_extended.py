from app.utils.progress import ProgressReporter


class TestProgressExtended:
    def test_report_complete(self):
        events = []
        reporter = ProgressReporter()
        reporter.subscribe(lambda event, **kwargs: events.append((event, kwargs)))
        reporter.report_complete("/output/path")
        assert len(events) == 1
        assert events[0][0] == "complete"
        assert events[0][1]["output_path"] == "/output/path"

    def test_report_error(self):
        events = []
        reporter = ProgressReporter()
        reporter.subscribe(lambda event, **kwargs: events.append((event, kwargs)))
        reporter.report_error("Something went wrong")
        assert len(events) == 1
        assert events[0][0] == "error"
        assert events[0][1]["text"] == "Something went wrong"
