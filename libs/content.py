from libs.filecopying import PathC
from libs.repo import RepoDir
from jinja2 import Template as jt
import markdown
import re

is_html = re.compile(r"^.+\.html?$")
# TODO umbau auf vollständiges template inheritance mit jinja


class Template:
    def __init__(self, myid: str, repo: RepoDir):
        self.templateid = myid
        self.files = repo.files
        self.models = self._load_models()
        self.templatevars = self._load_templatevars()

    def _load_models(self) -> dict:
        models = dict()

        for fileid, file in self.files.items():  # type: str, PathC
            if not is_html.match(fileid):
                continue

            t = jt(source=file.read_text(), autoescape=False)
            models[fileid] = t

        return models

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
            destfile = PathC(destdir / fpath)

            # Check parent directory
            parent = destfile.parent
            if not parent.exists():
                parent.mkdir_result(parents=True, exist_ok=True)

            newfile = file.copy(destfile)
            copied_files.append(newfile)

        return copied_files

    def generate(self, namespace: dict, content: dict, htmlmodel: str = "content.html") -> str:
        if htmlmodel not in self.models:
            raise FileNotFoundError(f"htmlmodel '{htmlmodel}' not found in template {self.templateid}")

        # TODO markdown

        m: jt = self.models[htmlmodel]
        return m.render(**namespace, content=content, template=self.templatevars)


class ContentGenerator:
    def __init__(self, templates: dict, defaulttemplate: str = None):
        if not templates:
            raise FileNotFoundError("No templates provided.")

        # Load each template
        self.templates = {templateid: Template(templateid, repo) for templateid, repo in templates.items()}

        # Check and get default tamplate
        if defaulttemplate is None:
            # Use first template of templates-dict.
            defaulttemplate = next(iter(self.templates.keys()))

        if defaulttemplate not in self.templates:
            raise FileNotFoundError(f"defaulttemplate '{defaulttemplate}' not found.")

        self.defaulttemplate_str = defaulttemplate
        self.defaulttemplate: Template = self.templates[self.defaulttemplate_str]

    def install_template_files(self, webroot: PathC) -> dict:
        copied_files = dict()

        for tid, t in self.templates.items():  # type: str, Template
            rootfolder = webroot / tid
            rootfolder.mkdir(exist_ok=True)
            copied_files[tid] = rootfolder

            templatefiles = t.install_template_files(rootfolder)
            copied_files.update({str(file.relative_to(webroot)): file for file in templatefiles})

        return copied_files

    def generate_content(self, namespace: dict, htmlmodel: str, content: dict) -> str:
        template_str = content.get("template", self.defaulttemplate_str)

        if template_str not in self.templates:
            # Unknown template specified. Using default
            template = self.defaulttemplate
        else:
            template = self.templates[template_str]

        return template.generate(namespace, content, htmlmodel)
