# AGENTS.md

AI agent reference for the Minecraft Mod Translator project.

## Project overview

A Python tool that translates Minecraft mod files between languages. It unpacks JAR files, finds language files (JSON/LANG/MCFUNCTION), translates their contents via Google Translate or AI providers (OpenAI, Anthropic, Gemini, Ollama, OpenAI-compatible), and repacks them into translated JARs.

Two interfaces: interactive TUI (`mod-translator app`) and CLI (`mod-translator cli`).

## Architecture

```
src/app/
  __init__.py          Package init
  __main__.py          python -m app entry point
  __version__.py       VERSION = (1, 0, 0)
  exceptions.py        Custom exception hierarchy
  logging_config.py    Rotating file + console logger setup

  core/
    settings.py        Settings dataclass — CLI args → internal config
    translator.py      Thin wrapper over service, owns source/target lang
    file_manager.py    JAR unpack/repack, file discovery, orchestration
    provider_check.py  Checks if a provider is available (API keys, packages)

  services/
    base_translator.py       ABC with batch/parallel/chunked translate
    factory.py               Provider registry → instantiation + fallback
    google_service.py        Google Translate via deep-translator
    openai_service.py        OpenAI direct client
    litellm_service.py       Unified AI backend (LiteLLM)
    openai_compatible_service.py  Custom OpenAI-compatible APIs

  parsers/
    json_parser.py      JSON with comments (// and /* */)
    lang_parser.py      Minecraft LANG format (key=value per line)
    mcfunction_parser.py Extracts translatable strings from mcfunction files

  commands/
    command_line.py     CLI entry point, subparsers (cli / app)
    translate.py        Translation orchestrator, dependency checks
    app.py              Interactive TUI (questionary + rich)

  utils/
    retry_logic.py      Exponential backoff, RateLimitTracker, decorator
    progress.py         ProgressReporter — pub/sub events for UI updates

  data/
    __init__.py         Loads languages.json
```

## Translation flow

```
User input (CLI args or TUI form)
  → Settings object (lang code formatting, provider resolution)
  → FileManager initialized with Settings + Translator
  → create_needed_folders()   — temp/ and translated_mods/
  → unpack_mods()             — JAR → temp/{mod_name}/
  → get_lang_folders()        — find folders with source lang files
  → edit_lang_files()         — parse source → translate → write target
  → convert_translated_mods() — temp/ → translated_mods/{mod_name}.jar
  → remove_folder(temp_path)  — cleanup
```

## Key modules

### `core/settings.py`

`Settings` holds all runtime configuration. Constructor accepts `argparse.Namespace` and maps CLI fields to internal properties:

| Property | CLI flag | Default |
|---|---|---|
| `source_mc_lang` | `--source -s` | `en_US` |
| `target_mc_lang` | `--target -t` | `es_ES` |
| `mods_path` | `--path -p` | `./mods` |
| `translation_path` | `--output -o` | `./translated_mods` |
| `provider` | `--provider` / `--ai` | `google` |
| `max_workers` | `--workers` | `4` |
| `dry_run` | `--dry-run` | `False` |

`--ai` is deprecated and sets `provider = "openai"`.
Language codes are formatted: `en_US` → `en_US` (lowercase lang, uppercase region).

### `core/translator.py`

Thin wrapper. Holds `source_language`, `target_language`, `provider`, and delegates translation to a service obtained via `factory.get_translator_service()`. Two public methods: `translate(text: str)` for single strings, `translate_data(data: dict)` for batched translation (with `max_workers`).

### `core/file_manager.py`

The orchestrator (490 lines). Key methods:

