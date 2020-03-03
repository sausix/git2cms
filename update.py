#!/usr/bin/env python3
import sys
from config import Config
from libs.page import Page
from libs.streamlogging import Logger


class Updater:
    def __init__(self, config: Config, stdout=sys.stdout, stderr=sys.stderr):
        self.config = config
        self.log = Logger(stdout, stdout, stderr)
        self.noclone = False
        self.noclonetemplates = False
        self.nogenerate = False
        self.generate_on_changes_only = False
        self.fromcron = False

    def fail(self, text: str):
        "Raise an Exception and quit application"
        self.log.err(text)
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
        self.log.out("""Help of updater.py:
        --cron
            Tell running by cron. Content generation only on demand.

        --allpages
            Update all pages

        --page pageid [--page pageid2] ..
            Update specific pages

        --noclone
            Do not think about cloning.

        --noclone-templates
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
        self.noclonetemplates = "--noclone-templates" in args
        self.nogenerate = "--nogenerate" in args
        self.fromcron = "--cron" in args
        self.generate_on_changes_only = self.fromcron

        if len(pages) == 0:
            self.log.warn("No pages configured/selected.")

        for page in pages:
            self.process_page(page)

        return 0  # The secret code of success

    def process_page(self, pageconfig):
        self.log.out(f"Processing page '{pageconfig.PAGEID}'...")
        p = Page(self.config, pageconfig, logger=None if self.fromcron else self.log.sublogger(pageconfig.PAGEID))

        if not self.noclone:
            p.clone_authors()
            if not self.noclonetemplates:
                p.clone_templates()
        if not self.nogenerate:
            p.generate_content(self.generate_on_changes_only)
        self.log.out(f"Done processing of '{pageconfig.PAGEID}'.")


if __name__ == "__main__":
    # Create app and assign config
    updater = Updater(Config())
    # TODO exception handling
    # Run app
    #try:
    exitcode = updater.main(sys.argv[1:])  # Pass all command line options to args
    #except Exception as e:
    #    updater.fail("General error" + e)
    #    exitcode = 1    # Return your exit code to the caller and exit gracefully.

    sys.exit(exitcode)
