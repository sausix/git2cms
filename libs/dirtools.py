import os
from pathlib import Path

# if os.name == 'nt':
#    import win32api, win32con  # TODO requirements


def is_item_hidden_posix(item: Path) -> bool:
    return item.name.startswith(".")


def is_item_hidden_nt(item: Path) -> bool:
    return False
    # attributes = win32api.GetFileAttributes(item)
    # return attributes & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)


def os_hidden_func():
    return {
        "posix": is_item_hidden_posix,
        "nt": is_item_hidden_nt
    }.get(os.name, is_item_hidden_posix)


class DirFiles:
    def __init__(self, path: Path, hidden_file_func=os_hidden_func()):
        self.path = path
        self.hidden_file_func = hidden_file_func

    def to_dict(self, maxdepth: int, with_folders=False, with_files=True, hidden_files=False, hidden_folders=False) -> dict:
        def key(p: Path) -> str:
            return str(p.relative_to(self.path)).replace("\\", "/")

        def loaditems(directory: Path, level: int) -> dict:
            # Collect result set
            ret = dict()

            if with_folders or level < maxdepth:
                # Iterate folders
                for d in directory.iterdir():
                    if d.is_dir():
                        if hidden_folders or not self.hidden_file_func(d):
                            if with_folders:
                                ret[key(d)] = d

                            if level < maxdepth:
                                ret.update(loaditems(d, level+1))

            # Files
            if with_files:
                for f in directory.iterdir():
                    if f.is_file():
                        if hidden_files or not self.hidden_file_func(f):
                            ret[key(f)] = f

            return ret

        return loaditems(directory=self.path, level=0)
