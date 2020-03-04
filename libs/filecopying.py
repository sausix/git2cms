from pathlib import Path, PosixPath
import shutil

PathFlavour = type(Path())  # Get prefered class base on OS to inherit from


class PathC(PathFlavour):
    # Extending Path objects with copy function.

    def mkdir_result(self, mode=0o777, parents=False, exist_ok=False) -> list:
        """
        Create a new directory at this given path.
        Returns all created directories as collection.
        """

        if parents:
            if self.parent == self:
                res = list()
            else:
                res = self.parent.mkdir_result(parents=True, exist_ok=True)
        else:
            # Dont create parents
            res = list()

        # Create myself
        if not self.exists():
            # I will be created
            res.append(self)

        # Create
        self.mkdir(mode, parents=False, exist_ok=exist_ok)

        return res

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
