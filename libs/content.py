from typing import Tuple

import markdown


class TemplateModels:
    def __init__(self, templates: dict, defaulttemplate: str = None):
        if not templates:
            raise FileNotFoundError("No templates provided.")
        self.templates = templates

        if defaulttemplate is None:
            # Use first template of templates-dict.
            defaulttemplate = next(iter(self.templates.keys()))

        if defaulttemplate not in self.templates:
            raise FileNotFoundError(f"defaulttemplate '{defaulttemplate}' not found.")
        self.defaulttemplate = defaulttemplate

        self.models = dict()
        self.md = markdown.Markdown()

    def get_model(self, template: str, modelname: str):
        if modelname in self.models:
            return self.models[modelname]

    def translate_content(self, namespace: dict, htmlmodel: str) -> Tuple[str, set]:
        self.md.reset()

        content: dict = namespace["content"]
        template = content.get("template", self.defaulttemplate)
        model = content.get("model", htmlmodel)

        m = self.get_model(template, model)

        #content_html = md.convert(content["content"])
        return "", files
