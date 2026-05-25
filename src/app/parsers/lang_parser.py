from ..exceptions import FileParsingError


def read_lang_file(path: str) -> dict[str, str]:
    data = {}
    try:
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except OSError as e:
        raise FileParsingError(f"Cannot read {path}: {e}") from e

    for line in lines:
        line = line.strip()
        if line:
            try:
                key, value = line.split("=", 1)
                data[key] = value
            except ValueError:
                pass
    return data


def write_lang_file(data: dict[str, str], path: str) -> None:
    import os
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        text = ""
        for key, value in data.items():
            text += f"{key}={value}\n"
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
    except OSError as e:
        raise FileParsingError(f"Cannot write {path}: {e}") from e
