from config.config_page_hackersweblog import HackersweblogConfig


class Config:
    """
    General config for webpage content creation
    """

    # Git source for cms backend updates
    GIT_SOURCE = "https://github.com/sausix/git2cms"

    # Absolute root directory for all working files
    # ROOT = "/home/git2cms"
    ROOT = "/tmp/git2cms"

    # Active webpages. Import them on top of this file.
    PAGES = {
        HackersweblogConfig.PAGEID: HackersweblogConfig(),
    }
