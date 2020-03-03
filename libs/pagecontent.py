from typing import Tuple, Dict, Union
from pathlib import Path
import re
import datetime
import traceback
import shutil
from config import Config
from libs.content import TemplateModels
from libs.dirtools import DirFiles
from libs.repo import RepoDir
from libs.fileparser import parse_md_file
from libs.setofmutable import SetOfMutable
from libs.streamlogging import Logger


def _copy(self: Path, target: Path) -> Union[Path, None]:
    if not self.is_file():
        return None

    return Path(shutil.copy(str(self), str(target)))


# Append copy function for Files in Path-Objects
Path.copy = _copy


AUTHORMETA_FILE = "author/meta.md"

is_author_lang_content = re.compile(r"^author/([a-z]{2})\.md$")
is_content_id_lang_md = re.compile(r"^content/(.*)\.([a-z]{2})\.md$")
is_directory_lang_md = re.compile(r"^content/?(.*)/([a-z]{2})\.md$")
is_md = re.compile(r"^content/.*\.md$")
is_valid_single_lang = re.compile(r"^[a-z]{2}$")

# Authors need at least these meta headers
required_author_meta_keys = {"nickname", "contentgrant"}

# Predefined meta headers will be removed
reserved_author_meta_keys = {"contents", "langs", "gitsources"}

# Content need at least these meta headers
required_content_keys = {"title", "date", "description"}

# Predefined meta headers will be removed
reserved_content_keys = {"lang", "langs", "otherlangs", "gitsource", "mdsource", "author", "url",
                         "id", "links", "file", "files"}


def _getcreate_subdict(dictcollection: dict, key: str, garbage: list) -> dict:
    if key in dictcollection:
        return dictcollection[key]

    d = dictcollection[key] = dict()
    garbage.append(d)
    return d


