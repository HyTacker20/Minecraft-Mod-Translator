import logging

from ..services.factory import get_translator_service

logger = logging.getLogger("mod_translator")


class Translator:
    def __init__(
        self,
        source_language: str,
        target_language: str,
        capitalize: bool = True,
        provider: str = "google",
        model: str | None = None,
    ) -> None:
        self.source_language = source_language
        self.target_language = target_language
        self.capitalize = capitalize
        self.provider = provider

        self._service = get_translator_service(
            provider=provider,
            source_lang=source_language,
            target_lang=target_language,
            capitalize=capitalize,
            model=model,
        )

    def translate(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return text
        return self._service.translate(text)

    def translate_data(self, data: dict[str, str], max_workers: int = 4) -> dict[str, str]:
        logger.info(
            "Translating %d entries from %s to %s using %s...",
            len(data),
            self.source_language,
            self.target_language,
            self.provider,
        )
        return self._service.batch_translate(data, len(data), max_workers)
