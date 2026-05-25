import json
import os

from loguru import logger

from .base_translator import BaseTranslatorService, make_chunk_system_prompt, make_system_prompt
from ..utils.retry_logic import create_retry_decorator, global_rate_limiter

DEFAULT_TRANSLATION_MODEL = "gpt-4o-mini"

PROVIDER_DEFAULTS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-haiku-20240307",
    "gemini": "gemini/gemini-1.5-flash",
    "ollama": "ollama/llama3",
}


class LitellmService(BaseTranslatorService):
    _CHUNK_SIZE = 25

    def __init__(
        self,
        source_lang: str,
        target_lang: str,
        capitalize: bool = True,
        max_retries: int = 3,
        model: str | None = None,
        provider: str = "litellm",
    ) -> None:
        super().__init__(source_lang, target_lang, capitalize)
        self._retry = create_retry_decorator("litellm", max_retries=max_retries)
        self._provider = provider

        try:
            from dotenv import load_dotenv
            load_dotenv()
            load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
        except ImportError:
            pass

        from litellm import completion
        self._completion = completion

        resolved = model or os.getenv("TRANSLATION_MODEL") or PROVIDER_DEFAULTS.get(provider, DEFAULT_TRANSLATION_MODEL)
        self._model = resolved
        logger.info("LiteLLM initialized with model: %s", self._model)

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
            global_rate_limiter.apply_service_delay("litellm")

            system_prompt = make_chunk_system_prompt(self.source_lang, self.target_lang)

            response = self._completion(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": payload},
                ],
                temperature=0.3,
                max_tokens=4096,
            )

            return completion.choices[0].message.content

        try:
            response = _do_translate(json.dumps(items, ensure_ascii=False))
            result = self._parse_chunk_response(response, chunk)

            for key in items:
                if key not in result:
                    result[key] = items[key]

            return result
        except Exception as e:
            logger.warning("LiteLLM chunk translation failed: %s", e)
            return {key: text for key, text in chunk}

    def translate(self, text: str) -> str:
        if not text.strip():
            return text

        @self._retry
        def _do_translate(t: str) -> str:
            global_rate_limiter.apply_service_delay("litellm")

            system_prompt = make_system_prompt(self.source_lang, self.target_lang)

            response = self._completion(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Translate: {t}"},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            translated_text = response.choices[0].message.content.strip()

            if self.capitalize and translated_text:
                translated_text = translated_text.capitalize()

            return translated_text

        try:
            return _do_translate(text)
        except Exception as e:
            logger.warning("LiteLLM translation failed for '%s': %s", text, e)
            return text
