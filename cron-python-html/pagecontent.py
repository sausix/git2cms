import markdown
from repo import RepoDir
from fileparser import MDFileParser


"""
---
Title: Generelle Infos
Date: 2020-02-15
Publish: Hidden
Publish-after: 2020-02-15 12:00
Description: Diese Seite beinhaltet ein paar Markdown-Elemente
Tags: demo, markdown
Source: http://where-i-stole-my-content.com/article.html
Linkto: some-category/other-content-pointed-to
Linkwith: some-category/other-content-linked-vice-versa
---
"""
AUTHORMETA = "author/meta.md"


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

        """
        /tmp/git2cms/hackersweblog.net/git/authors/deatplayer_main
        README.md /tmp/git2cms/hackersweblog.net/git/authors/deatplayer_main/README.md
        content/README.md /tmp/git2cms/hackersweblog.net/git/authors/deatplayer_main/content/README.md
        author/meta.md /tmp/git2cms/hackersweblog.net/git/authors/deatplayer_main/author/meta.md
        author/en.md /tmp/git2cms/hackersweblog.net/git/authors/deatplayer_main/author/en.md
        author/de.md /tmp/git2cms/hackersweblog.net/git/authors/deatplayer_main/author/de.md
        author/avatar.jpg /tmp/git2cms/hackersweblog.net/git/authors/deatplayer_main/author/avatar.jpg

        /tmp/git2cms/hackersweblog.net/git/authors/sausix_main
        README.md /tmp/git2cms/hackersweblog.net/git/authors/sausix_main/README.md
        author/meta.md /tmp/git2cms/hackersweblog.net/git/authors/sausix_main/author/meta.md
        author/en.md /tmp/git2cms/hackersweblog.net/git/authors/sausix_main/author/en.md
        author/de.md /tmp/git2cms/hackersweblog.net/git/authors/sausix_main/author/de.md
        author/avatar.jpg /tmp/git2cms/hackersweblog.net/git/authors/sausix_main/author/avatar.jpg

        content/seitenaufbau.de.md /tmp/git2cms/hackersweblog.net/git/authors/sausix_main/content/seitenaufbau.de.md
        content/demo/demofile.en.md /tmp/git2cms/hackersweblog.net/git/authors/sausix_main/content/demo/demofile.en.md
        content/demo/demofile.de.md /tmp/git2cms/hackersweblog.net/git/authors/sausix_main/content/demo/demofile.de.md
        content/demo/demo-photo.jpg /tmp/git2cms/hackersweblog.net/git/authors/sausix_main/content/demo/demo-photo.jpg
        """

        # Read all authors
        # repos["AUTHORS"]
        authors = dict()  # nickname
        for repoid, authorrepo in repos["AUTHORS"].items():  # type: RepoDir
            files = authorrepo.files
            meta = files.get(AUTHORMETA)
            if meta is None:
                self.warn(f"There is no author's meta file '{AUTHORMETA}' in repo {repoid}.")
            else:
                # Load meta info of author
                self.log(f"Processing meta of author {repoid}.")
                headers, content = MDFileParser(meta)





        # m = markdown.Markdown()
        #m.reset()

        # markdown.markdownFromFile()


        # Store each repo date as last processed date.
        for typename, repodict in repos.items():
            for repoid, repo in repodict.items():
                repo.store_process_date()

