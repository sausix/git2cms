# -*- coding: utf-8 -*-


class HackersweblogConfig:
    """
    Config for webpage content creation of a specific page
    """

    # Authors need to grant their content to this page id in their meta.md
    PAGEID = "hackersweblog.net"

    # For absolute URL generatings
    BASEADDRESS = "https://hackersweblog.net"

    # Root directory below Config.ROOT or absolute for project's working files
    ROOT = f"{PAGEID}"

    # Where to clone everything to. Relative to Config.ROOT or absolute.
    CLONE_DESTINATIONS = {
        "TEMPLATES": "git/templates",
        "AUTHORS": "git/authors",
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
    # WEBROOT = "/srv/http/hackersweblog.net/beta"  # Absolute path!
    WEBROOT = "content"

    CONTENT_SETTINGS = {
        # Preferred language if not specified. Main language of page.
        "LANG_DEFAULT": "en",

        # If no template defined:
        "TEMPLATE_DEFAULT": f"{PAGEID}",

        # If defined template unknown
        "TEMPLATE_ON_MISSING": f"{PAGEID}",

        # Index file name of root documents
        "INDEX_FILE": "index.html",

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

        # If a content has no image tag set and non of "tag".jpg in content.tags can be found, use this one:
        "CONTENT_IMAGE": "content.jpg"
    }