- `unpack_mods()` — iterates `mods_path/*.jar`, extracts each to `temp/{jar_name}/`
- `get_lang_folders()` — walks temp/, finds folders containing source lang files (JSON or LANG), also discovers mcfunction-containing mods
- `edit_lang_files(lang_folders)` — for each folder: reads source files via parsers, calls `translator.translate_data()`, writes target files
- `translate_mcfunction_files(mod_root)` — processes `.mcfunction` files with `data modify storage ... set value "..."` patterns
- `convert_translated_mods()` — repacks temp folders into JAR files at translation_path
- `_convert_folder_to_jar()` — creates JAR, includes all original + translated files
- Cleanup/copy helpers: `remove_original_mod_files()`, `move_translated_mod_files()`, `copy_translated_files_to_same_path()`

When `mods_path == translation_path`, it verifies JAR validity after creation.

### `services/factory.py`

Single function `get_translator_service(provider, source_lang, target_lang, capitalize, max_retries, model)`:

| Provider | Service class | Notes |
|---|---|---|
| `google` | `GoogleService` | Always available if `deep-translator` installed |
| `openai` | `OpenAIService` → fallback `LitellmService` | If direct OpenAI import fails, uses LiteLLM |
| `openaicompatible` | `OpenAICompatibleService` | Requires `OPENAICOMPATIBLE_API_KEY` + `OPENAICOMPATIBLE_BASE_URL` |
| `anthropic` | `LitellmService` | Via LiteLLM with `provider="anthropic"` |
| `gemini` | `LitellmService` | Via LiteLLM with `provider="gemini"` |
| `ollama` | `LitellmService` | Via LiteLLM with `provider="ollama"` |
| `litellm` | `LitellmService` | Generic LiteLLM, uses `TRANSLATION_MODEL` env var |

AI_PROVIDERS = `frozenset({"openai", "anthropic", "gemini", "ollama", "litellm", "openaicompatible"})`

### `services/base_translator.py`

Abstract base class. Key design:

- **System prompts**: `TRANSLATION_SYSTEM_PROMPT` for single-string, `CHUNK_TRANSLATION_SYSTEM_PROMPT` for batch JSON — both instruct to preserve placeholders (`%s`, `%d`, `{{}}`)
- **Chunk size**: `_CHUNK_SIZE = 0` (disabled) by default. AI services set it to 10-25 to batch translations into a single API call
- **`_parse_chunk_response()`**: strips markdown fences (` ```json ``` `), parses JSON, supports node-code-fences (strips language tags on opening line)
- **Batch strategies**: sequential (`_batch_translate_seq`), parallel with ThreadPoolExecutor (`_batch_translate_parallel`), chunked-parallel (`_batch_translate_chunked`). Chunked is used when `_CHUNK_SIZE > 0`
- **Capitalize**: if enabled, first character of each translation is uppercased

### `services/google_service.py`

Uses `deep_translator.GoogleTranslator`. Wraps `translate()` with `@retry_with_exponential_backoff`. Applies preventive delay via `global_rate_limiter.apply_service_delay("google")`.

### `services/openai_service.py`

Direct OpenAI API client (`openai.OpenAI`). Reads `OPENAI_API_KEY` and `OPENAI_MODEL` from env. `_CHUNK_SIZE = 25`. Chunk translation: sends JSON payload in user message, expects JSON back. Falls back to per-item translate on parse failure. Raises `ValueError` if no API key found.

### `services/litellm_service.py`

Unified AI backend. Uses LiteLLM's `completion()` which auto-routes to the correct provider. Model resolution:
1. Explicit `model` parameter
2. `TRANSLATION_MODEL` env var
3. Provider defaults: `openai`→`gpt-4o-mini`, `anthropic`→`claude-3-haiku-20240307`, `gemini`→`gemini/gemini-1.5-flash`, `ollama`→`ollama/llama3`
4. Fallback: `gpt-4o-mini`

### `services/openai_compatible_service.py`

For any OpenAI-compatible API (vLLM, LM Studio, OpenRouter, etc.). Reads `OPENAICOMPATIBLE_API_KEY`, `OPENAICOMPATIBLE_BASE_URL`, `OPENAICOMPATIBLE_MODEL` from env. `_CHUNK_SIZE = 10` (more conservative, since local LLMs may have smaller context). Logs verbose completion metadata at debug level.

