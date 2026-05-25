<p align="center">
  <img src="docs/logo/logo.png" alt="Logo" width="200">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-CC%20BY--NC%204.0-blue.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python"></a>
</p>

# Minecraft Mod Translator

A tool for translating Minecraft mods into multiple languages, automating the localization process for mod developers and translators.

## Features

- **Automated Translation** — Translate mod files to multiple languages
- **AI-Powered Translation** — Multiple AI providers for higher quality translations
- **Comprehensive File Support** — JSON, LANG, and MCFUNCTION file formats
- **Multiple Translation Services** — Google Translate (free) and AI providers (OpenAI, Anthropic, Gemini, Ollama, OpenAI-Compatible)
- **Batch Processing** — Translate single files or entire mod folders at once
- **Smart Text Detection** — Automatically identifies translatable content while preserving game logic

## Translation Providers

| Provider | Flag | Cost | Requirements |
|---|---|---|---|
| Google Translate | `--provider google` | Free | `deep-translator` package |
| OpenAI | `--provider openai` | Paid | `OPENAI_API_KEY` |
| Anthropic Claude | `--provider anthropic` | Paid | `ANTHROPIC_API_KEY` |
| Google Gemini | `--provider gemini` | Paid/Free tier | `GEMINI_API_KEY` |
| Ollama (Local) | `--provider ollama` | Free | Ollama running locally |
| OpenAI-Compatible | `--provider openaicompatible` | Varies | `OPENAICOMPATIBLE_API_KEY` + `OPENAICOMPATIBLE_BASE_URL` |

## Installation

### Pre-built Executables

Download ready-to-use executable files from the releases page:

- **App Version** — `Minecraft Mod Translator.exe` (interactive application)
- **CLI Version** — `mod-translator.exe` (command-line interface)

No Python installation required.

### From Source

```bash
# Install uv first (https://docs.astral.sh/uv/getting-started/installation/)
git clone https://github.com/zvictorium/minecraft-mod-translator.git
cd minecraft-mod-translator

# Setup the environment (Windows)
scripts\setup.bat
# Or for Linux/Mac
./scripts/setup.sh

# For AI translation support, sync with ai extras:
uv sync --extra ai

# Run the application (Windows)
scripts\start.bat
# Or for Linux/Mac
./scripts/start.sh
```

## Configuration

Copy `.env.example` to `.env` and configure your API keys:

```bash
cp .env.example .env
```

Supported environment variables:

| Variable | Provider | Required | Default |
|---|---|---|---|
| `TRANSLATION_MODEL` | All AI | No | `gpt-4o-mini` |
| `OPENAI_API_KEY` | openai | Yes | — |
| `OPENAI_MODEL` | openai | No | `gpt-3.5-turbo` |
| `ANTHROPIC_API_KEY` | anthropic | Yes | — |
| `GEMINI_API_KEY` | gemini | Yes | — |
| `OLLAMA_API_BASE` | ollama | No | `http://localhost:11434` |
| `OPENAICOMPATIBLE_API_KEY` | openaicompatible | Yes | — |
| `OPENAICOMPATIBLE_BASE_URL` | openaicompatible | Yes | — |
| `OPENAICOMPATIBLE_MODEL` | openaicompatible | No | `gpt-4o-mini` |

## Usage

### Interactive Mode

```bash
mod-translator app
```

### Command Line Interface

```bash
# Basic usage with Google Translate (free)
mod-translator cli --path path/to/mods --source en_US --target es_ES --output path/to/output

# AI-powered translation with OpenAI (requires API key)
mod-translator cli --path path/to/mods --source en_US --target es_ES --output path/to/output --provider openai

# Use Anthropic Claude
mod-translator cli --path path/to/mods --source en_US --target es_ES --output path/to/output --provider anthropic

# Use Google Gemini
mod-translator cli --path path/to/mods --source en_US --target es_ES --output path/to/output --provider gemini

# Use local Ollama
mod-translator cli --path path/to/mods --source en_US --target es_ES --output path/to/output --provider ollama

# Dry-run to preview changes
mod-translator cli --path path/to/mods --source en_US --target es_ES --dry-run

# Parameters:
# --path (-p): Path to mod or mods folder (default: ./mods)
# --source (-s): Source language code (e.g., en_US)
# --target (-t): Target language code (e.g., es_ES)
# --output (-o): Output folder path (if same as mods path, will replace original mods)
# --provider: Translation provider (google, openai, anthropic, gemini, ollama, openaicompatible)
# --workers: Number of concurrent translation workers (default: 4)
# --dry-run: Show what would be translated without making changes
# --debug (-d): Enable debug logging
```

> The `--ai` flag is deprecated. Use `--provider openai` instead.

## Development

### Setup

```bash
uv sync                # Install core dependencies
uv sync --extra ai     # Install AI provider dependencies
uv sync --group dev    # Install dev tools (pytest, ruff, mypy)
```

### Commands

```bash
uv run pytest              # Run tests
uv run pytest --cov        # Run tests with coverage
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run mypy src/           # Type check
```

### Project Structure

```
src/app/
  core/            Settings, Translator, FileManager, provider checks
  services/        Translation providers (Google, OpenAI, LiteLLM, etc.)
  parsers/         File parsers (JSON, LANG, MCFUNCTION)
  commands/        CLI entry points and TUI application
  utils/           Retry logic, rate limiting, progress reporting
tests/             Pytest test suite
scripts/           Build and setup scripts
docs/              Logo and screenshots
```

## Screenshots

### Main Application

![Main Application](docs/screenshots/main-app.png)

### Confirmation

![Confirmation](docs/screenshots/confirmation.png)

### Translation Process

![Translation Process](docs/screenshots/translation-process.png)

### Results View

![Results View](docs/screenshots/results-view.png)

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](LICENSE).

### Attribution

Original work by **zvictorium** — [GitHub Repository](https://github.com/zvictorium/minecraft-mod-translator)
