from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="git2cms",
    description="git2cms html content generator",
    keywords="git, cms, html",

    version="0.1.0",  # main.minor.bugfix
    packages=[],

    install_requires=("Jinja2", "PyYAML", "GitPython", "markdown"),

    author="Adrian Sausenthaler",
    author_email="pypi@digi-solution.de",
    
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/sausix/git2cms",

    license="GPLv3",

    classifiers=[  # https://pypi.org/classifiers/
        "Development Status :: 1 - Planning",

        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        # "Operating System :: OS Independent",

        "Environment :: Plugins",
        "Environment :: X11 Applications :: Qt",

        "Environment :: Console",
        # "Environment :: Win32 (MS Windows)",
        # "Environment :: MacOS X",

        "Operating System :: POSIX :: Linux",
        # "Operating System :: Microsoft :: Windows",
        # "Operating System :: MacOS",

        "Intended Audience :: Information Technology",

        "Topic :: Internet",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],

    python_requires='>=3.6',

    project_urls={
        "GitHub repository": "https://github.com/sausix/git2cms",
        "Homepage": "https://hackersweblog.net/projects/git2cms",
        "Manual": "https://hackersweblog.net/git2cms/",
    },
)

# from pkg_resources import parse_version
# parse_version('1.9.a.dev') == parse_version('1.9a0dev')
# parse_version('2.1-rc2') < parse_version('2.1')
