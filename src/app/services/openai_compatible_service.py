import json
import os

from loguru import logger

from .base_translator import BaseTranslatorService, make_chunk_system_prompt, make_system_prompt
from ..utils.retry_logic import create_retry_decorator, global_rate_limiter

DEFAULT_MODEL = "gpt-4o-mini"


class OpenAICompatibleService(BaseTranslatorService):
    _CHUNK_SIZE = 10

    def __init__(
        self,
        source_lang: str,
        target_lang: str,
        capitalize: bool = True,
        max_retries: int = 3,
        model: str | None = None,
    ) -> None:
        super().__init__(source_lang, target_lang, capitalize)
        self._retry = create_retry_decorator("openaicompatible", max_retries=max_retries)

        try:
            from dotenv import load_dotenv
            load_dotenv()
            load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
        except ImportError:
            pass

        self._api_key = os.getenv("OPENAICOMPATIBLE_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "OPENAICOMPATIBLE_API_KEY environment variable not set.\n"
                "Please set OPENAICOMPATIBLE_API_KEY in a .env file or environment variable."
            )

        self._base_url = os.getenv("OPENAICOMPATIBLE_BASE_URL")
        if not self._base_url:
            raise ValueError(
                "OPENAICOMPATIBLE_BASE_URL environment variable not set.\n"
                "Please set OPENAICOMPATIBLE_BASE_URL in a .env file or environment variable."
            )

        from openai import OpenAI
        self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        self._model = model or os.getenv("OPENAICOMPATIBLE_MODEL") or os.getenv("TRANSLATION_MODEL") or DEFAULT_MODEL
        logger.info("OpenAICompatibleService initialized with model: %s, base_url: %s", self._model, self._base_url)

    def _translate_chunk(self, chunk: list[tuple[str, str]]) -> dict[str, str]:
        if not chunk:
            return {}

        if len(chunk) == 1:
            key, text = chunk[0]
            try:
                return {key: self.translate(text)}
            except Exception:
                return {key: text}

        items = {key: text for key, text in chunk}

        @self._retry
        def _do_translate(payload: str) -> str:
            global_rate_limiter.apply_service_delay("openaicompatible")

            system_prompt = make_chunk_system_prompt(self.source_lang, self.target_lang)

            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": payload},
                ],
                temperature=0.3,
                max_tokens=4096,
            )

            content = completion.choices[0].message.content
            finish_reason = getattr(completion.choices[0], "finish_reason", "unknown")
            usage = getattr(completion, "usage", None)
            logger.debug(
                "Completion metadata: model=%s, finish_reason=%s, content_len=%s, usage=%s",
                self._model,
                finish_reason,
                len(content) if content else 0,
                usage,
            )
            return content

        try:
            response = _do_translate(json.dumps(items, ensure_ascii=False))
            result = self._parse_chunk_response(response, chunk)

            for key in items:
                if key not in result:
                    result[key] = items[key]

            return result
        except Exception as e:
            logger.warning("OpenAICompatibleService chunk translation failed: %s", e)
            return {key: text for key, text in chunk}

    def translate(self, text: str) -> str:
        if not text.strip():
            return text

        @self._retry
        def _do_translate(t: str) -> str:
            global_rate_limiter.apply_service_delay("openaicompatible")

            system_prompt = make_system_prompt(self.source_lang, self.target_lang)

            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Translate: {t}"},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            translated_text = completion.choices[0].message.content.strip()

            if self.capitalize and translated_text:
                translated_text = translated_text.capitalize()

            return translated_text

        try:
            return _do_translate(text)
        except Exception as e:
            logger.warning("OpenAICompatibleService translation failed for '%s': %s", text, e)
            return text
