from loguru import logger

from deep_translator import GoogleTranslator

from .base_translator import BaseTranslatorService
from ..utils.retry_logic import create_retry_decorator, global_rate_limiter


class GoogleService(BaseTranslatorService):
    def __init__(self, source_lang: str, target_lang: str, capitalize: bool = True, max_retries: int = 3) -> None:
        super().__init__(source_lang, target_lang, capitalize)
        self._retry = create_retry_decorator("google", max_retries=max_retries)
        self._translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)

    def translate(self, text: str) -> str:
        if not text.strip():
            return text

        @self._retry
        def _do_translate(t: str) -> str:
            global_rate_limiter.apply_service_delay("google")
            result = self._translator.translate(t)
            if self.capitalize and result:
                result = result.capitalize()
            return result

        try:
            return _do_translate(text)
        except ImportError as e:
            logger.error("Error: %s", e)
            return text
        except Exception as e:
            logger.warning('Google translation failed for "%s": %s', text, e)
            return text
