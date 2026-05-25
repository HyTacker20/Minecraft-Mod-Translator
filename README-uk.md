<p align="center">
  <img src="docs/logo/logo.png" alt="Логотип" width="200">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-CC%20BY--NC%204.0-blue.svg" alt="Ліцензія"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python"></a>
</p>

# Minecraft Mod Translator

Інструмент для перекладу модифікацій Minecraft на різні мови, що автоматизує процес локалізації для розробників модів і перекладачів.

## Можливості

- **Автоматичний переклад** — швидкий переклад файлів модів на різні мови
- **AI-переклад** — декілька AI-провайдерів для перекладів вищої якості
- **Підтримка форматів** — сумісність з JSON, LANG та MCFUNCTION файлами
- **Декілька сервісів перекладу** — Google Translate (безкоштовно) та AI-провайдери (OpenAI, Anthropic, Gemini, Ollama, OpenAI-сумісні)
- **Пакетна обробка** — переклад окремих файлів або цілих тек модів
- **Розумне визначення тексту** — автоматично визначає контент для перекладу, зберігаючи ігрову логіку

## Провайдери перекладу

| Провайдер | Прапорець | Вартість | Вимоги |
|---|---|---|---|
| Google Translate | `--provider google` | Безкоштовно | Пакет `deep-translator` |
| OpenAI | `--provider openai` | Платний | `OPENAI_API_KEY` |
| Anthropic Claude | `--provider anthropic` | Платний | `ANTHROPIC_API_KEY` |
| Google Gemini | `--provider gemini` | Платний/Безкоштовний | `GEMINI_API_KEY` |
| Ollama (Локальний) | `--provider ollama` | Безкоштовно | Ollama запущено локально |
| OpenAI-Сумісний | `--provider openaicompatible` | Залежить | `OPENAICOMPATIBLE_API_KEY` + `OPENAICOMPATIBLE_BASE_URL` |

## Встановлення

### Готові виконувані файли

Завантажте готові виконувані файли зі сторінки релізів:

- **Версія застосунку** — `Minecraft Mod Translator.exe` (інтерактивний застосунок)
- **Версія CLI** — `mod-translator.exe` (інтерфейс командного рядка)

Встановлення Python не потрібне.

### З вихідного коду

```bash
# Спочатку встановіть uv (https://docs.astral.sh/uv/getting-started/installation/)
git clone https://github.com/zvictorium/minecraft-mod-translator.git
cd minecraft-mod-translator

# Налаштування середовища (Windows)
scripts\setup.bat
# Або для Linux/Mac
./scripts/setup.sh

# Для підтримки AI-перекладу встановіть додаткові залежності:
uv sync --extra ai

# Запуск застосунку (Windows)
scripts\start.bat
# Або для Linux/Mac
./scripts/start.sh
```

## Конфігурація

Скопіюйте `.env.example` у `.env` та налаштуйте API ключі:

```bash
cp .env.example .env
```

Підтримувані змінні середовища:

| Змінна | Провайдер | Обов'язково | За замовчуванням |
|---|---|---|---|
| `TRANSLATION_MODEL` | Усі AI | Ні | `gpt-4o-mini` |
| `OPENAI_API_KEY` | openai | Так | — |
| `OPENAI_MODEL` | openai | Ні | `gpt-3.5-turbo` |
| `ANTHROPIC_API_KEY` | anthropic | Так | — |
| `GEMINI_API_KEY` | gemini | Так | — |
| `OLLAMA_API_BASE` | ollama | Ні | `http://localhost:11434` |
| `OPENAICOMPATIBLE_API_KEY` | openaicompatible | Так | — |
| `OPENAICOMPATIBLE_BASE_URL` | openaicompatible | Так | — |
| `OPENAICOMPATIBLE_MODEL` | openaicompatible | Ні | `gpt-4o-mini` |

## Використання

### Інтерактивний режим

```bash
mod-translator app
```

### Інтерфейс командного рядка

```bash
# Базове використання з Google Translate (безкоштовно)
mod-translator cli --path path/to/mods --source en_US --target uk_UA --output path/to/output

# AI-переклад з OpenAI (потрібен API ключ)
mod-translator cli --path path/to/mods --source en_US --target uk_UA --output path/to/output --provider openai

# Використання Anthropic Claude
mod-translator cli --path path/to/mods --source en_US --target uk_UA --output path/to/output --provider anthropic

# Використання Google Gemini
mod-translator cli --path path/to/mods --source en_US --target uk_UA --output path/to/output --provider gemini

# Використання локального Ollama
mod-translator cli --path path/to/mods --source en_US --target uk_UA --output path/to/output --provider ollama

# Попередній перегляд (dry-run)
mod-translator cli --path path/to/mods --source en_US --target uk_UA --dry-run

# Параметри:
# --path (-p): Шлях до моду або теки з модами (за замовчуванням: ./mods)
# --source (-s): Код вихідної мови (напр., en_US)
# --target (-t): Код цільової мови (напр., uk_UA)
# --output (-o): Шлях до вихідної теки (якщо збігається з текою модів, замінить оригінальні моди)
# --provider: Провайдер перекладу (google, openai, anthropic, gemini, ollama, openaicompatible)
# --workers: Кількість одночасних потоків перекладу (за замовчуванням: 4)
# --dry-run: Показати, що буде перекладено, без внесення змін
# --debug (-d): Увімкнути debug-логування
```

> Прапорець `--ai` застарілий. Використовуйте `--provider openai` натомість.

## Розробка

### Налаштування

```bash
uv sync                # Встановити основні залежності
uv sync --extra ai     # Встановити залежності AI-провайдерів
uv sync --group dev    # Встановити інструменти розробки (pytest, ruff, mypy)
```

### Команди

```bash
uv run pytest              # Запуск тестів
uv run pytest --cov        # Запуск тестів з покриттям
uv run ruff check .        # Лінтинг
uv run ruff format .       # Форматування
uv run mypy src/           # Перевірка типів
```

### Структура проекту

```
src/app/
  core/            Settings, Translator, FileManager, перевірки провайдерів
  services/        Провайдери перекладу (Google, OpenAI, LiteLLM та ін.)
  parsers/         Парсери файлів (JSON, LANG, MCFUNCTION)
  commands/        CLI точки входу та TUI застосунок
  utils/           Логіка повторів, обмеження запитів, звітування прогресу
tests/             Набір тестів Pytest
scripts/           Скрипти збірки та налаштування
docs/              Логотип та скріншоти
```

## Скріншоти

### Головний застосунок

![Головний застосунок](docs/screenshots/main-app.png)

### Підтвердження

![Підтвердження](docs/screenshots/confirmation.png)

### Процес перекладу

![Процес перекладу](docs/screenshots/translation-process.png)

### Перегляд результатів

![Перегляд результатів](docs/screenshots/results-view.png)

## Ліцензія

Цей проект ліцензовано відповідно до [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](LICENSE).

### Зазначення авторства

Оригінальна робота: **zvictorium** — [GitHub репозиторій](https://github.com/zvictorium/minecraft-mod-translator)
