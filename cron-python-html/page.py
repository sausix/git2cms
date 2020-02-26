import subprocess
import sys
from pathlib import Path
from pagecontent import PageContent
from repo import RepoDir
from streamlogging import Logger


class Page:
    def __init__(self, config, pageconfig, logger: Logger=None):
        self.config = config
        self.pageconfig = pageconfig
        self._create_absolute_pagepaths()
        self._check_pagepaths()

        self.log = logger
        if self.log is None:
            # Determine log destinations
            logfile = self.pageconfig.LOGFILE

            if isinstance(logfile, Path):
                stream = open(str(logfile), "w")
                self.log = Logger(stream, stream, stream)
            else:
                # Use stdout from process if no logfile configured.
                self.log = Logger(sys.stdout, sys.stdout, sys.stderr)

        self.contentgen = PageContent(
            self.config,
            self.pageconfig,
            self.log.sublogger("CONTENT")
        )

    def fail(self, text: str):
        "Raise an Exception and quit application"
        self.log.err(text)
        raise Exception(text)

    def _create_absolute_pagepaths(self):
        # pageconfig.ROOT
        if isinstance(self.pageconfig.ROOT, Path):
            # Path set
            if not self.pageconfig.ROOT.is_absolute():
                self.pageconfig.ROOT = Path(self.config.ROOT) / Path(self.pageconfig.ROOT)
        else:
            # Not set or unknown type
            self.pageconfig.ROOT = Path(self.config.ROOT)

        root = self.pageconfig.ROOT

        # pageconfig.CLONE_DESTINATIONS
        self.pageconfig.CLONE_DESTINATIONS = {
            key: path if path.is_absolute() else root / path
            for key, path in self.pageconfig.CLONE_DESTINATIONS.items()  # type: str, Path
        }

        # pageconfig.WEBROOT
        if not self.pageconfig.WEBROOT.is_absolute():
            self.pageconfig.WEBROOT = root / self.pageconfig.WEBROOT

        # pageconfig.LOGFILE
        if not self.pageconfig.LOGFILE.is_absolute():
            self.pageconfig.LOGFILE = root / self.pageconfig.LOGFILE

    def _check_pagepaths(self):
        # Create CLONE_DESTINATIONS folders
        for path in self.pageconfig.CLONE_DESTINATIONS.values():
            p = Path(path)
            p.mkdir(parents=True, exist_ok=True)

        # Create pageconfig.WEBROOT folder
        if isinstance(self.pageconfig.WEBROOT, Path):
            self.pageconfig.WEBROOT.mkdir(parents=True, exist_ok=True)

        # Create logfile folders
        if isinstance(self.pageconfig.LOGFILE, Path):
            parent = self.pageconfig.LOGFILE.parent
            parent.mkdir(parents=True, exist_ok=True)

    def clone_all(self):
        self.clone_authors()
        self.clone_templates()

    def clone_authors(self):
        key = "AUTHORS"
        for gitid, url in self.pageconfig.GIT_SOURCES[key].items():
            self.clone_by_key(key, gitid, url)

    def clone_templates(self):
        key = "TEMPLATES"
        for gitid, url in self.pageconfig.GIT_SOURCES[key].items():
            self.clone_by_key(key, gitid, url)

    def open_repos_by_key(self, key: str) -> dict:
        ret = dict()

        clonefolder = self.pageconfig.CLONE_DESTINATIONS[key]

        for gitid in self.pageconfig.GIT_SOURCES[key].keys():
            folder = clonefolder / Path(gitid)
            if folder.is_dir():
                ret[gitid] = RepoDir(folder, gitid)
            else:
                self.log.warn(f"Repo folder not valid. Must be a directory. Skipped: {folder}")

        return ret

    def clone(self, repoid: str, folder: Path, url: str):
        if folder.exists():
            # git --git-dir=sausix_main/.git pull "https://github.com/sausix/hackersweblog.net-author.git"
            self.log.out(f"Pulling {repoid} from {url} into {folder}")
            cmds = ("git", "-C", str(folder), "pull", url),
        else:
            # git clone "https://github.com/sausix/hackersweblog.net-author.git" sausix_main
            self.log.out(f"Cloning {repoid} from {url} into {folder}")
            cmds = ("git", "clone", url, str(folder)),

        try:
            for cmd in cmds:
                res = subprocess.run(cmd, stdout=self.log._out, stderr=self.log._out)  # TODO: iowrapper
                if res.returncode:
                    self.log.err(f"git command returned {res.returncode}")

        except Exception as e:
            self.log.err(f"Error while running git on {repoid}:")
            self.log.err(" ".join(e.args))

    def clone_by_key(self, key: str, gitid: str, url: str):
        directory = self.pageconfig.CLONE_DESTINATIONS[key] / Path(gitid)
        self.clone(gitid, directory, url)

    def generate_content(self, onlywhenchanged: bool = True):
        repos = {key: self.open_repos_by_key(key) for key in self.pageconfig.GIT_SOURCES.keys()}
        self.contentgen.generate(repos, onlywhenchanged)
