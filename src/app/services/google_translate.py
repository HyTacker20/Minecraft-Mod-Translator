import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from ..utils.retry_logic import global_rate_limiter

logger = logging.getLogger("mod_translator")


def google_translate(
    text: str,
    source_lang: str,
    target_lang: str,
    capitalize: bool,
    google_retry: Callable,
) -> str:
    @google_retry
    def _do_google_translation(t: str) -> str:
        global_rate_limiter.apply_service_delay("google")
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source=source_lang, target=target_lang)
        result = translator.translate(t)
        if capitalize and result:
            result = result.capitalize()
        return result

    try:
        return _do_google_translation(text)
    except ImportError as e:
        logger.error("Error: %s", e)
        return text
    except Exception as e:
        logger.info('Google translation failed for "%s": %s', text, e)
        return text


def batch_translate_google(
    data: dict[str, str],
    translate_fn: Callable[[str], str],
    total_items: int = 0,
    max_workers: int = 4,
) -> dict[str, str]:
    if max_workers <= 1:
        return _batch_translate_sequential(data, translate_fn, total_items)
    return _batch_translate_concurrent(data, translate_fn, total_items, max_workers)


def _batch_translate_sequential(
    data: dict[str, str],
    translate_fn: Callable[[str], str],
    total_items: int = 0,
) -> dict[str, str]:
    translated_data: dict[str, str] = {}

    for index, (key, text) in enumerate(data.items(), 1):
        if not text or not isinstance(text, str):
            translated_data[key] = text
            continue

        try:
            translated_text = translate_fn(text)
            logger.info('🌐 [%d/%d] "%s" → "%s"', index, total_items, text, translated_text)
            translated_data[key] = translated_text

            if index < len(data):
                time.sleep(0.1)
        except Exception as e:
            logger.info('Error translating "%s": %s', text, e)
            translated_data[key] = text

    logger.info("Successfully translated %d entries using Google Translate", len(data))
    return translated_data


def _batch_translate_concurrent(
    data: dict[str, str],
    translate_fn: Callable[[str], str],
    total_items: int = 0,
    max_workers: int = 4,
) -> dict[str, str]:
    translated_data: dict[str, str] = {}
    items = [(k, v) for k, v in data.items() if v and isinstance(v, str)]
    empty_items = {k: v for k, v in data.items() if not v or not isinstance(v, str)}
    translated_data.update(empty_items)

    with ThreadPoolExecutor(max_workers=min(max_workers, len(items))) as executor:
        future_map = {executor.submit(translate_fn, text): key for key, text in items}
        completed = len(empty_items)

        for future in as_completed(future_map):
            key = future_map[future]
            try:
                translated_text = future.result()
                completed += 1
                logger.info('🌐 [%d/%d] translated entry', completed, total_items)
                translated_data[key] = translated_text
            except Exception as e:
                logger.info('Error translating entry: %s', e)
                original = dict(data)
                translated_data[key] = original[key]

    logger.info("Successfully translated %d entries using Google Translate", len(data))
    return translated_data
