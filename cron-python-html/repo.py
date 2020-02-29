from datetime import datetime
from typing import Union
from git import Repo
from pathlib import Path
from dirtools import DirFiles

timeformat = '%Y-%m-%d %H:%M:%S'


class RepoDir:
    def __init__(self, path: Path, repoid: str, maxdepth=10):
        self.path = path
        self.repo: Union[Repo, None] = None
        self.repoid = repoid
        self.maxdepth = maxdepth
        self.statusfile = Path(str(path) + ".status")
        self._files: Union[dict, None] = None
        self._dirloader = DirFiles(self.path)
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

    @property
    def files(self) -> dict:
        if self._files is None:
            self._files = self._dirloader.to_dict(self.maxdepth)

        return self._files

    @property
    def origin(self) -> str:
        if "origin" not in self.repo.remotes:
            return f"<local repository '{self.path}'>"

        origin = self.repo.remote("origin")

        try:
            url = next(origin.urls)
        except StopIteration:
            url = f"<local repository '{self.path}' without urls>"

        return url
