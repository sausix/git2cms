from libs.filecopying import PathC
from libs.repo import RepoDir
from libs.streamlogging import Logger
from jinja2 import Environment, select_autoescape
import markdown as mdmod
import re

is_html = re.compile(r"^.+\.html?$")


def markdown(text: str) -> str:
    return "yeah!"


class Template:
    def __init__(self, myid: str, repo: RepoDir, basemodels: tuple):
        self.templateid = myid
        self.files = repo.files
        self.envs = self._load_envs(basemodels)
        self.templatevars = self._load_templatevars()

    def _load_envs(self, models: tuple) -> dict:
        envs = dict()

        for model in models:  # type: str
            if model not in self.files:
                raise FileNotFoundError(f"Base model '{model}' not found in template '{self.templateid}'")

            htmlfile = self.files[model]

            e = Environment(
                # undefined=1,
                autoescape=select_autoescape(['html'])
            )

            e.tem
            e.filters["markdown"] = markdown

            envs[model] = e

        return envs

    def _load_templatevars(self) -> dict:
        return {
            # All relative links and references will default to the template's directory.
            "head_extras": f"""<base href='/{self.templateid}/'>""",
        }

    def install_template_files(self, destdir: PathC) -> list:
        "Copy all template related files into specified directory."
        copied_files = list()

        for fpath, file in self.files.items():  # type: str, PathC
            if not file.is_file():
                # We don't copy directories. They get created in destdir automatically.
                continue

            if is_html.match(fpath):
                # Skip all html files. Should only affect models.
                continue

            # New full file path
            destfile = destdir / fpath

            # Check parent directory
            parent: PathC = destfile.parent
            if not parent.exists():
                parent.mkdir(exist_ok=True, parents=True)

            newfile = file.copy(destfile)
            copied_files.append(newfile)

        return copied_files

    def generate(self, namespace: dict, content: dict, htmlmodel: str = "content.html") -> str:
        if htmlmodel not in self.envs:
            raise FileNotFoundError(f"htmlmodel '{htmlmodel}' not found in template {self.templateid}")

        e: Environment = self.envs[htmlmodel]
        t = e.get_template('mytemplate.html')
        return t.render(**namespace, content=content, template=self.templatevars)


class ContentGenerator:
    def __init__(self, templates: dict, models: tuple, log: Logger, defaulttemplate: str = None):
        self.log = log

        if not templates:
            raise FileNotFoundError("No templates provided.")

        # Load each template
        self.templates = {templateid: Template(templateid, repo, models) for templateid, repo in templates.items()}

        # Check and get default tamplate
        if defaulttemplate is None:
            # Use first template of templates-dict.
            defaulttemplate = next(iter(self.templates.keys()))

        if defaulttemplate not in self.templates:
            raise FileNotFoundError(f"defaulttemplate '{defaulttemplate}' not found.")

        self.defaulttemplate_str = defaulttemplate
        self.defaulttemplate: Template = self.templates[self.defaulttemplate_str]

    def install_template_files(self, webroot: PathC, touched_files: dict):
        for tid, t in self.templates.items():  # type: str, Template
            rootfolder = webroot / tid
            rootfolder.mkdir(exist_ok=True, parents=True)
            files = t.install_template_files(rootfolder)
            for file in files:  # type: PathC
                relpath = str(file.relative_to(webroot))
                if relpath in touched_files:
                    self.log.err(f"File already existed and has been overwritten: {file}")
                else:
                    touched_files[relpath] = file

    def generate_content(self, namespace: dict, htmlmodel: str, content: dict) -> str:
        template_str = content.get("template", self.defaulttemplate_str)

        if template_str not in self.templates:
            # Unknown template specified. Using default
            template = self.defaulttemplate
        else:
            template = self.templates[template_str]

        return template.generate(namespace, content, htmlmodel)
