from config import THEME, AUTHOR_SOURCES_GIT, CLONE_DESTINATION, GITSRC
import subprocess
import markdown


def clone_all():
    for authorid, url in AUTHOR_SOURCES_GIT.items():
        clone(authorid, url)


def clone(authorid: str, url: str):
    cmd = 'git', 'clone', url, f"{CLONE_DESTINATION}/{authorid}"

    with open(f"{CLONE_DESTINATION}/{authorid}.log", "w") as log:
        with open(f"{CLONE_DESTINATION}/{authorid}.err", "w") as err:
            try:
                subprocess.run(cmd, stdout=log, stderr=err)
            except Exception as e:
                err.write("\n\nError while running git: ")
                err.write(" ".join(e.args))


clone_all()
