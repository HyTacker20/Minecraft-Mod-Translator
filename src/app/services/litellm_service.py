import logging
import os

from ..utils.retry_logic import create_retry_decorator, global_rate_limiter
from .base_translator import BaseTranslatorService

logger = logging.getLogger("mod_translator")

DEFAULT_TRANSLATION_MODEL = "gpt-4o-mini"

PROVIDER_DEFAULTS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-haiku-20240307",
    "gemini": "gemini/gemini-1.5-flash",
    "ollama": "ollama/llama3",
}


class LitellmService(BaseTranslatorService):
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

    def translate(self, text: str) -> str:
        if not text.strip():
            return text

        @self._retry
        def _do_translate(t: str) -> str:
            global_rate_limiter.apply_service_delay("litellm")

            system_prompt = f"""You are a professional translator specializing in video game localization.
Translate from {self.source_lang} to {self.target_lang}.

Guidelines:
- Preserve formatting like %s, %d, {{}} placeholders
- Maintain gaming-appropriate tone
- Use natural, idiomatic expressions
- Keep technical terms consistent

Respond with ONLY the translated text, no explanations."""

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
            logger.info("LiteLLM translation failed for '%s': %s", text, e)
            return text
