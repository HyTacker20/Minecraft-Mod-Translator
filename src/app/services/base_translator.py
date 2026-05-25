import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger("mod_translator")


class BaseTranslatorService(ABC):
    def __init__(self, source_lang: str, target_lang: str, capitalize: bool = True) -> None:
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.capitalize = capitalize

    @abstractmethod
    def translate(self, text: str) -> str:
        pass

    def batch_translate(
        self,
        data: dict[str, str],
        total_items: int = 0,
        max_workers: int = 4,
    ) -> dict[str, str]:
        if max_workers <= 1:
            return self._batch_translate_seq(data, total_items)
        return self._batch_translate_parallel(data, total_items, max_workers)

    def _batch_translate_seq(
        self,
        data: dict[str, str],
        total_items: int = 0,
    ) -> dict[str, str]:
        translated_data: dict[str, str] = {}

        items = [(k, v) for k, v in data.items()]
        for index, (key, text) in enumerate(items, 1):
            if not text or not isinstance(text, str):
                translated_data[key] = text
                continue

            try:
                translated_text = self.translate(text)
                logger.info('[%d/%d] "%s" -> "%s"', index, total_items, text, translated_text)
                translated_data[key] = translated_text

                if index < len(data):
                    time.sleep(0.1)
            except Exception as e:
                logger.info('Error translating "%s": %s', text, e)
                translated_data[key] = text

        logger.info("Successfully translated %d entries", len(data))
        return translated_data

    def _batch_translate_parallel(
        self,
        data: dict[str, str],
        total_items: int = 0,
        max_workers: int = 4,
    ) -> dict[str, str]:
        translated_data: dict[str, str] = {}
        items = [(k, v) for k, v in data.items() if v and isinstance(v, str)]
        empty_items = {k: v for k, v in data.items() if not v or not isinstance(v, str)}
        translated_data.update(empty_items)

        with ThreadPoolExecutor(max_workers=min(max_workers, max(1, len(items)))) as executor:
            future_map = {executor.submit(self.translate, text): key for key, text in items}
            completed = len(empty_items)

            for future in as_completed(future_map):
                key = future_map[future]
                try:
                    translated_text = future.result()
                    completed += 1
                    logger.info("[%d/%d] translated entry", completed, total_items)
                    translated_data[key] = translated_text
                except Exception as e:
                    logger.info("Error translating entry: %s", e)
                    original = dict(data)
                    translated_data[key] = original[key]

        logger.info("Successfully translated %d entries", len(data))
        return translated_data
