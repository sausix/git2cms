import subprocess
import sys
import pathlib


class Page:
    def __init__(self, config, pageconfig, stdout=None):
        self.config = config
        self.pageconfig = pageconfig
        self._create_absolute_pagepaths()
        self._check_pagepaths()

        self.stdout = stdout
        if self.stdout is None:
            if "logfile" in self.pageconfig.WRITE_DESTINATIONS:
                # Logfile configured
                if len(self.pageconfig.WRITE_DESTINATIONS["logfile"]):
                    # Use logfile if not empty
                    self.stdout = open(self.pageconfig.WRITE_DESTINATIONS["logfile"], "w")
            else:
                # Use stdout from process if no logfile configured.
                self.stdout = sys.stdout

    def log(self, text: str):
        "Output text to stdout"
        if self.stdout is None:
            return

        self.stdout.write(text)
        self.stdout.write("\n")

    def fail(self, text: str):
        "Raise an Exception and quit application"
        raise Exception(text)

    def printpaths(self):
        self.log("CLONE_DESTINATIONS")
        for key, value in self.pageconfig.CLONE_DESTINATIONS.items():
            self.log(f"{key}: {value}")

        self.log("WRITE_DESTINATIONS")
        for key, value in self.pageconfig.WRITE_DESTINATIONS.items():
            self.log(f"{key}: {value}")

    def _create_absolute_pagepaths(self):
        if len(self.pageconfig.ROOT) == 0:
            self.pageconfig.ROOT = self.config.ROOT
        elif self.pageconfig.ROOT[:1] != "/":
            # Relative path
            self.pageconfig.ROOT = f"{self.config.ROOT}/{self.pageconfig.ROOT}"

        self.pageconfig.CLONE_DESTINATIONS = {
            key: path if path[:1] == "/" else self.pageconfig.ROOT + "/" + path for key, path in self.pageconfig.CLONE_DESTINATIONS.items()
        }

        self.pageconfig.WRITE_DESTINATIONS = {
            key: path if path[:1] == "/" or len(path) == 0 else self.pageconfig.ROOT + "/" + path for key, path in self.pageconfig.WRITE_DESTINATIONS.items()
        }

    def _check_pagepaths(self):
        print(self.pageconfig.CLONE_DESTINATIONS)

        for path in self.pageconfig.CLONE_DESTINATIONS.values():
            p = pathlib.Path(path)
            p.mkdir(parents=True, exist_ok=True)

        if "logfile" in self.pageconfig.WRITE_DESTINATIONS:
            if len(self.pageconfig.WRITE_DESTINATIONS["logfile"]):
                p = pathlib.Path(self.pageconfig.WRITE_DESTINATIONS["logfile"])
                folder = p.parent
                folder.mkdir(parents=True, exist_ok=True)

    def clone_authors(self):
        for authorgitid, url in self.pageconfig.GIT_SOURCES_AUTHORS.items():
            self.clone_author(authorgitid, url)

    def clone_author(self, authorgitid: str, url: str):
        authordir = f"{self.pageconfig.CLONE_DESTINATIONS['authors']}/{authorgitid}"

        cmd = 'git', 'clone', url, authordir

        with open(f"{authordir}.log", "w") as log:
            with open(f"{authordir}.err", "w") as err:
                try:
                    subprocess.run(cmd, stdout=log, stderr=err)
                except Exception as e:
                    err.write(f"Error while running git on author {authorgitid}: \n")
                    err.write(" ".join(e.args))
                    err.write("\n")

    def clone_templates(self):
        for templategitid, url in self.pageconfig.GIT_SOURCES_TEMPLATES.items():
            self.clone_template(templategitid, url)

    def clone_template(self, templateid: str, url: str):
        templatesdir = f"{self.pageconfig.CLONE_DESTINATIONS['templates']}/{templateid}"

        cmd = 'git', 'clone', url, templatesdir

        with open(f"{templatesdir}.log", "w") as log:
            with open(f"{templatesdir}.err", "w") as err:
                try:
                    subprocess.run(cmd, stdout=log, stderr=err)
                except Exception as e:
                    err.write(f"Error while running git on template {templateid}: \n")
                    err.write(" ".join(e.args))
                    err.write("\n")

    def generate_content(self):
        pass
