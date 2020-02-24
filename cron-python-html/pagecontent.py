import markdown
from repo import RepoDir
from fileparser import MDFileParser
from pathlib import Path
import re

"""
---
title: Generelle Infos
date: 2020-02-15
publish: Hidden
publish-after: 2020-02-15 12:00
description: Diese Seite beinhaltet ein paar Markdown-Elemente
tags: demo, markdown
source: http://where-i-stole-my-content.com/article.html
linkto: some-category/other-content-pointed-to
linkwith: some-category/other-content-linked-vice-versa
---
"""
AUTHORMETA_FILE = "author/meta.md"
AUTHORMETA_BASEDICT = {
    "langs": set(),
    "contents": dict()
}

is_author_lang_content = re.compile(r"^author/([a-z]{2})\.md$")
is_content_lang_md = re.compile(r"^content/(.*)\.([a-z]{2})\.md$")


class PageContent:
    def __init__(self, writefolder: str, contentsettings: dict, stdout=None):
        self.writefolder = writefolder
        self.contentsettings = contentsettings
        self.stdout = stdout

    def log(self, text: str):
        "Output text to stdout"
        if self.stdout is None:
            return

        self.stdout.write(text)
        self.stdout.write("\n")

    def warn(self, text: str):
        "Output warning to stdout"
        if self.stdout is None:
            return

        self.stdout.write("#WARNING: ")
        self.stdout.write(text)
        self.stdout.write("\n")

    def need_regenerate(self, repolist: list) -> bool:
        found = False

        self.log("Checking if sources have updated...")
        for repo in repolist:  # type: RepoDir
            if repo.commit_date_newer():
                self.log(f"Repo has updated: {repo.repoid}")
                found = True

        return found

    def read_authors(self, authorrepos: dict) -> dict:
        "Read all authors"

        ret_authors = dict()  # nickname -> author_meta_dict
        for repoid, authorrepo in authorrepos.items():  # type: str, RepoDir
            files = authorrepo.files
            meta = files.get(AUTHORMETA_FILE)
            if meta is None:
                self.warn(f"There is no author's meta file '{AUTHORMETA_FILE}' in repo {repoid}.")
                continue

            # Load meta info of author
            self.log(f"Processing meta of author {repoid}.")
            headers, content = MDFileParser(meta)

            # Save author's content
            headers["content"] = markdown.markdown(content)
            for path, file in files.items():  # type: str, Path
                m = is_author_lang_content.search(path)
                if m:
                    self.log(f"Parsing {path}")
                    lang = m.group(1)
                    headers[f"content/{lang}"] = markdown.markdown(file.read_text(encoding="UTF-8"))

            headers.update(AUTHORMETA_BASEDICT)

            # Append author
            ret_authors[headers["nickname"]] = headers

        return ret_authors

    def read_contents(self, authors: dict, authorrepos: dict) -> dict:
        "Read all contents of authors"

        ret_contents = dict()  # path
        for repoid, authorrepo in authorrepos.items():  # type: str, RepoDir
            for fpath, file in authorrepo.files.items():  # type: str, Path
                m = is_content_lang_md.search(fpath)
                if m:
                    self.log(f"Reading content of: {fpath}")
                    headers, content = MDFileParser(file)

                    path = m.group(1)
                    lang = m.group(2)

                    # ret_contents[]

                else:
                    self.log(f"Skipping content of: {fpath}")

        return ret_contents

    def generate(self, repos: dict, onlywhenchanged: bool = False):
        """
        Generate all content from authors and templates
        :param repos:
            dict["AUTHORS"/"TEMPLATES"] -> dict[repoid] -> RepoDir
        :param onlywhenchanged:
            Exit if no repos pulls have changed.
        :return:
        """

        if onlywhenchanged:
            if not self.need_regenerate([repo for repo in [repoclass for repoclass in repos.values()]]):
                return

        authors = self.read_authors(repos["AUTHORS"])
        contents = self.read_contents(authors, repos["AUTHORS"])

        # Store each repo date as last processed date.
        for typename, repodict in repos.items():
            for repoid, repo in repodict.items():
                repo.store_process_date()
