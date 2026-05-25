import logging
import os

from ..utils.retry_logic import create_retry_decorator, global_rate_limiter
from .base_translator import BaseTranslatorService

logger = logging.getLogger("mod_translator")


class OpenAIService(BaseTranslatorService):
    def __init__(
        self,
        source_lang: str,
        target_lang: str,
        capitalize: bool = True,
        max_retries: int = 3,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        super().__init__(source_lang, target_lang, capitalize)
        self._retry = create_retry_decorator("openai", max_retries=max_retries)

        try:
            from dotenv import load_dotenv
            load_dotenv()
            load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
        except ImportError:
            pass

        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set.\n"
                "Please:\n"
                "1. Set OPENAI_API_KEY environment variable, or\n"
                "2. Create a .env file with: OPENAI_API_KEY=your_key_here"
            )

        from openai import OpenAI
        self._client = OpenAI(api_key=self._api_key)
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        logger.info("OpenAI initialized with model: %s", self._model)

    def translate(self, text: str) -> str:
        if not text.strip():
            return text

        @self._retry
        def _do_translate(t: str) -> str:
            global_rate_limiter.apply_service_delay("openai")

            system_prompt = f"""You are a professional translator specializing in video game localization.
Translate from {self.source_lang} to {self.target_lang}.

Guidelines:
- Preserve formatting like %s, %d, {{}} placeholders
- Maintain gaming-appropriate tone
- Use natural, idiomatic expressions
- Keep technical terms consistent

Respond with ONLY the translated text, no explanations."""

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
            logger.info("OpenAI translation failed for '%s': %s", text, e)
            return text
