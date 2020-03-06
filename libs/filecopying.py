from pathlib import Path, PosixPath
import shutil

PathFlavour = type(Path())  # Get prefered class base on OS to inherit from


class PathC(PosixPath):
    # Extending Path objects with copy function.

    def copy(self, target: Path) -> "PathC":
        if self.is_dir():
            # Copy a directory with contents
            pass

        elif self.is_file():
            # Copy a single file
            cls = type(self)
            return cls(shutil.copy(str(self), str(target)))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.as_posix()})"

    # Unchecked functions of Path class that may return an Path instance instead of self: PathC.
    # parents, parent, joinpath, relative_to, with_name, with_suffix, home, expanduser, glob, rename, replace, resolve, rglob
