# -*- coding: utf-8 -*-
from pathlib import Path


class HackersweblogConfig:
    """
    Config for webpage content creation of a specific page
    """

    # Authors need to grant their content to this page id in their meta.md
    PAGEID = "hackersweblog.net"

    # For absolute URL generatings
    BASEADDRESS = "https://hackersweblog.net"

    # Root directory below Config.ROOT or absolute
    # Affect all project's working directories below if they're absolute
    ROOT = Path(f"{PAGEID}")

    # Date and time formats for each propertyname used in datetimes.
    # Languages may be diverge. Formats without language code refer to ISO.
    # This list overwrites and/or extends Config.DATETIME_FORMATS.
    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    DATETIME_FORMATS = {
    }

    # Where to clone everything to. Relative to ROOT or absolute.
    CLONE_DESTINATIONS = {
        "TEMPLATES": Path("git/templates"),
        "AUTHORS": Path("git/authors"),
    }

    GIT_SOURCES = {
        # Template sources
        #  Dictionary of template sources to clone.
        #  Key is template id.
        "TEMPLATES": {
            f"{PAGEID}": "https://github.com/DeatPlayer/hackersweblog.net-page-template"
        },

        # Content sources
        #  Dictionary of authors and their sources to clone.
        #  Key is just descriptive for the repository url. Unique authors may have multiple repositories.
        "AUTHORS": {
            "sausix_main": "https://github.com/sausix/hackersweblog.net-author.git",
            "deatplayer_main": "https://github.com/DeatPlayer/hackersweblog.net-author.git",
            "git2cms_manual": "https://github.com/sausix/git2cms.git"
        }
    }

    # Where to write generated content to.
    #  Script-User need either write access to this directory or http server user need read access there.
    # WEBROOT = Path("/srv/http/hackersweblog.net/beta")
    WEBROOT = Path("content")

    # If no other output defined (cron task), use this one.
    LOGFILE = Path("generate.log")

    CONTENT_SETTINGS = {
        # Preferred language if not specified. Main language of page.
        # Content in this language will be displayed implicitly.
        "LANG_DEFAULT": "en",

        # If no template defined:
        "TEMPLATE_DEFAULT": f"{PAGEID}",

        # Create INDEX_FILE in each named subfolder
        "INDEX_ONLY": False,

        # Generate extensions
        #  INDEX_ONLY = False
        #   file.md to file.html
        #   file.en.md to file/en.html
        #  INDEX_ONLY = True
        #   file.md to file/index.html
        #   file.en.md to file/en/index.html
        "CONTENT_FILE_EXTENSION": ".html",

        # Index file name of root documents
        "INDEX_FILE": "index.html",

        # All files of content directories will be copied.
        # Valid content files may be skipped.
        "COPY_CONTENT_MD": False,

        # If a content has no image tag set and none of "tag".jpg in content.tags can be found, use this one:
        "CONTENT_IMAGE": "content.jpg",

        # If a content file has no tag specified which is not required, use this tag set:
        # If empty set, None or set of an empty string is chosen, there will be no visible tag.
        "TAG_DEFAULT": {"notag"},

        "GLOBAL_STRINGS": {
            "copyright": "© Copyright 2020"
        }
    }
