# -*- coding: utf-8 -*-
from pathlib import Path
from config.config_page_hackersweblog import HackersweblogConfig


class Config:
    """
    General config for webpage content creation
    """

    # Date and time formats for each propertyname used in datetimes.
    # Languages may be diverge. Formats without language code refer to ISO.
    # PageConfig.DATETIME_FORMATS overwrites and/or extends this list.
    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    DATETIME_FORMATS = {
        "year": "%Y",
        "year2": "%y",
        "month": "%m",
        "day": "%d",
        "hour": "%H",
        "minute": "%M",
        "second": "%S",

        "date": "%Y-%m-%d",  # ISO
        "date:en": "%d/%m/%Y",  # DMY or YMD anytime, deal?
        "date:de": "%d.%m.%Y",

        "time": "%H:%M:%S",  # ISO
        "time:en": "%I:%M:%S %p",
    }

    # Git source for cms backend updates
    GIT_SOURCE = "https://github.com/sausix/git2cms"

    # Absolute root directory for all working files
    # ROOT = "/home/git2cms"
    ROOT = Path("/home/as/workfiles")

    # Active webpages. Import them on top of this file.
    PAGES = {
        HackersweblogConfig.PAGEID: HackersweblogConfig(),
    }