### `parsers/json_parser.py`

Parses JSON files with comments. `remove_comments_from_json()` strips `//` single-line and `/* */` multi-line comments via regex, then passes to `json.loads()`. Raises `FileParsingError` on invalid JSON or IO errors.

### `parsers/lang_parser.py`

Minecraft LANG format: `key=value` per line. `read_lang_file()` splits on first `=`. `write_lang_file()` writes `{key}={value}\n` for each entry. Both raise `FileParsingError` on IO errors.

### `parsers/mcfunction_parser.py`

Extracts translatable strings from Minecraft function files. Only processes lines with `data modify storage ... set value "..."`. Uses regex to extract quoted strings, handles escaped quotes. Keys are formatted as `{path}:{line_number}` so translations can be written back to the correct line.

### `commands/command_line.py`

CLI entry point. `build_argument_parser()` creates subparsers for `cli` and `app` commands. For backward compatibility, translate arguments are also added to the root parser. `main()` dispatches to `handle_translate_command()` or `app_main()`.

### `commands/translate.py`

Translation orchestrator. `add_translate_arguments()` defines CLI args. `handle_translate_command()`:
1. Resolves provider (handles deprecated `--ai` flag)
2. Checks dependencies (`_check_dependencies()` — verifies packages installed, API keys set)
3. Sets up logging
4. Creates Settings → FileManager
5. If dry-run: unpacks, finds lang folders, logs what would happen, cleans up
6. Otherwise: full translate flow → repack → verify → cleanup

### `commands/app.py`

Interactive TUI. Uses `questionary` for forms (with search filter), `rich` for styled output, `pyfiglet` for title. Supports 90+ languages via select/search dropdowns. Checks provider availability dynamically, shows ✅/❌ indicators. Runs translation in a `Progress` spinner context. Handles `KeyboardInterrupt` gracefully (silent exit).

### Exceptions

Hierarchy in `exceptions.py`:
- `TranslationError` (base)
  - `FileParsingError`
  - `JarPackagingError`
  - `ConfigurationError`
  - `TranslationServiceError`
    - `RateLimitExceededError`

### `utils/retry_logic.py`

**RateLimitTracker**: tracks consecutive rate limits, calculates exponential backoff with jitter. Returns delays: base * 2^(n-1), capped at 300s, with ±25% jitter.

**`retry_with_exponential_backoff` decorator**: accepts `max_retries`, `base_delay`, `max_delay`, `exceptions` tuple, optional `rate_limit_tracker`. On retry: applies preventive delay before first attempt if recent rate limits detected.

**`TranslationRateLimiter`**: global singleton that coordinates rate limits per service name.

**`create_retry_decorator(service, max_retries)`**: factory that picks the right exception types for each provider (OpenAI RateLimitError, LiteLLM RateLimitError, or generic Exception).

### `core/provider_check.py`

`check_provider_available(provider)` returns `(bool, str)`. Checks:
- Package imports (deep-translator, openai, litellm)
- API key env vars (OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, OPENAICOMPATIBLE_API_KEY + BASE_URL)
- OLLAMA_API_BASE defaults to `http://localhost:11434`

### `logging_config.py`

`setup_logging(log_dir, console_level)`: creates `mod_translator` logger with `RotatingFileHandler` (5MB, 3 backups) and `StreamHandler`. File handler logs DEBUG with full context; console handler uses clean format.

## Conventions

### Logging
```python
import logging
logger = logging.getLogger("mod_translator")
```
Use logger directly, never `print()`. Log levels: INFO for progress, WARNING for retries/fallback, ERROR for failures, DEBUG for verbose API responses.

### Type hints
All public methods use full type annotations (`dict[str, str]`, `list[str]`, `Path`, `bool`, `int`). Use `| None` for optionals. Use `collections.abc.Callable` for callables.

