import json
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger("mod_translator")

TRANSLATION_SYSTEM_PROMPT = """You are a professional translator specializing in video game localization.
Translate from {source_lang} to {target_lang}.

Guidelines:
- Preserve formatting like %s, %d, {{}} placeholders
- Maintain gaming-appropriate tone
- Use natural, idiomatic expressions
- Keep technical terms consistent

Respond with ONLY the translated text, no explanations."""

CHUNK_TRANSLATION_SYSTEM_PROMPT = """You are a professional translator specializing in video game localization.
Translate from {source_lang} to {target_lang}.

Guidelines:
- Preserve formatting like %s, %d, {{}} placeholders
- Maintain gaming-appropriate tone
- Use natural, idiomatic expressions
- Keep technical terms consistent

You will receive a JSON object where each key maps to a source text.
Respond with ONLY a JSON object with the same keys mapped to their translations.
Do not include any explanation, markdown fences, or extra text."""


def make_system_prompt(source_lang: str, target_lang: str) -> str:
    return TRANSLATION_SYSTEM_PROMPT.format(source_lang=source_lang, target_lang=target_lang)


def make_chunk_system_prompt(source_lang: str, target_lang: str) -> str:
    return CHUNK_TRANSLATION_SYSTEM_PROMPT.format(source_lang=source_lang, target_lang=target_lang)


class BaseTranslatorService(ABC):
    _CHUNK_SIZE: int = 0

    def __init__(self, source_lang: str, target_lang: str, capitalize: bool = True) -> None:
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.capitalize = capitalize

    @abstractmethod
    def translate(self, text: str) -> str:
        pass

    def _translate_chunk(self, chunk: list[tuple[str, str]]) -> dict[str, str]:
        result: dict[str, str] = {}
        for key, text in chunk:
            try:
                result[key] = self.translate(text)
            except Exception:
                result[key] = text
        return result

    def _parse_chunk_response(self, response: str, chunk: list[tuple[str, str]]) -> dict[str, str]:
        response = response.strip()
        logger.debug(
            "_parse_chunk_response: raw response (len=%d, keys=%d): %s",
            len(response),
            len(chunk),
            response[:1500],
        )

        # Remove markdown code fences (including language tags like ```json)
        if response.startswith("```"):
            lines = response.split("\n")
            if lines and lines[0].startswith("```"):
                lines = lines[1:]  # Strip opening fence line
            if lines and lines[-1].strip() in ("```", "``` "):
                lines = lines[:-1]  # Strip closing fence line
            response = "\n".join(lines).strip()

        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict):
                parsed_dict = dict(parsed)
                if self.capitalize:
                    return {k: v.capitalize() if isinstance(v, str) and v else v for k, v in parsed_dict.items()}
                return parsed_dict
        except json.JSONDecodeError as e:
            logger.warning(
                "Failed to parse chunk response as JSON (error: %s, response head: %s), falling back to per-item",
                e,
                response[:300],
            )
            result: dict[str, str] = {}
            for key, text in chunk:
                try:
                    result[key] = self.translate(text)
                except Exception:
                    result[key] = text
            return result

        return {}

    def batch_translate(
        self,
        data: dict[str, str],
        total_items: int = 0,
        max_workers: int = 4,
    ) -> dict[str, str]:
        if max_workers <= 1:
            return self._batch_translate_seq(data, total_items)
        return self._batch_translate_parallel(data, total_items, max_workers)

    def _batch_translate_chunked(
        self,
        data: dict[str, str],
        total_items: int,
        max_workers: int,
    ) -> dict[str, str]:
        translated_data: dict[str, str] = {}
        items = [(k, v) for k, v in data.items() if v and isinstance(v, str)]
        empty_items = {k: v for k, v in data.items() if not v or not isinstance(v, str)}
        translated_data.update(empty_items)

        chunk_size = self._CHUNK_SIZE
        chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

        executor = ThreadPoolExecutor(max_workers=min(max_workers, max(1, len(chunks))))
        try:
            future_map = {executor.submit(self._translate_chunk, chunk): idx for idx, chunk in enumerate(chunks)}

            for future in as_completed(future_map):
                try:
                    chunk_result = future.result()
                    translated_data.update(chunk_result)
                except Exception as e:
                    logger.warning("Error translating chunk: %s", e)
        except KeyboardInterrupt:
            logger.info("Translation interrupted by user — cancelling remaining tasks...")
            raise
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        logger.info("Successfully translated %d entries", len(data))
        return translated_data

    def _batch_translate_seq(
        self,
        data: dict[str, str],
        total_items: int = 0,
    ) -> dict[str, str]:
        if self._CHUNK_SIZE > 0:
            return self._batch_translate_chunked(data, total_items, max_workers=1)

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
                logger.warning('Error translating "%s": %s', text, e)
                translated_data[key] = text

        logger.info("Successfully translated %d entries", len(data))
        return translated_data

    def _batch_translate_parallel(
        self,
        data: dict[str, str],
        total_items: int = 0,
        max_workers: int = 4,
    ) -> dict[str, str]:
        if self._CHUNK_SIZE > 0:
            return self._batch_translate_chunked(data, total_items, max_workers)

        translated_data: dict[str, str] = {}
        items = [(k, v) for k, v in data.items() if v and isinstance(v, str)]
        empty_items = {k: v for k, v in data.items() if not v or not isinstance(v, str)}
        translated_data.update(empty_items)

        executor = ThreadPoolExecutor(max_workers=min(max_workers, max(1, len(items))))
        try:
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
                    logger.warning("Error translating entry: %s", e)
                    translated_data[key] = data[key]
        except KeyboardInterrupt:
            logger.info("Translation interrupted by user — cancelling remaining tasks...")
            raise
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        logger.info("Successfully translated %d entries", len(data))
        return translated_data
