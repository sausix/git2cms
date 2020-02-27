from typing import Tuple
from pathlib import Path
import re
import markdown
import datetime
from config.config import Config
from repo import RepoDir
from fileparser import parse_md_file
from streamlogging import Logger

AUTHORMETA_FILE = "author/meta.md"
is_author_lang_content = re.compile(r"^author/([a-z]{2})\.md$")
is_content_id_lang_md = re.compile(r"^content/(.*)\.([a-z]{2})\.md$")
is_directory_lang_md = re.compile(r"^content/?(.*)/([a-z]{2})\.md$")
is_md = re.compile(r"^content/.*\.md$")
is_valid_single_lang = re.compile(r"^[a-z]{2}$")


class PageContent:
    def __init__(self, config: Config, pageconfig, logger: Logger = None):
        self.config = config
        self.pageconfig = pageconfig
        self.writefolder = Path(self.pageconfig.WEBROOT)
        self.log = logger

    def need_regenerate(self, repolist: list) -> bool:
        found = False

        self.log.out("Checking if sources have updated...")
        for repo in repolist:  # type: RepoDir
            if repo.commit_date_newer():
                self.log.out(f"Repo has updated: {repo.repoid}")
                found = True

        return found

    def read_authors_with_contents(self, authorrepos: dict) -> Tuple[dict, list]:
        """Read all authors
        Better deep destroy the result after elements are not used anymore anywhere.
        """
        ret_repos = dict()  # repoid -> author_meta_dict

        # Collect all lists and dicts containing references to other objects
        garbage = list()

        for repoid, authorrepo in authorrepos.items():  # type: str, RepoDir
            files = authorrepo.files
            meta = files.get(AUTHORMETA_FILE)
            if meta is None:
                self.log.warn(f"There is no author's meta file '{AUTHORMETA_FILE}' in repo {repoid}. Skipping.")
                continue

            # Load meta info of author
            self.log.out(f"Processing meta of author {repoid}.")
            authormeta, content = parse_md_file(meta)
            garbage.append(authormeta)

            # ### By manipulating the mechanism of contentgrant you violate personal copy rights.                 ###
            # ### Authors may enforce legal steps against you, if you use their content without their permission. ###
            # Check grant of contents
            grant = authormeta.get("contentgrant", NotImplemented)
            if grant is NotImplemented:
                self.log.warn(f"Skipping author repo {repoid} because missing contentgrant header in meta.md.")
                continue

            if grant is None:
                self.log.warn(f"Skipping author repo {repoid} because not granted to this website.")
                continue

            if isinstance(grant, str):
                authormeta["contentgrant"] = grant = [page.strip() for page in grant.split(",")]

            if "*" not in grant and self.pageconfig.PAGEID not in grant:
                self.log.warn(f"This page is not allowed to use content from git repository configured as {repoid}. "
                              "Content of author skipped.")
                continue
            # ### End of contentgrant ###

            # Save author's self descriptions
            langcontents = authormeta["content"] = dict()  # dict of lang
            garbage.append(langcontents)

            # Check content of meta.md
            if len(content.strip()):
                mainlang = authormeta.get("lang", self.pageconfig.CONTENT_SETTINGS.get("LANG_DEFAULT", NotImplemented))
                if mainlang is NotImplemented:
                    self.log.warn(f"Skipping repo {repoid} because could not determine language neither from header "
                                  "nor from LANG_DEFAULT.")
                    continue

                if not is_valid_single_lang.match(mainlang.strip()):
                    self.log.warn(f"Skipping repo {repoid} because not a valid single language code aquired neither "
                                  f"from header nor from LANG_DEFAULT: '{mainlang}'")
                    continue

                langcontents[mainlang] = content.strip()

            # Check additional author descriptions
            for path, file in files.items():  # type: str, Path
                m = is_author_lang_content.search(path)
                if m:
                    self.log.out(f"Parsing author description in {path}")
                    lang = m.group(1)
                    langcontents[lang] = file.read_text(encoding="UTF-8")

            # Read author repo's contents
            contents, contentgarbage = self.read_contents(authorrepo)
            garbage.append(contents)
            garbage.extend(contentgarbage)

            # Link author's contents
            authormeta["contents"] = contents

            # Append repo to author meta collection
            ret_repos[repoid] = authormeta

        return ret_repos, garbage

    def read_contents(self, authorrepo: RepoDir) -> Tuple[dict, list]:  # of contentid
        "Read all contents of an author repo"

        ret_contents = dict()  # path -> dict of lang -> content

        # Collect all lists and dicts containing references to other objects
        garbage = list()

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
                    self.log.out(f"Reading content of: {fpath}")
                    headers, content = parse_md_file(file)
                    garbage.append(headers)
                    contentid = m.group(1)
                    lang = m.group(2)

                    # contents[path] -> dict[lang] -> content
                    if contentid in ret_contents:
                        # There's already at least one content file in an other language
                        contentlangs = ret_contents[contentid]
                    else:
                        # First content
                        contentlangs = ret_contents[contentid] = dict()
                        garbage.append(contentlangs)

                    if lang in contentlangs:
                        self.log.warn(f"Skipping duplicate content file: {fpath} -> contentid={contentid}, lang={lang}")
                        continue

                    if "content" in headers and len(content.strip()):
                        self.log.warn(f"Skipping content file: {fpath} having both content in body and in content header.")
                        continue

                    if "content" not in headers and len(content.strip()) == 0:
                        self.log.warn(f"Skipping content file: {fpath}. Missing content.")
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
                    self.log.warn(f"Skipping content of {fpath} because md file not matching requirements.")

        return ret_contents, garbage

    def create_time_aliases(self, time: datetime) -> dict:
        dtf = self.config.DATETIME_FORMATS.copy()
        dtf.update(self.pageconfig.DATETIME_FORMATS)
        return {code: time.strftime(dtstr) for code, dtstr in dtf.items()}

    def create_global_page_struct(self, authorcontents: dict) -> Tuple[dict, list]:
        # Collect all lists and dicts containing references to other objects
        garbage = list()

        # Global variables
        if "GLOBAL_STRINGS" in self.pageconfig.CONTENT_SETTINGS:
            ret_merged = self.pageconfig.CONTENT_SETTINGS["GLOBAL_STRINGS"].copy()
        else:
            ret_merged = dict()

        authors = dict()  # {nickname: author}
        contents = dict()  # {pageid: {lang: [contents]} }
        tags = dict()  # {tagname: {lang: [contents]} }
        langs = dict()  # {lang: [contents] }

        ret_merged["authors"] = authors
        ret_merged["contents"] = contents
        ret_merged["tags"] = tags
        ret_merged["langs"] = langs
        ret_merged["generationtime"] = self.create_time_aliases(datetime.datetime.now())

        for item in ret_merged.values():
            garbage.append(item)

        # Iterate through all contents
        for repoid, author_meta_dict in authorcontents.items():
            pass


        # Checks
        #if "nickname" not in authormeta:
        #    self.warn(f"Missing nickname in {repoid}. Content of author skipped.")
        #    continue

        #nickname = authormeta["nickname"]
        return ret_merged, garbage

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

        # Read all authors and their contents.
        authorcontentstruct, garbage = self.read_authors_with_contents(repos["AUTHORS"])

        # Merge all authors, link contents, collect tags
        allcontents, linkedgarbage = self.create_global_page_struct(authorcontentstruct)
        garbage.extend(linkedgarbage)

        # Now safe destroy garbage contents
        for element in garbage:
            element.clear()
        garbage.clear()

        # Store each repo date as last processed date.
        for typename, repodict in repos.items():
            for repoid, repo in repodict.items():
                repo.store_process_date()
