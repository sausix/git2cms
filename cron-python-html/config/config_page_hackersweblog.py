class HackersweblogConfig:
    """
    Config for webpage content creation of a specific page
    """

    # Authors need to grant their content to this page id in their meta.md
    PAGEID = "hackersweblog.net"

    # Root directory below Config.ROOT or absolute for project's working files
    ROOT = f"{PAGEID}"

    # Where to clone everything to. Relative to Config.ROOT or absolute.
    CLONE_DESTINATIONS = {
        "git2cms": "git/git2cms",
        "templates": "git/templates",
        "authors": "git/authors",
    }

    # Template sources
    #  Dictionary of template sources to clone.
    #  Key is template id.
    GIT_SOURCES_TEMPLATES = {
        f"{PAGEID}": "https://github.com/DeatPlayer/hackersweblog.net-page-template",
    }

    # If no template defined:
    TEMPLATE_DEFAULT = f"{PAGEID}"

    # If defined template unknown
    TEMPLATE_ON_MISSING = TEMPLATE_DEFAULT

    # Content sources
    #  Dictionary of authors and their sources to clone.
    #  Key is just descriptive for the repository url. Unique authors may have multiple repositories.
    GIT_SOURCES_AUTHORS = {
        "sausix_main": "https://github.com/sausix/hackersweblog.net-author.git",
        # "deatplayer_main": "https://github.com/DeatPlayer/hackersweblog.net-author.git",
    }

    # Create only index.html in named subfolders
    # INDEX_ONLY = "index.html"

    # Generate extensions
    #   file.md to file.html
    #   file.md to file/index.html
    #   file.en.md to file/en.html
    #   file.en.md to file/en/index.html
    CONTENT_FILE_EXTENSION = ".html"

    # Preferred language if not specified. Main language of page.
    LANG_DEFAULT = "en"

    # Where to write generated content to.
    #  Script-User need either write access to this directory or http server user need read access there.
    WRITE_DESTINATIONS = {
        # "content": "/srv/http/hackersweblog.net/beta",  # Absolute path!
        "content": "content",  # Absolute path!
        "logfile": "content-create.log"  # Relative path.
    }
