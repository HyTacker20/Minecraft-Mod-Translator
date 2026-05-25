import os
import time
import logging
from typing import Callable

from ..utils.retry_logic import global_rate_limiter

logger = logging.getLogger("mod_translator")


def setup_openai_client():
    try:
        from openai import OpenAI

        try:
            from dotenv import load_dotenv

            load_dotenv()
            load_dotenv(
                dotenv_path=os.path.join(
                    os.path.dirname(__file__), "..", "..", "..", ".env"
                )
            )
            logger.info("Loaded .env configuration")
        except ImportError:
            logger.info("python-dotenv not found, using system environment variables")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set.\n"
                "Please:\n"
                "1. Set OPENAI_API_KEY environment variable, or\n"
                "2. Create a .env file with: OPENAI_API_KEY=your_key_here"
            )

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        logger.info("OpenAI initialized with model: %s", model)
        return client, model

    except ImportError as e:
        raise ImportError(
            "OpenAI package not found. Install with: pip install openai python-dotenv"
        ) from e


def openai_translate(
    text: str,
    source_lang: str,
    target_lang: str,
    capitalize: bool,
    client,
    model: str,
    openai_retry: Callable,
) -> str:
    if not text.strip():
        return text

    @openai_retry
    def _do_openai_translation(t: str) -> str:
        global_rate_limiter.apply_service_delay("openai")

        system_prompt = f"""You are a professional translator specializing in video game localization.
        Translate from {source_lang} to {target_lang}.

        Guidelines:
        - Preserve formatting like %s, %d, {{}} placeholders
        - Maintain gaming-appropriate tone
        - Use natural, idiomatic expressions
        - Keep technical terms consistent

        Respond with ONLY the translated text, no explanations."""

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate: {t}"},
            ],
            temperature=0.3,
            max_tokens=500,
        )

        translated_text = completion.choices[0].message.content.strip()

        if capitalize and translated_text:
            translated_text = translated_text.capitalize()

        return translated_text

    try:
        return _do_openai_translation(text)
    except Exception as e:
        logger.info("OpenAI translation failed for '%s': %s", text, e)
        return text


def batch_translate_openai(
    data: dict[str, str],
    translate_fn: Callable[[str], str],
    total_items: int = 0,
    max_workers: int = 4,
) -> dict[str, str]:
    if max_workers <= 1:
        return _batch_translate_openai_seq(data, translate_fn, total_items)
    return _batch_translate_openai_parallel(data, translate_fn, total_items, max_workers)


def _batch_translate_openai_seq(
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
            logger.info('🤖 [%d/%d] "%s" → "%s"', index, total_items, text, translated_text)
            translated_data[key] = translated_text

            if index < len(data):
                time.sleep(0.1)
        except Exception as e:
            logger.info('Error translating "%s": %s', text, e)
            translated_data[key] = text

    logger.info("Successfully translated %d entries using OpenAI", len(data))
    return translated_data


def _batch_translate_openai_parallel(
    data: dict[str, str],
    translate_fn: Callable[[str], str],
    total_items: int = 0,
    max_workers: int = 4,
) -> dict[str, str]:
    import concurrent.futures

    translated_data: dict[str, str] = {}
    items = [(k, v) for k, v in data.items() if v and isinstance(v, str)]
    empty_items = {k: v for k, v in data.items() if not v or not isinstance(v, str)}
    translated_data.update(empty_items)

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers, max(1, len(items)))) as executor:
        future_map = {executor.submit(translate_fn, text): key for key, text in items}
        completed = len(empty_items)

        for future in concurrent.futures.as_completed(future_map):
            key = future_map[future]
            try:
                translated_text = future.result()
                completed += 1
                logger.info('🤖 [%d/%d] translated entry', completed, total_items)
                translated_data[key] = translated_text
            except Exception as e:
                logger.info('Error translating entry: %s', e)
                original = dict(data)
                translated_data[key] = original[key]

    logger.info("Successfully translated %d entries using OpenAI", len(data))
    return translated_data
