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
        pass

    @abstractmethod
    def DATETIME_FORMATS(self) -> dict:
        pass

    @abstractmethod
    def CLONE_DESTINATIONS(self) -> dict:
        # Where to clone everything to. Relative to ROOT or absolute.
        pass

    @abstractmethod
    def GIT_SOURCES(self) -> dict:
        pass

    @abstractmethod
    def WEBROOT(self) -> Path:
        # Where to write generated content to.
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
        pass
