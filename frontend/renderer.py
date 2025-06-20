import jinja2

from .constants import SOURCE_DIR


class Renderer:
    TEMPLATES_DIR = f"{SOURCE_DIR}/templates"

    def __init__(self) -> None:
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=jinja2.select_autoescape(),
        )

    def render_template(self, path: str, template: str, **kwargs) -> None:
        with open(path, "wt", encoding="utf-8") as fobj:
            fobj.write(self.env.get_template(template).render(**kwargs))

    def read_template(self, template: str) -> str:
        with open(f"{self.TEMPLATES_DIR}/{template}", "rt", encoding="utf-8") as fobj:
            return fobj.read()
