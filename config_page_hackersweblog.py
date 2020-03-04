# -*- coding: utf-8 -*-
from pathlib import Path
from libs.abs.pageconfig import PageConfig


class HackersweblogConfig(PageConfig):
    """
    Config for webpage content creation of hackersweblog.net
    """

    # Authors need to grant their content to this page id in their meta.md
    PAGEID = "hackersweblog.net"

    # For absolute URL generatings
    BASEADDRESS = "https://hackersweblog.net"

    # Root directory below Config.ROOT or absolute
    # Affect all project's working directories below if they're absolute
    ROOT = Path(PAGEID)

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
            # "cooltemplate": "https://github.com/DeatPlayer/hackersweblog.net-page-template",
            f"{PAGEID}": "https://github.com/sausix/hackersweblog.net-page-template.git"
        },

        # Content sources
        #  Dictionary of authors and their sources to clone.
        #  Key is just descriptive for the repository url. Unique authors may have multiple repositories.
        "AUTHORS": {
            "sausix_main": "https://github.com/sausix/hackersweblog.net-author.git",
            "deatplayer_main": "https://github.com/DeatPlayer/hackersweblog.net-author.git",
            "git2cms_manual": "https://github.com/sausix/git2cms-content-manual.git"
        }
    }

    # Where to write generated content to.
    #  Script-User need either write access to this directory or http server user need read access there.
    # WEBROOT = Path("/srv/http/hackersweblog.net/beta")
    WEBROOT = Path("webroot")

    # Static directories under WEBROOT wont be modified or deleted.
    WEBROOT_STATIC_DIRS = {
        Path("static"),
    }

    # If no other output defined (cron task), use this one.
    LOGFILE = Path("generate.log")

    FEATURES = {  # TODO implement feature options in code
        "content:linking": True,  # meta headers linkto, linkwith
        "content:tags": True,  # tags and tag index pages
        "content:authors": True,  # Create author pages
        "files:copy:other": True,  # copy images, downloads
        "files:copy:md": False,  # copy md source file
        "generate:fileindex": Path("files.txt"),
        "lang:preferisolate": True,
    }

    CONTENT_SETTINGS = {
        # Preferred language if not specified. Main language of page.
        # Content in this language will be displayed implicitly.
        "LANG_DEFAULT": "en",

        # If no template defined:
        "TEMPLATE_DEFAULT": f"{PAGEID}",

        # ### File naming ############################################
        # Create INDEX_FILE in each named subfolder
        "INDEX_ONLY": False,

        # Filename extension
        "CONTENT_FILE_EXTENSION": ".html",

        # Index file name of root documents
        "INDEX_FILE": "index.html",

        # Use title in url. Urls will be uglier an longer.
        # "http://example.com/linux/php/how-to-remove-php.html"
        # "URL_TITLE": False,

        # Use title directly in root folder for url.
        # INDEX_ONLY should be used to minimize naming conflicts on content merge.
        # "http://example.com/how-to-remove-php.html"
        # "http://example.com/how-to-remove-php/index.html"
        # "URL_TITLE_ROOT_ONLY": False,

        # Generated extensions
        #  INDEX_ONLY = False
        #   file.md to file.html
        #   file.en.md to file-en.html
        #  INDEX_ONLY = True
        #   file.md to file/index.html
        #   file.en.md to file/en/index.html
        # ############################################################

        # Replace spaces from content id for URLs to this char before urlencode does crazy things.
        # None refers completely to urlencode.
        # "SPACE_REPLACE": "_",
        "SPACE_REPLACE": "-",

        # If a content has no image tag set and none of "tag".jpg in content.tags can be found, use this one:
        "CONTENT_IMAGE": "content.jpg",

        # If a content file has no tag specified which is not required, use this tag set:
        # If empty set, None or set of an empty string is chosen, there will be no visible tag.
        "TAG_DEFAULT": {"notag"},

        "GLOBAL_STRINGS": {
            "pagename": "hackersweblog.net",
            "copyright": "© Copyright 2020"
        }
    }
