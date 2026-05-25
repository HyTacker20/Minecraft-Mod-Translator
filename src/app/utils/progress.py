from collections.abc import Callable
from typing import Any


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

    def report_error(self, error: str) -> None:
        self._notify("error", text=error)

    def report_complete(self, output_path: str) -> None:
        self._notify("complete", output_path=output_path)

    def report_scan_start(self, total: int) -> None:
        self._notify("scan_start", total=total)

    def report_scan_progress(self, current: int, total: int, name: str) -> None:
        self._notify("scan_progress", current=current, total=total, name=name)

    def report_scan_complete(self, total: int) -> None:
        self._notify("scan_complete", total=total)

    def report_mod_start(self, mod_name: str, file_count: int, entry_count: int) -> None:
        self._notify("mod_start", mod_name=mod_name, file_count=file_count, entry_count=entry_count)

    def report_mod_file_start(self, mod_name: str, file_path: str, entry_count: int) -> None:
        self._notify("mod_file_start", mod_name=mod_name, file_path=file_path, entry_count=entry_count)

    def report_mod_file_progress(self, mod_name: str, file_path: str, current: int, total: int) -> None:
        self._notify("mod_file_progress", mod_name=mod_name, file_path=file_path, current=current, total=total)

    def report_mod_file_complete(
        self, mod_name: str, file_path: str, duration_ms: int, errors: int
    ) -> None:
        self._notify(
            "mod_file_complete",
            mod_name=mod_name, file_path=file_path, duration_ms=duration_ms, errors=errors,
        )

    def report_mod_complete(self, mod_name: str, translated: int, total: int, failed: int) -> None:
        self._notify("mod_complete", mod_name=mod_name, translated=translated, total=total, failed=failed)

    def report_overall_progress(
        self, completed_mods: int, total_mods: int, completed_entries: int, total_entries: int
    ) -> None:
        self._notify(
            "overall_progress",
            completed_mods=completed_mods,
            total_mods=total_mods,
            completed_entries=completed_entries,
            total_entries=total_entries,
        )

    def report_repack_start(self, total: int) -> None:
        self._notify("repack_start", total=total)

    def report_repack_progress(self, current: int, total: int, name: str) -> None:
        self._notify("repack_progress", current=current, total=total, name=name)

    def report_repack_complete(self, total: int) -> None:
        self._notify("repack_complete", total=total)

    def report_progress(self, current: int, total: int, item: str = "") -> None:
        self._notify("progress", current=current, total=total, item=item)