class PageContent:
    def __init__(self, config: Config, pageconfig, logger: Logger = None):
        self.config = config
        self.pageconfig = pageconfig
        self.log = logger

    def need_regenerate(self, repolist: list) -> bool:
        found = False

        self.log.out("Checking if sources have updated...")
        for repo in repolist:  # type: RepoDir
            if repo.commit_date_newer():
                self.log.out(f"Repo has updated: {repo.repoid}")
                found = True

        return found

    def check_authormeta(self, authormeta: dict) -> bool:
        """
        Check author meta for reserved keys, warn and remove them.
        Warns about missing required keys and then returns False
        Returns True, if all required keys were found.
        """
        keys = authormeta.keys()
        reserved = reserved_author_meta_keys.intersection(keys)
        missing = required_author_meta_keys.difference(keys)

        for metakey in reserved:
            self.log.warn(f"Author meta contains a reserved meta key: {metakey}. It will be removed or overwritten.")
            del(authormeta[metakey])

        for metakey in missing:
            self.log.warn(f"Author meta missing required meta key: {metakey}.")

        return len(missing) == 0

    def check_contentmeta(self, contentmeta: dict) -> bool:
        """
        Check content for reserved keys, warn and remove them.
        Warns about missing required keys and then returns False
        Returns True, if all required keys were found.
        """
        keys = contentmeta.keys()
        reserved = reserved_content_keys.intersection(keys)
        missing = required_content_keys.difference(keys)

        for metakey in reserved:
            self.log.warn(f"Content meta contains a reserved meta key: {metakey}. It will be removed or overwritten.")
            contentmeta.pop(metakey)

        for metakey in missing:
            self.log.err(f"Required content meta key missing: '{metakey}'.")

        return len(missing) == 0

    def _addmerge(self, thingid: str, contentl: dict, collectionl: dict, namespace: str):
        if thingid in collectionl:
            # Thingid already present in some language
            thingcol: dict = collectionl[thingid]
        else:
            # Create thing initially in this language
            thingcol = collectionl[thingid] = dict()

        for lang, content in contentl.items():  # type: str, dict
            if lang in thingcol:
                self.log.warn(f"Duplicate content collision for language: '{lang}', id: '{thingid}',"
                              f" namespace: {namespace}. Content will be skipped.")
                continue

            # Add language with content
            thingcol[lang] = content

    def read_authors_with_contents(self, authorrepos: dict) -> Tuple[dict, list]:
        """Read all authors
        Better deep destroy the result after elements are not used anymore anywhere.
        """
        ret_repos = dict()  # repoid -> author_meta_dict, contents, gitsource

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

            # ### By manipulating the mechanism of contentgrant you violate personal copy rights.                 ###
            # ### Authors may enforce legal steps against you, if you use their content without their permission. ###
            # Check grant of contents
            grant = authormeta.get("contentgrant", NotImplemented)
            if grant is NotImplemented:
                self.log.warn(f"Skipping repo {repoid} because missing contentgrant header in {AUTHORMETA_FILE}.")
                continue

            if grant is None:
                self.log.warn(f"Skipping repo {repoid} because not granted to this website.")
                continue

            if isinstance(grant, str):
                authormeta["contentgrant"] = grant = [page.strip() for page in grant.split(",")]

            if "*" not in grant and self.pageconfig.PAGEID not in grant:
                self.log.warn(f"This page is not allowed to use content from git repository configured as {repoid}. "
                              "Content of author skipped.")
                continue
            # ### End of contentgrant ###

            # We're allowed to use author's contents!

            # Sanity checks
            if not self.check_authormeta(authormeta):
                self.log.warn(f"Skipping repo {repoid} because some required header missing in {AUTHORMETA_FILE}.")

            # Collect author's self descriptions
            _getcreate_subdict(authormeta, "content", garbage)  # dict of lang

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

                # Merge check main description of author
                self._addmerge("content", {mainlang: content.strip()}, authormeta,
                               f"repo[{repoid}]/{AUTHORMETA_FILE}:content")

            # Check additional author descriptions
            for path, file in files.items():  # type: str, Path
                m = is_author_lang_content.search(path)
                if m:
                    self.log.out(f"Parsing author description in {path}")
                    lang = m.group(1)
                    self._addmerge("content",
                                   {lang: file.read_text(encoding="UTF-8")},
                                   authormeta,
                                   f"repo[{repoid}]/{path} (lang={lang})"
                                   )

            # Read author repo's contents
            contentsl, contentgarbage = self.read_contents(authorrepo)
            garbage.extend(contentgarbage)
            garbage.append(authormeta)

            # Append meta and content to repo collection
            ret_repos[repoid] = authormeta, contentsl, authorrepo.origin

        return ret_repos, garbage

    def replace_headers_basic_inplace(self, headers: dict) -> bool:
        # ### Publish ###
        if "publish" not in headers:
            headers["publish"] = True  # Default

        publish = headers["publish"]

        if type(publish) is bool:
            if not publish:
                return False

        if type(publish) in (datetime.datetime, datetime.date):
            if datetime.datetime.now() <= publish:
                self.log.out(f"Publish date not yet reached: ({publish})")
                return False

        if type(publish) is str:
            if publish.strip().lower() == "hidden":
                headers["publish"] = NotImplemented
            else:
                self.log.warn(f"Unrecognized value for meta key 'publish': '{publish}'")
                return False

        # ### Tags ###
        tags = headers.get("tags", self.pageconfig.CONTENT_SETTINGS.get("TAG_DEFAULT", {""}))

        if tags is None:
            tags = {""}
        elif type(tags) is str:
            tags = tags.strip()
            if len(tags) == 0:
                tags = {""}
            else:
                tags = {tag.strip() for tag in tags.split(",") if len(tag.strip())}
                if len(tags) == 0:
                    tags = {""}
        elif type(tags) in (dict, set):
            if len(tags) == 0:
                tags = {""}
            else:
                tags = set(tags)
        else:
            tags = str(tags)
            self.log.warn(f"Unrecognized value for meta key 'tags': '{tags}'")
            return False

        headers["tags"] = tags

        # Linkto, linkwith, sources
        def check_header_links(key: str):
            # Replace string header in set of contentids
            if key not in headers:
                return

            links_str = headers[key]
            headers[key] = {link.strip() for link in links_str.split(",") if len(link.strip())}

        check_header_links("linkto")
        check_header_links("linkwith")
        check_header_links("sources")

        return True

    def read_contents(self, authorrepo: RepoDir) -> Tuple[dict, list]:  # of contentid
        "Read all contents of an author repo"

        ret_contentsl = dict()  # path -> dict of lang -> content

        # Collect all lists and dicts containing references to other objects
        garbage = list()

        files = authorrepo.files

        uselinking = self.pageconfig.FEATURES.get("content:linking", True)
        do_copyfiles = self.pageconfig.FEATURES.get("files:copy:other", True)
        do_copyfile = self.pageconfig.FEATURES.get("files:copy:md", False)

        def contentlang(path: str):
            # Try match content/*.lang.md files
            match = is_content_id_lang_md.search(path)
            if not match:
                # Try match content/*/lang.md files
                match = is_directory_lang_md.search(path)
            return match

        for fpath, file in files.items():  # type: str, Path
            # Try match content/*.md files
            if not is_md.match(fpath):
                continue

            m = contentlang(fpath)
            if not m:
                self.log.warn(f"Skipping content of {fpath} because file does not match naming requirements.")
                continue

            # File path matched one of both patterns
            self.log.out(f"Reading content of: {fpath}")
            headers, content = parse_md_file(file)
            garbage.append(headers)
            contentid = m.group(1)

            # TODO urlencode contentid here

            lang = m.group(2)

            # Sanity checks
            if not self.check_contentmeta(headers):
                self.log.warn(f"Skipping content of {fpath} because some required meta keys are missing.")
                continue

            # Create repo related dynamic headers
            headers["gitsource"] = authorrepo.origin
            headers["mdsource"] = fpath
            headers["lang"] = lang
            headers["id"] = contentid

            if uselinking:
                headers["links"] = SetOfMutable()  # to add unhashable dicts to a set by id.
                garbage.append(headers["links"])

            if do_copyfiles:
                # Track all files in same folder except content files
                parentfolder = file.parent
                headers["files"] = set(f for f in parentfolder.iterdir() if f.is_file() and not contentlang(str(f.relative_to(authorrepo.path))))

            if do_copyfile:
                # Sourcefile itself
                headers["file"] = file

            # Early basic header analysis and translations
            if not self.replace_headers_basic_inplace(headers):
                self.log.out(f"Skipping content file: {fpath} because of any meta check.")
                continue

            # Check for exactly one content source in file
            if "content" in headers:
                if len(content.strip()):
                    self.log.warn(f"Skipping content file: {fpath} having both content in body and in content header.")
                    continue
            else:
                if len(content.strip()) == 0:
                    self.log.warn(f"Skipping content file: {fpath}. Missing content.")
                    continue

                # Add content to headers.content
                headers["content"] = content.strip()

            # Merge into return subset
            self._addmerge(contentid, {lang: headers}, ret_contentsl, f"read_contents file: '{fpath}' lang: {lang}")

        garbage.append(ret_contentsl)
        return ret_contentsl, garbage

    def apply_datetime_formats(self, dt: datetime) -> Dict[str, str]:
        dtf = self.config.DATETIME_FORMATS.copy()
        dtf.update(self.pageconfig.DATETIME_FORMATS)
        return {code: dt.strftime(dtstr) for code, dtstr in dtf.items()}

    def create_global_page_struct(self, raw_repos: dict) -> Tuple[dict, list]:
        # Collect all lists and dicts containing references to other objects
        garbage = list()

        # Global variables
        if "GLOBAL_STRINGS" in self.pageconfig.CONTENT_SETTINGS:
            ret_merged = self.pageconfig.CONTENT_SETTINGS["GLOBAL_STRINGS"].copy()
        else:
            ret_merged = dict()

        # ### Collect these global variables:
        # 1.
        global_authors = _getcreate_subdict(ret_merged, "authors", garbage)  # {nickname: author}

        # 1.a: author["contents"]

        # 2.
        global_contentsl = _getcreate_subdict(ret_merged, "contents", garbage)  # {contentid: {lang: [contents]} }

        # 3.
        global_tagsl = _getcreate_subdict(ret_merged, "tags", garbage)  # {tagname: {contentid: {lang: [contents]} } }

        # 4.
        # Structure not perfect but uniform
        global_langsl = _getcreate_subdict(ret_merged, "langs", garbage)  # {lang: {contentid: {lang: [contents]} } }

        # 5.
        ret_merged["generationtime"] = self.apply_datetime_formats(datetime.datetime.now())

        # Iterate through all repos
        for repoid, raw_repo in raw_repos.items():  # type: str, dict
            # Process author and contents of one repo
            raw_author, raw_contentsl, raw_gitsource = raw_repo  # type: dict, dict, str

            # ### Nickname/author related ###
            #
            # Merge by nickname
            author_nickname = raw_author["nickname"]  # (1.)

            # Check already having author by nickname (1.)
            if author_nickname in global_authors:
                # Another repo of same author. No problem!
                author: dict = global_authors[author_nickname]
                gitsources: set = author["gitsources"]
                # TODO: check for varying meta tags in raw_author
            else:
                # First author occurrence. Take raw meta.
                author = global_authors[author_nickname] = raw_author
                gitsources = author["gitsources"] = set()

            # Collect gitsource
            gitsources.add(raw_gitsource)

            # ### Content related ###
            #
            # Check contents list of author (1.a)
            author_contentsl = _getcreate_subdict(author, "contents", garbage)

            # Iterate raw repo contents of author and merge globally
            for contentid, raw_contentl in raw_contentsl.items():  # type: str, dict
                # Iterate unmerged repo content

                # (1.a)
                self._addmerge(contentid, raw_contentl, author_contentsl, f"author[{author_nickname}].contents")

                # (2.)
                self._addmerge(contentid, raw_contentl, global_contentsl, "contents")

                # Different languages may have different or localized tags
                for lang, raw_content in raw_contentl.items():  # type: str, dict
                    contentl = {lang: raw_content}

                    # (3.)
                    tags: set = raw_content["tags"]
                    for tag in tags:  # type: str
                        tagl = _getcreate_subdict(global_tagsl, tag, garbage)
                        self._addmerge(contentid, contentl, tagl, f"tags[{tag}]")

                    # (4.)
                    langl = _getcreate_subdict(global_langsl, lang, garbage)
                    self._addmerge(contentid, contentl, langl, f"langs[{lang}]")

        return ret_merged, garbage

    def link_contents(self, namespace: dict) -> list:
        """
        Modify content headers:
            linkto -> links
            linkwith -> links
            langs
            otherlangs
        """

        # Collect all lists and dicts containing references to other objects
        garbage = list()
        contentsl: dict = namespace["contents"]

        deflang = self.pageconfig.CONTENT_SETTINGS["LANG_DEFAULT"]
        uselinking = self.pageconfig.FEATURES.get("content:linking", True)

        def get_linked_content(headerkey: str, c: dict) -> Union[dict, None]:
            if headerkey not in c:
                # Header not present
                return None

            cid = c["id"]
            clang = c["lang"]

            for link in c[headerkey]:  # type: str
                if link == cid:
                    self.log.warn(f"Selflinking: Header {headerkey} of content '{cid}'"
                                  f" in language '{clang}' points to itself. Skipped.")
                    continue

                # Link valid?
                if link not in contentsl:
                    self.log.warn(f"Unknown contentid: Header {headerkey} of content '{cid}'"
                                  f" in language {clang} points to unknown contentid: '{link}'. Skipped.")
                    continue

                # Get best language
                destcontentl: dict = contentsl[link]
                if clang in destcontentl:
                    # Found same language
                    return destcontentl[lang]

                if deflang in destcontentl:
                    # Fallback: Found content in deflang
                    self.log.warn(f"Crosslanguage: Header {headerkey} of content '{cid}' in language '{clang}'"
                                  f" points to default language: '{deflang}'.")
                    return destcontentl[deflang]

                if len(destcontentl):
                    # Get first language.
                    firstlang, destcontent = next(iter(destcontentl.items()))
                    self.log.warn(f"Crosslanguage: Header {headerkey} of content '{cid}' in language '{clang}'"
                                  f" points to first found language: '{firstlang}'.")
                    return destcontent

                self.log.warn(f"Invalid link: Header {headerkey} of content '{cid}'"
                              f" in language '{clang}' does not match any contents.")
                return None

        for contentid, contentl in contentsl.items():  # type: str, dict
            for lang, content in contentl.items():  # type: str, dict
                if uselinking:
                    # Linkto
                    linkcontent = get_linked_content("linkto", content)
                    if linkcontent is not None:
                        content["links"].add(linkcontent)

                    # Linkwith
                    linkcontent = get_linked_content("linkwith", content)
                    if linkcontent is not None:
                        content["links"].add(linkcontent)
                        linkcontent["links"].add(content)

                # langs
                content["langs"] = contentl

                # otherlangs
                otherlangs = content["otherlangs"] = {lang: c for lang, c in contentl.items() if c is not content}
                if len(otherlangs):
                    garbage.append(otherlangs)

        return garbage

    def write_global_page_struct(self, struct, webroot: Path, templates: dict) -> dict:
        deflang = self.pageconfig.CONTENT_SETTINGS.get("LANG_DEFAULT", "en")
        index_only = self.pageconfig.CONTENT_SETTINGS.get("INDEX_ONLY", False)
        index_file = self.pageconfig.CONTENT_SETTINGS.get("INDEX_FILE", "index.html")
        file_extension = self.pageconfig.CONTENT_SETTINGS.get("CONTENT_FILE_EXTENSION", ".html")
        default_template = self.pageconfig.CONTENT_SETTINGS.get("TEMPLATE_DEFAULT", None)

        useauthors = self.pageconfig.FEATURES.get("content:authors", True)
        uselinking = self.pageconfig.FEATURES.get("content:linking", True)
        do_copyfiles = self.pageconfig.FEATURES.get("files:copy:other", True)
        do_copyfile = self.pageconfig.FEATURES.get("files:copy:md", False)
        use_tags = self.pageconfig.FEATURES.get("content:tags", True)

        # Track all touched files
        touched_files = dict()

        def get_folder_file_url(cid: str, clang: str):
            "Determine folder, create it if needed, propose filename and url"

            def createfolder(cfolder: Path, depth=0):
                if str(cfolder) not in touched_files:
                    relfolder = cfolder.relative_to(webroot)
                    if relfolder.name:
                        touched_files[str(relfolder)] = cfolder

                if cfolder.is_dir():
                    # Folder already exists. All fine.
                    return

                if depth>16:
                    self.log.err(f"Reached maxdepth while creating parent folders: {cfolder}")
                    return

                if cfolder.exists():
                    self.log.err(f"Directory could not be created. Element already on disk: {cfolder}")
                    return

                parent = cfolder.parent
                createfolder(parent, depth+1)

                # Create this folder
                cfolder.mkdir()

            if index_only:
                # python/learn/index.html
                # python/learn/en/index.html
                if not clang or clang == deflang:
                    rfolder = webroot / cid
                    rurl =
                else:
                    rfolder = webroot / cid / clang
                rfile = rfolder / index_file

            else:
                # python/learn.html
                # python/learn-en.html
                vfolder = webroot / cid
                rfolder = vfolder.parent
                fname = vfolder.name

                if not clang or clang == deflang:
                    rfile = rfolder / f"{fname}{file_extension}"
                else:
                    rfile = rfolder / f"{fname}-{clang}{file_extension}"

            if not clang:
                # No changes, just an informational request
                return rfolder, rfile

            if str(rfolder) not in touched_files:
                createfolder(rfolder)
            relfile = rfile.relative_to(webroot)

            fileid = str(relfile)
            if fileid in touched_files:
                self.log.err(f"File collision at '{fileid}'. Content will be overwritten.")
            else:
                touched_files[fileid] = rfile

            return rfolder, rfile, rurl

        def copy(cfiles: set, destfolder: Path):
            for cfile in cfiles:  # type: Path
                newdest = cfile.copy(destfolder)
                newid = str(newdest.relative_to(webroot))
                touched_files[newid] = newdest

        models = TemplateModels(templates, default_template)

        # Write contents
        contentsl = struct["contents"]
        for contentid, contentl in contentsl.items():  # type: str, dict
            if not index_only:
                # Files share same folder. Collect all of each language.
                files_to_copy = set()

            for lang, content in contentl.items():  # type: str, dict
                folder, file, url = get_folder_file_url(contentid, lang)

                # Remember url
                content["url"] = url

                # Add current content to namespace
                struct["content"] = content

                # Generate html
                html = models.translate_content(struct, "content")
                file.write_text(html, encoding="UTF-8", errors="xmlcharrefreplace")

                # Collect other source files
                if index_only:
                    files_to_copy = set()

                if do_copyfiles:
                    files_to_copy.update(content["files"])
                if do_copyfile:
                    files_to_copy.add(content["file"])

                if index_only:
                    # Copy to own folder (duplicates possible)
                    copy(files_to_copy, folder)

            if not index_only and files_to_copy:
                commonfolder, _ = get_folder_file(contentid, "")
                copy(files_to_copy, commonfolder)

        return touched_files

    def get_orphan_files(self, root: Path, files_before: dict, files_touched: dict) -> dict:
        "Determine old files or folders not used anymore"

        before = set(files_before)
        touched = set(files_touched)
        orphans = before.difference(touched)

        return {orphan: files_before[orphan] for orphan in orphans}

    def delete_files(self, itemlist: dict):
        "Determine old files or folders not used anymore and delete them"

        log = self.log.sublogger("DELETEOLD")

        def rm_dir(folder: Path):
            log.out(f"Folder: {folder}")
            for element in folder.iterdir():
                if element.is_dir():
                    rm_dir(element)
                if element.is_file():
                    log.out(f"File: {element}")
                    element.unlink(missing_ok=True)
            folder.rmdir()

        for orphan in itemlist.values():  # type: Path
            if orphan.is_file():
                log.out(f"File: {orphan}")
                orphan.unlink(missing_ok=True)
            if orphan.is_dir():
                rm_dir(orphan)

    def generate(self, repos: dict, onlywhenchanged: bool = False):
        """
        Generate all content from authors and templates
        :param repos:
            dict["AUTHORS"/"TEMPLATES"] -> dict[repoid] -> RepoDir
        :param onlywhenchanged:
            Exit if no repos pulls have changed.
        :return:
        """
        garbage = list()

        try:
            if onlywhenchanged:
                if not self.need_regenerate([repo for repodict in repos.values() for repo in repodict.values()]):
                    self.log.out("No changed repositories found. No regeneration needed. Content should be up to date.")
                    return

            # Read all authors and their contents.
            raw_author_and_contents_struct, authorcontentgarbage = self.read_authors_with_contents(repos["AUTHORS"])
            garbage.extend(authorcontentgarbage)

            # Merge all authors and contents into a single global namespace
            global_page_struct, basegarbage = self.create_global_page_struct(raw_author_and_contents_struct)
            garbage.extend(basegarbage)

            # Link contents
            linkgarbage = self.link_contents(global_page_struct)
            garbage.extend(linkgarbage)

            # ### WEBROOT access ###
            writedir = self.pageconfig.WEBROOT
            if not writedir.is_dir():
                self.log.err(f"Destination folder configured in pageconfig.WEBROOT as '{writedir}'"
                             f" is missing. Create it with correct permissions first.")
                raise FileNotFoundError("Folder WEBROOT not existing.")

            # Remember old files
            webroot = DirFiles(writedir)
            files_before = webroot.to_dict(10, with_folders=True, with_files=True, hidden_files=True, hidden_folders=True)

            # Update files on disk
            touched_files = self.write_global_page_struct(global_page_struct, webroot.path, repos["TEMPLATES"])

            #from pprint import pprint
            #structfile: Path = self.pageconfig.ROOT / "struct.txt"
            #with open(str(structfile), "w") as sf:
            #    pprint(global_page_struct, width=200, depth=4, stream=sf)

            # Delete old files
            delete_files = self.get_orphan_files(webroot.path, files_before, touched_files)
            self.delete_files(delete_files)

            # Create file index?
            fileindex = self.pageconfig.FEATURES.get("generate:fileindex", None)
            if isinstance(fileindex, Path):
                if not fileindex.is_absolute():
                    fileindex = self.pageconfig.ROOT / fileindex

                with open(str(fileindex), "w") as fi:
                    fi.write("File index of generation")

                    fi.write("\n\nTouched files:\n")
                    for file in touched_files:
                        fi.write(f"  {file}\n")

                    fi.write("\n\nDeleted files:\n")
                    for file in delete_files:
                        fi.write(f"  {file}\n")

        except Exception as err:
            self.log.err(traceback.format_exc())
            for earg in err.args:
                self.log.err(earg)

        finally:
            # ### Finish ###
            # Now safe destroy garbage contents
            for element in garbage:
                element.clear()
            garbage.clear()

        # Store each repo date as last processed date.
        for typename, repodict in repos.items():
            for repoid, repo in repodict.items():
                repo.store_process_date()
