import jinja2

from .constants import SOURCE_DIR


class Renderer:
    TEMPLATES_DIR = f"{SOURCE_DIR}/templates"

    def __init__(self) -> None:
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=jinja2.select_autoescape(),
        )

    def render_index(self, path: str, **params) -> None:
        with open(path, "wt", encoding="utf-8") as fobj:
            fobj.write(self.env.get_template("01-index.html").render(**params))

    def render_details(self, path: str, **kwargs) -> None:
        with open(path, "wt", encoding="utf-8") as fobj:
            fobj.write(self.env.get_template("06-details.html").render(**kwargs))
