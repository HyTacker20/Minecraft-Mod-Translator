import logging
import os

logger = logging.getLogger("mod_translator")


def check_openai_available() -> tuple[bool, str]:
    try:
        import openai
    except ImportError:
        return False, "Package not installed (pip install openai python-dotenv)"

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return True, "Available (API key configured)"
    else:
        return False, "API key not found (.env file or environment variable)"
