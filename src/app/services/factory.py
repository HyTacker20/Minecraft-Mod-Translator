from loguru import logger

from .base_translator import BaseTranslatorService
from .google_service import GoogleService
from .litellm_service import LitellmService
from .openai_compatible_service import OpenAICompatibleService
from .openai_service import OpenAIService

AI_PROVIDERS = frozenset({"openai", "anthropic", "gemini", "ollama", "litellm", "openaicompatible"})
ALL_PROVIDERS = frozenset({"google", "openai", "anthropic", "gemini", "ollama", "litellm", "openaicompatible"})


def get_translator_service(
    provider: str,
    source_lang: str,
    target_lang: str,
    capitalize: bool = True,
    max_retries: int = 3,
    model: str | None = None,
) -> BaseTranslatorService:
    provider_lower = provider.lower()

    if provider_lower == "google":
        return GoogleService(
            source_lang=source_lang,
            target_lang=target_lang,
            capitalize=capitalize,
            max_retries=max_retries,
        )

    if provider_lower == "openai":
        try:
            return OpenAIService(
                source_lang=source_lang,
                target_lang=target_lang,
                capitalize=capitalize,
                max_retries=max_retries,
                model=model,
            )
        except (ImportError, ValueError):
            logger.info("OpenAI direct client unavailable, falling back to LiteLLM for openai")
            return LitellmService(
                source_lang=source_lang,
                target_lang=target_lang,
                capitalize=capitalize,
                max_retries=max_retries,
                model=model,
                provider="openai",
            )

    if provider_lower == "openaicompatible":
        return OpenAICompatibleService(
            source_lang=source_lang,
            target_lang=target_lang,
            capitalize=capitalize,
            max_retries=max_retries,
            model=model,
        )

    if provider_lower in AI_PROVIDERS:
        return LitellmService(
            source_lang=source_lang,
            target_lang=target_lang,
            capitalize=capitalize,
            max_retries=max_retries,
            model=model,
            provider=provider_lower,
        )

    raise ValueError(f"Unsupported translation provider: {provider}. Supported: {', '.join(sorted(ALL_PROVIDERS))}")
