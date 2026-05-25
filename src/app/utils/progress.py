from typing import Callable, Any


class ProgressReporter:
    def __init__(self) -> None:
        self._callbacks: list[Callable[..., None]] = []

    def subscribe(self, callback: Callable[..., None]) -> None:
        self._callbacks.append(callback)

    def _notify(self, event: str, **kwargs: Any) -> None:
        for cb in self._callbacks:
            cb(event, **kwargs)

    def report_title(self, title: str) -> None:
        self._notify("title", text=title)

    def report_message(self, message: str) -> None:
        self._notify("message", text=message)

    def report_progress(self, current: int, total: int, item: str = "") -> None:
        self._notify("progress", current=current, total=total, item=item)

    def report_complete(self, output_path: str) -> None:
        self._notify("complete", output_path=output_path)

    def report_error(self, error: str) -> None:
        self._notify("error", text=error)
