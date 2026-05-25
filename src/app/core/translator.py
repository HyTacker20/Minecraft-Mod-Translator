import logging

from ..utils.retry_logic import create_retry_decorator, global_rate_limiter
from ..services import google_translate, openai_translate

logger = logging.getLogger("mod_translator")


class Translator:
    def __init__(
        self,
        source_language: str,
        target_language: str,
        capitalize: bool = True,
        use_openai: bool = False,
    ) -> None:
        self.source_language = source_language
        self.target_language = target_language
        self.capitalize = capitalize
        self.use_openai = use_openai

        self.google_retry = create_retry_decorator("google", max_retries=3)
        self.openai_retry = create_retry_decorator("openai", max_retries=3)

        if self.use_openai:
            self._setup_openai()

    def _setup_openai(self) -> None:
        self.openai_client, self.model = openai_translate.setup_openai_client()

    def translate(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return text

        if self.use_openai:
            return openai_translate.openai_translate(
                text,
                self.source_language,
                self.target_language,
                self.capitalize,
                self.openai_client,
                self.model,
                self.openai_retry,
            )
        else:
            return google_translate.google_translate(
                text,
                self.source_language,
                self.target_language,
                self.capitalize,
                self.google_retry,
            )

    def translate_data(self, data: dict[str, str], max_workers: int = 4) -> dict[str, str]:
        translation_service = "OpenAI" if self.use_openai else "Google Translate"
        logger.info(
            "Translating %d entries from %s to %s using %s...",
            len(data),
            self.source_language,
            self.target_language,
            translation_service,
        )

        if self.use_openai:
            return openai_translate.batch_translate_openai(
                data, self.translate, len(data), max_workers
            )
        else:
            return google_translate.batch_translate_google(
                data, self.translate, len(data), max_workers
            )
