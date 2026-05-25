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
- **AI-Powered Translation** — OpenAI integration for higher quality translations
- **Comprehensive File Support** — Compatible with JSON, LANG, and MCFUNCTION file formats
- **Multiple Translation Services** — Google Translate (free) and OpenAI (API key required)
- **Batch Processing** — Translate single files or entire mod folders at once
- **Smart Text Detection** — Automatically identifies translatable content while preserving game logic

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

## Usage

### Interactive Mode

```bash
mod-translator app
```

### Command Line Interface

```bash
# Basic usage with Google Translate (free)
mod-translator --path path/to/mods --source en_US --target es_ES --output path/to/output

# AI-powered translation with OpenAI (requires API key)
mod-translator --path path/to/mods --source en_US --target es_ES --output path/to/output --ai

# Parameters:
# --path (-p): Path to mod or mods folder (default: ./mods)
# --source (-s): Source language code (e.g., en_US)
# --target (-t): Target language code (e.g., es_ES)
# --output (-o): Output folder path (if same as mods path, will replace original mods)
# --ai: Use OpenAI translation instead of Google Translate (requires OPENAI_API_KEY)
```

## AI Translation Setup

To use OpenAI-powered translation:

1. Get an OpenAI API key from [OpenAI API](https://platform.openai.com/api-keys)
2. Create a `.env` file in the project root:

   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

3. Install dependencies:

    ```bash
    uv sync --extra ai
    ```

4. Use the `--ai` flag when running translations

> OpenAI translation provides better context awareness and gaming-specific terminology but requires an API key with usage costs.

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
