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
- **AI-переклад** — інтеграція з OpenAI для перекладів вищої якості
- **Підтримка форматів** — сумісність з JSON, LANG та MCFUNCTION файлами
- **Декілька сервісів перекладу** — Google Translate (безкоштовно) та OpenAI (потрібен API ключ)
- **Пакетна обробка** — переклад окремих файлів або цілих тек модів
- **Розумне визначення тексту** — автоматично визначає контент для перекладу, зберігаючи ігрову логіку

## Встановлення

### Готові виконувані файли

Завантажте готові виконувані файли зі сторінки релізів:

- **Версія застосунку** — `Minecraft Mod Translator.exe` (інтерактивний застосунок)
- **Версія CLI** — `mod-translator.exe` (інтерфейс командного рядка)

Встановлення Python не потрібне.

### З вихідного коду

```bash
git clone https://github.com/zvictorium/minecraft-mod-translator.git
cd minecraft-mod-translator

# Налаштування середовища (Windows)
setup.bat
# Або для Linux/Mac
./setup.sh

# Для підтримки AI-перекладу встановіть додаткові залежності:
pip install openai python-dotenv
# Або встановіть все одразу:
pip install -e .[ai]

# Запуск застосунку (Windows)
start.bat
# Або для Linux/Mac
./start.sh
```

## Використання

### Інтерактивний режим

```bash
mod-translator app
```

### Інтерфейс командного рядка

```bash
# Базове використання з Google Translate (безкоштовно)
mod-translator --path path/to/mods --source en_US --target uk_UA --output path/to/output

# AI-переклад з OpenAI (потрібен API ключ)
mod-translator --path path/to/mods --source en_US --target uk_UA --output path/to/output --ai

# Параметри:
# --path (-p): Шлях до моду або теки з модами (за замовчуванням: ./mods)
# --source (-s): Код вихідної мови (напр., en_US)
# --target (-t): Код цільової мови (напр., uk_UA)
# --output (-o): Шлях до вихідної теки (якщо збігається з текою модів, замінить оригінальні моди)
# --ai: Використовувати переклад OpenAI замість Google Translate (потрібен OPENAI_API_KEY)
```

## Налаштування AI-перекладу

Для використання перекладу на основі OpenAI:

1. Отримайте API ключ OpenAI на [OpenAI API](https://platform.openai.com/api-keys)
2. Створіть файл `.env` у кореневій теці проекту:

   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

3. Встановіть залежності:

   ```bash
   pip install openai python-dotenv
   ```

4. Використовуйте прапорець `--ai` під час запуску перекладу

> Переклад OpenAI забезпечує краще розуміння контексту та ігрової термінології, але потребує API ключа з витратами на використання.

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
