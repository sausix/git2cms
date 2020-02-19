#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from config.config import Config
from page import Page


class Updater:
    def __init__(self, config: Config, stdout=sys.stdout, stderr=sys.stderr):
        self.config = config
        self.stdout = stdout
        self.stderr = stderr
        self.noclone = False
        self.noclonethemes = False
        self.nogenerate = False
        self.generate_on_changes = False
        self.fromcron = False

    def log(self, text: str):
        "Output text to stdout"
        if self.stdout is None:
            return

        self.stdout.write(text)
        self.stdout.write("\n")

    def fail(self, text: str):
        "Raise an Exception and quit application"
        raise Exception(text)

    def parse_pages(self, args: list) -> set:
        """
        Parse and check pages with arguments and config.
        returns list of pageconfigs
        """
        pages = set()

        if "--allpages" in args:
            # Return all page configs found in config
            return set(self.config.PAGES.values())

        next_is_pageid = False
        for arg in args:
            if next_is_pageid:
                pageid = arg

                if pageid not in self.config.PAGES:
                    self.fail(f"PageID '{pageid}' not found in Config.PAGES.")

                pages.add(self.config.PAGES[pageid])
                next_is_pageid = False
            else:
                next_is_pageid = arg == "--page"

        return pages

    def help(self):
        self.stdout.write("""Help of updater.py:
        --cron
            Tell running by cron. Content generation only on demand.

        --allpages
            Update all pages

        --page pageid [--page pageid2] ..
            Update specific pages

        --noclone
            Do not think about cloning.

        --noclone-themes
            Do not clone themes.

        --nogenerate
            Do not generate content.
        \n""")

    def main(self, args: list) -> int:
        """
        Runs the cron-to-html updater

        :param args: Command line args
            see self.help()
        :return: Exit code
        """

        if "--help" in args:
            self.help()
            return 0

        pages = self.parse_pages(args)

        self.noclone = "--noclone" in args
        self.noclonethemes = "--noclone-themes" in args
        self.nogenerate = "--nogenerate" in args
        self.fromcron = "--cron" in args
        self.generate_on_changes = self.fromcron

        if len(pages) == 0:
            self.log("No pages configured/selected.")

        for page in pages:
            self.process_page(page)

        return 0

    def process_page(self, pageconfig):
        self.log(f"Processing page '{pageconfig.PAGEID}'...")
        p = Page(self.config, pageconfig, stdout=None if self.fromcron else self.stdout)
        if not self.noclone:
            p.clone_authors()
            if not self.noclonethemes:
                p.clone_templates()
        if not self.nogenerate:
            p.generate_content(self.generate_on_changes)
        self.log(f"Done processing of '{pageconfig.PAGEID}'.")


if __name__ == "__main__":
    # Create app and assign config
    updater = Updater(Config())

    # Run app
    #try:
    exitcode = updater.main(sys.argv[1:])  # Pass all command line options to args
    #except Exception as e:
    #    updater.fail("General error" + e)
    #    exitcode = 1    # Return your exit code to the caller and exit gracefully.

    sys.exit(exitcode)
