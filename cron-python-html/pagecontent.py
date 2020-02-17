from repo import RepoDir
import markdown

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

        # Read all authors
        # repos["AUTHORS"]

        markdown.markdownFromFile()


        # Store each repo date as last processed date.
        for typename, repodict in repos.items():
            for repoid, repo in repodict.items():
                repo.store_process_date()

