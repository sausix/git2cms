from pathlib import Path
from typing import Tuple
from yaml import SafeLoader


def parse_md_file(path: Path) -> Tuple[dict, str]:
    loader = SafeLoader(path.read_bytes())

    try:
        # Read YAML-Header
        if loader.check_data():
            # Found header
            header = loader.get_data()

            if loader.check_data():
                start = loader.pointer
                # length = len(loader.buffer)
                content = loader.buffer[start+1:]

                return header, content
            else:
                return header, ""
        else:
            # No headers, only content
            return {}, path.read_text(encoding="UTF-8")

    finally:
        loader.dispose()
