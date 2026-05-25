import os
import sys
import traceback

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(current_dir))  # .../src
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def _main() -> None:
    from app.commands.command_line import main
    main()


if __name__ == "__main__":
    try:
        _main()
    except Exception as e:
        print(f"Error in Mod Translator: {e}")
        traceback.print_exc()
        sys.exit(1)
