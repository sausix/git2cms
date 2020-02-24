from datetime import datetime
from typing import Union
from git import Repo
from pathlib import Path

timeformat = '%Y-%m-%d %H:%M:%S'


class RepoDir:
    def __init__(self, path: Path, repoid: str):
        self.path = path
        self.repo = None
        self.repoid = repoid
        self.statusfile = Path(str(path) + ".status")
        self._files: Union[dict, None] = None
        self.reload()

    def reload(self):
        self.repo = Repo(self.path)
        self._files = None

    def get_commit_date(self) -> datetime:
        # 2020-02-16 04:53:32+01:00 <class 'datetime.datetime'>
        return self.repo.heads.master.commit.committed_datetime.replace(tzinfo=None)

    def get_commit_summary(self) -> str:
        return self.repo.heads.master.commit.summary

    def get_process_date(self) -> Union[datetime, None]:
        if self.statusfile.exists():
            dstr = self.statusfile.read_text()
            return datetime.strptime(dstr, timeformat)
        else:
            return None

    def commit_date_newer(self) -> bool:
        if self.get_process_date() is None:
            return True

        return self.get_commit_date() > self.get_process_date()

    def store_process_date(self):
        self.statusfile.write_text(self.get_commit_date().strftime(timeformat))

    def loadfiles(self, directory: Path, recurse=True):
        "Add files from directory to files list of this object."
        # Files first
        for element in directory.iterdir():
            if element.is_file():
                if element.name[:1] != ".":
                    key = str(element.relative_to(self.path)).replace("\\", "/")
                    self._files[key] = element

        # Then subdirs if recurse
        if recurse:
            for element in directory.iterdir():
                if element.is_dir():
                    if element.name[:1] != ".":
                        self.loadfiles(directory / element, recurse)

    @property
    def files(self) -> dict:
        if self._files is None:
            self._files = dict()
            self.loadfiles(self.path)

        return self._files
