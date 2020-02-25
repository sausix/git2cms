import subprocess
import sys
from pathlib import Path
from pagecontent import PageContent
from repo import RepoDir


class Page:
    def __init__(self, config, pageconfig, stdout=None):
        self.config = config
        self.pageconfig = pageconfig
        self._create_absolute_pagepaths()
        self._check_pagepaths()
        self.stdout = stdout

        if self.stdout is None:
            self.stdout = self.pageconfig.WRITE_DESTINATIONS.get("LOGFILE", NotImplemented)

            if self.stdout is NotImplemented:
                # Use stdout from process if no logfile configured.
                self.stdout = sys.stdout
            elif type(self.stdout) is str:
                # Logfile configured
                if len(str(self.stdout)):
                    # Use logfile if not empty
                    self.stdout = open(str(self.stdout), "w")

        self.contentgen = PageContent(
            self.config,
            self.pageconfig,
            self.stdout
        )

    def log(self, text: str):
        "Output text to stdout"
        if self.stdout is None:
            return

        self.stdout.write(text)
        self.stdout.write("\n")

    def fail(self, text: str):
        "Raise an Exception and quit application"
        raise Exception(text)

    def _create_absolute_pagepaths(self):
        if len(self.pageconfig.ROOT) == 0:
            self.pageconfig.ROOT = self.config.ROOT
        elif self.pageconfig.ROOT[:1] != "/":
            # Relative path
            self.pageconfig.ROOT = f"{self.config.ROOT}/{self.pageconfig.ROOT}"

        self.pageconfig.CLONE_DESTINATIONS = {
            key: path if path[:1] == "/"
            else self.pageconfig.ROOT + "/" + path
            for key, path in self.pageconfig.CLONE_DESTINATIONS.items()
        }

        self.pageconfig.WRITE_DESTINATIONS = {
            key: path if path[:1] == "/" or len(path) == 0
            else self.pageconfig.ROOT + "/" + path
            for key, path in self.pageconfig.WRITE_DESTINATIONS.items()
        }

    def _check_pagepaths(self):
        for path in self.pageconfig.CLONE_DESTINATIONS.values():
            p = Path(path)
            p.mkdir(parents=True, exist_ok=True)

        if "LOGFILE" in self.pageconfig.WRITE_DESTINATIONS:
            if len(self.pageconfig.WRITE_DESTINATIONS["LOGFILE"]):
                p = Path(self.pageconfig.WRITE_DESTINATIONS["LOGFILE"])
                folder = p.parent
                folder.mkdir(parents=True, exist_ok=True)

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

        clonedir = self.pageconfig.CLONE_DESTINATIONS[key]
        rootfolder = Path(clonedir)

        for gitid in self.pageconfig.GIT_SOURCES[key].keys():
            folder = rootfolder / Path(gitid)
            if folder.is_dir():
                ret[gitid] = RepoDir(folder, gitid)

        return ret

    def clone(self, repoid: str, folder: str, url: str):
        f = Path(folder)
        if f.exists():
            # git --git-dir=sausix_main/.git pull "https://github.com/sausix/hackersweblog.net-author.git"
            self.log(f"Pulling {repoid} from {url}")
            cmds = ("git", "-C", folder, "pull", url),
        else:
            # git clone "https://github.com/sausix/hackersweblog.net-author.git" sausix_main
            self.log(f"Cloning {repoid} from {url}")
            cmds = ("git", "clone", url, folder),

        with open(f"{folder}.log", "w") as log:
            with open(f"{folder}.err", "w") as err:
                try:
                    for cmd in cmds:
                        res = subprocess.run(cmd, stdout=log, stderr=err)
                        if res.returncode:
                            raise Exception(f"git command returned {res.returncode}")

                except Exception as e:
                    err.write(f"Error while running git on {repoid}: \n")
                    err.write(" ".join(e.args))
                    err.write("\n")

    def clone_by_key(self, key: str, gitid: str, url: str):
        directory = f"{self.pageconfig.CLONE_DESTINATIONS[key]}/{gitid}"
        self.clone(gitid, directory, url)

    def generate_content(self, onlywhenchanged: bool = True):
        repos = {key: self.open_repos_by_key(key) for key in self.pageconfig.GIT_SOURCES.keys()}
        self.contentgen.generate(repos, onlywhenchanged)
