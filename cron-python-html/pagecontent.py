import markdown
from repo import RepoDir
from fileparser import MDFileParser
from pathlib import Path
from config.config import Config
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
AUTHORCONTENT_FOLDER = "content"

is_author_lang_content = re.compile(r"^author/([a-z]{2})\.md$")
is_content_id_lang_md = re.compile(r"^content/(.*)\.([a-z]{2})\.md$")
is_directory_lang_md = re.compile(r"^content/?(.*)/([a-z]{2})\.md$")
is_md = re.compile(r"^content/.*\.md$")


class PageContent:
    def __init__(self, config: Config, pageconfig, stdout=None):
        self.config = config
        self.pageconfig = pageconfig
        self.writefolder = Path(self.pageconfig.WEBROOT)
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

    def read_authors_with_contents(self, authorrepos: dict) -> dict:
        "Read all authors"

        ret_repos = dict()  # repoid -> author_meta_dict
        for repoid, authorrepo in authorrepos.items():  # type: str, RepoDir
            files = authorrepo.files
            meta = files.get(AUTHORMETA_FILE)
            if meta is None:
                self.warn(f"There is no author's meta file '{AUTHORMETA_FILE}' in repo {repoid}.")
                continue

            # Load meta info of author
            self.log(f"Processing meta of author {repoid}.")
            authormeta, content = MDFileParser(meta)

            # ### By manipulating the mechanism of contentgrant you violate personal copy rights.                 ###
            # ### Authors may enforce legal steps against you, if you use their content without their permission. ###
            # Check grant of contents
            grant = authormeta.get("contentgrant", NotImplemented)
            if grant is NotImplemented:
                self.warn(f"Skipping author repo {repoid} because missing contentgrant header in meta.md.")
                continue

            if grant is None or grant == "":
                self.warn(f"Skipping author repo {repoid} because not granted to this website.")
                continue

            if grant != "*" and self.pageconfig.PAGEID not in (page.strip() for page in grant.split(",")):
                self.warn(f"This page is not allowed to use content from git repository configured as {repoid}. Content skipped.")
                continue

            # ### End of contentgrant ###

            # Save author's self descriptions
            langcontents = authormeta["content"] = dict()  # dict of lang

            # Check content of meta.md
            if len(content.strip()):
                mainlang = authormeta.get("lang", self.pageconfig.CONTENT_SETTINGS.get("LANG_DEFAULT", NotImplemented))
                if mainlang is NotImplemented:
                    self.warn(f"Skipping repo {repoid} because could not determine language neither from header nor from LANG_DEFAULT.")
                    continue

                langcontents[mainlang] = content.strip()

            # Check additional author descriptions
            for path, file in files.items():  # type: str, Path
                m = is_author_lang_content.search(path)
                if m:
                    self.log(f"Parsing author description in {path}")
                    lang = m.group(1)
                    langcontents[lang] = file.read_text(encoding="UTF-8")

            # Read author repo's contents
            authormeta["contents"] = self.read_contents(authorrepo)

            # Append repo to author meta collection
            ret_repos[repoid] = authormeta

        return ret_repos

    def read_contents(self, authorrepo: RepoDir) -> dict:  # of contentid
        "Read all contents of an author repo"

        ret_contents = dict()  # path -> dict of lang -> content
        files = authorrepo.files

        for fpath, file in files.items():  # type: str, Path
            # Try match content/*.md files
            if is_md.match(fpath):
                # Try match content/*.lang.md files
                m = is_content_id_lang_md.search(fpath)
                if not m:
                    # Try match content/*/lang.md files
                    m = is_directory_lang_md.search(fpath)

                if m:
                    # File path matched one of both patterns
                    self.log(f"Reading content of: {fpath}")
                    headers, content = MDFileParser(file)
                    contentid = m.group(1)
                    lang = m.group(2)

                    # contents[path] -> dict[lang] -> content
                    if contentid in ret_contents:
                        # There's already at least one content file in an other language
                        contentlangs = ret_contents[contentid]
                    else:
                        # First content
                        contentlangs = ret_contents[contentid] = dict()

                    if lang in contentlangs:
                        self.warn(f"Skipping duplicate content file: {fpath} -> contentid={contentid}, lang={lang}")
                        continue

                    if "content" in headers and len(content.strip()):
                        self.warn(f"Skipping content file: {fpath} having both content in body and in content header.")
                        continue

                    if "content" not in headers and len(content.strip()) == 0:
                        self.warn(f"Skipping content file: {fpath}. Missing content.")
                        continue

                    if "content" not in headers:
                        # Add body to content
                        headers["content"] = content

                    # Create dynamic headers
                    headers["lang"] = lang
                    headers["gitsource"] = authorrepo.origin
                    headers["mdsource"] = fpath

                    # Assign content to contents[contentid][lang]
                    contentlangs[lang] = headers

                else:
                    self.log(f"Skipping content of {fpath} because md file not matching requirements.")

        return ret_contents

    def mergecontents(self):
        # Checks
        if "nickname" not in authormeta:
            self.warn(f"Missing nickname in {repoid}. Content of author skipped.")
            continue

        nickname = authormeta["nickname"]


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

        #
        authorcontentstruct = self.read_authors_with_contents(repos["AUTHORS"])





        # Store each repo date as last processed date.
        for typename, repodict in repos.items():
            for repoid, repo in repodict.items():
                repo.store_process_date()
