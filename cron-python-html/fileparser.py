from pathlib import Path
from typing import Tuple
from yaml import safe_load_all


def MDFileParser(path: Path) -> Tuple[dict, str]:
    yamldocs = safe_load_all(path.read_bytes())

    try:
        yamldoc = next(yamldocs)



        return yamldoc, ""

    except StopIteration:
        return {}, ""