### Imports
- Ruff sorts imports (I rule) — standard library first, then third-party, then relative
- Use relative imports within the package: `from ..core.settings import Settings`

### Service pattern
1. Extend `BaseTranslatorService` — implement `translate(text: str) -> str`
2. Optionally override `_translate_chunk()` for batched API calls
3. Register in `factory.py` via `get_translator_service()`
4. Add provider check in `provider_check.py`
5. Wrap with `create_retry_decorator(service_name, max_retries)`
6. Apply `global_rate_limiter.apply_service_delay(service_name)` before each API call

### Error handling
Translation failures are logged and fall back to returning original text. Don't let a single translation failure stop the entire batch.

### Testing
All shared fixtures in `tests/conftest.py` — use `tmp_path` for temp dirs. Match source module structure: `src/app/core/file_manager.py` → `tests/test_file_manager.py`. Use `pytest.mark` for grouping. Mock translation services with `unittest.mock` or `pytest-mock`.

## Project commands

```bash
uv sync                    # Install all deps (including dev)
uv sync --extra ai         # Install with AI providers
uv run pytest              # Run tests
uv run pytest --cov        # Run tests with coverage
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run mypy src/           # Type check
uv run mod-translator app  # Run interactive app
```

## Environment variables

Copy `.env.example` to `.env`. Supported vars:

| Variable | Provider | Required |
|---|---|---|
| `TRANSLATION_MODEL` | All AI | No (default: gpt-4o-mini) |
| `OPENAI_API_KEY` | openai | Yes |
| `OPENAI_MODEL` | openai | No (default: gpt-3.5-turbo) |
| `ANTHROPIC_API_KEY` | anthropic | Yes |
| `GEMINI_API_KEY` | gemini | Yes |
| `OLLAMA_API_BASE` | ollama | No (default: http://localhost:11434) |
| `OPENAICOMPATIBLE_API_KEY` | openaicompatible | Yes |
| `OPENAICOMPATIBLE_BASE_URL` | openaicompatible | Yes |
| `OPENAICOMPATIBLE_MODEL` | openaicompatible | No |

LiteLLM auto-detects providers from these env vars — you don't need to set a `PROVIDER` var.

## Test structure

```
tests/
  conftest.py                      Shared fixtures (sample JSON/LANG/mcfunction, temp dirs, JAR builder)
  test_app.py                      Interactive app tests
  test_command_line_extended.py    CLI arg parsing
  test_data.py                     languages.json loading
  test_file_manager.py             File discovery, read/write
  test_file_manager_extended.py    Edge cases for file_manager
  test_google_translate_service.py Google service tests
  test_json_parser_edge.py         JSON parser edge cases
  test_lang_parser_edge.py         LANG parser edge cases
  test_logging_config.py           Logger setup
  test_main_entry.py               __main__.py entry point
  test_mcfunction_parser_edge.py   MCFUNCTION parser edge cases
  test_openai_check.py             Provider check logic
  test_openai_compatible_service.py OpenAI-compatible service
  test_openai_translate_service.py  OpenAI service tests
  test_progress_extended.py        ProgressReporter
  test_retry_logic.py              Retry/backoff logic
  test_settings.py                 Settings dataclass
  test_settings_extended.py        Settings edge cases
  test_translate_orchestrator.py   Translate command orchestration
  test_translator.py               Translator wrapper
  test_version.py                  Version tuple
```

## File format support

| Format | Extension | Structure | Parser |
|---|---|---|---|
| JSON with comments | `.json` | `{"key": "value"}` with `//` and `/* */` comments | `json_parser.py` |
| Minecraft LANG | `.lang` | `key=value` per line | `lang_parser.py` |
| MCFUNCTION | `.mcfunction` | Lines with `data modify storage ... set value "..."` | `mcfunction_parser.py` |

Source files are detected by filename: `{lang_code}.json` or `{lang_code}.lang` (case-insensitive). Target files are written with lowercase lang codes for JSON (`en_us.json`) and original-case for LANG (`en_US.lang`).
