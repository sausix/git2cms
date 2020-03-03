# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from pathlib import Path

# No settings to change in this file!


class PageConfig(metaclass=ABCMeta):
    """
    ABS PageConfig for webpage config
    Defines required properties of a PageConfig
    Don't change settings in this file!
    """
    def __init__(self, config):
        self.config = config

        # pageconfig.ROOT
        if isinstance(self.ROOT, Path):
            # Path set
            if not self.ROOT.is_absolute():
                self.ROOT = self.config.ROOT / self.ROOT
        else:
            # Not set or unknown type
            self.ROOT = self.config.ROOT

        # pageconfig.CLONE_DESTINATIONS
        self.CLONE_DESTINATIONS = {
            key: path if path.is_absolute() else self.ROOT / path
            for key, path in self.CLONE_DESTINATIONS.items()  # type: str, Path
        }

        # pageconfig.LOGFILE
        if not self.LOGFILE.is_absolute():
            self.LOGFILE = self.ROOT / self.LOGFILE

        # pageconfig.WEBROOT
        if not self.WEBROOT.is_absolute():
            self.WEBROOT = self.ROOT / self.WEBROOT

        # pageconfig.WEBROOT_STATIC_DIRS
        self.WEBROOT_STATIC_DIRS = {
            self.WEBROOT / path for path in self.WEBROOT_STATIC_DIRS if not path.is_absolute()  # type: Path
        }

    @abstractmethod
    def PAGEID(self) -> str:
        # Authors need to grant their content to this page id in their meta.md
        pass

    @abstractmethod
    def BASEADDRESS(self) -> str:
        # For absolute URL generatings
        pass

    @abstractmethod
    def ROOT(self) -> Path:
        # Root directory below Config.ROOT or absolute
        # Affect all project's working directories below if they're absolute
        pass

    @abstractmethod
    def DATETIME_FORMATS(self) -> dict:
        # Date and time formats for each propertyname used in datetimes.
        # Languages may be diverge. Formats without language code refer to ISO.
        # This list overwrites and/or extends Config.DATETIME_FORMATS.
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        pass

    @abstractmethod
    def CLONE_DESTINATIONS(self) -> dict:
        # Where to clone everything to. Relative to ROOT or absolute.
        pass

    @abstractmethod
    def GIT_SOURCES(self) -> dict:
        """
        "TEMPLATES": {
            "my_template": "https://github.com/sausix/git2cms-template-base.git"
        },

        # Content sources
        #  Dictionary of authors and their sources to clone.
        #  Key is just descriptive for the repository url. Unique authors may have multiple repositories.
        "AUTHORS": {
            "git2cms_manual": "https://github.com/sausix/git2cms-content-manual.git",
        }
        """
        pass

    @abstractmethod
    def WEBROOT(self) -> Path:
        # Where to write generated content to.
        #  Script-User need either write access to this directory or http server user need read access there.
        # WEBROOT = Path("/srv/http/hackersweblog.net/beta")
        pass

    @abstractmethod
    def WEBROOT_STATIC_DIRS(self) -> set:
        # Static directories under WEBROOT wont be modified or deleted.
        pass

    @abstractmethod
    def LOGFILE(self) -> Path:
        # If no other output defined (cron task), use this one.
        pass

    @abstractmethod
    def FEATURES(self) -> dict:
        # Enabled features for page
        pass

    @abstractmethod
    def CONTENT_SETTINGS(self) -> dict:
        # Detailed settings for content
        """
        {
            # Preferred language if not specified. Main language of page.
            # Content in this language will be displayed implicitly.
            "LANG_DEFAULT": "en",

            # If no template defined:
            "TEMPLATE_DEFAULT": "my_template",

            # ### File naming ############################################
            # Create INDEX_FILE in each named subfolder
            "INDEX_ONLY": False,

            # Filename extension
            "CONTENT_FILE_EXTENSION": ".html",

            # Index file name of root documents
            "INDEX_FILE": "index.html",

            # Generated extensions
            #  INDEX_ONLY = False
            #   file.md to file.html
            #   file.en.md to file-en.html
            #  INDEX_ONLY = True
            #   file.md to file/index.html
            #   file.en.md to file/en/index.html
            # ############################################################

            # Replace ugly URL chars to this char.
            # None refers to urlencode.
            "REPLACE_URL_CHAR": "-",

            # If a content has no image tag set and none of "tag".jpg in content.tags can be found, use this one:
            "CONTENT_IMAGE": "content.jpg",

            # If a content file has no tag specified which is not required, use this tag set:
            # If empty set, None or set of an empty string is chosen, there will be no visible tag.
            "TAG_DEFAULT": {"notag"},

            "GLOBAL_STRINGS": {
                "copyright": "© Copyright 2020"
            }
        }
        """
        pass
