import logging
import os

logger = logging.getLogger("mod_translator")


def check_provider_available(provider: str) -> tuple[bool, str]:
    if provider == "google":
        try:
            from deep_translator import GoogleTranslator  # noqa: F401
            return True, "Always available"
        except ImportError:
            return False, "Package not installed (pip install deep-translator)"

    litellm_ok = False
    try:
        import litellm  # noqa: F401
        litellm_ok = True
    except ImportError:
        pass

    if not litellm_ok:
        return False, "LiteLLM package not installed (pip install litellm python-dotenv openai)"

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return True, "Available (OPENAI_API_KEY configured)"
        return False, "OPENAI_API_KEY not found (.env file or environment variable)"

    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            return True, "Available (ANTHROPIC_API_KEY configured)"
        return False, "ANTHROPIC_API_KEY not found (.env file or environment variable)"

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            return True, "Available (GEMINI_API_KEY configured)"
        return False, "GEMINI_API_KEY not found (.env file or environment variable)"

    if provider == "ollama":
        base_url = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        return True, f"Available (using {base_url})"

    if provider == "litellm":
        model = os.getenv("TRANSLATION_MODEL") or "gpt-4o-mini"
        return True, f"Available (model: {model})"

    return False, f"Unknown provider: {provider}"
