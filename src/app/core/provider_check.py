import os


def check_provider_available(provider: str) -> tuple[bool, str]:
    if provider == "google":
        try:
            from deep_translator import GoogleTranslator  # noqa: F401
            return True, "Always available"
        except ImportError:
            return False, "Package not installed (pip install deep-translator)"

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    if provider == "openaicompatible":
        try:
            import openai  # noqa: F401
        except ImportError:
            return False, "OpenAI package not installed (pip install openai python-dotenv)"
        api_key = os.getenv("OPENAICOMPATIBLE_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAICOMPATIBLE_BASE_URL")
        if not api_key:
            return False, "OPENAICOMPATIBLE_API_KEY not found (.env file or environment variable)"
        if not base_url:
            return False, "OPENAICOMPATIBLE_BASE_URL not found (.env file or environment variable)"
        model = os.getenv("OPENAICOMPATIBLE_MODEL") or "gpt-4o-mini"
        return True, f"Available (base_url={base_url}, model={model})"

    if provider == "openai":
        openai_ok = False
        try:
            import openai  # noqa: F401
            openai_ok = True
        except ImportError:
            pass
        litellm_ok = False
        try:
            import litellm  # noqa: F401
            litellm_ok = True
        except ImportError:
            pass
        if not openai_ok and not litellm_ok:
            return False, "OpenAI or LiteLLM package not installed (pip install openai litellm python-dotenv)"
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return True, "Available (OPENAI_API_KEY configured)"
        return False, "OPENAI_API_KEY not found (.env file or environment variable)"

    litellm_ok = False
    try:
        import litellm  # noqa: F401
        litellm_ok = True
    except ImportError:
        pass

    if not litellm_ok:
        return False, "LiteLLM package not installed (pip install litellm python-dotenv)"

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

    return False, f"Unknown provider: {provider}"
