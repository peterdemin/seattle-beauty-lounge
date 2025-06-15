from collections import deque
from typing import Callable, cast

import docutils.core
from bs4 import BeautifulSoup
from docutils.nodes import Element


class Page:
    TAG_CLASSES = {
        "p": "py-2",
        "h1": "py-2 text-2xl text-primary font-light",
        "h2": "py-2 text-xl",
        "h3": "py-2 text-lg",
        "img": "w-full",
        "ul": "list-disc list-inside",
        "a": "font-medium text-primary underline",
    }

    def __init__(self, hooks: dict[str, Callable[[Element], None]] | None = None) -> None:
        self._hooks = hooks or {}

    def render_html(self, rst: str) -> str:
        doctree = docutils.core.publish_doctree(rst)
        return self.render_from_doctree(doctree)

    def render_from_doctree(self, doctree: Element) -> str:
        if not doctree.children:
            return ""
        soup = BeautifulSoup(
            docutils.core.publish_from_doctree(doctree, writer_name="html"),
            "html.parser",
        )
        div = soup.html.body.div  # pyright: ignore
        assert div is not None
        div["class"] = "p-6 font-light text-black"
        del div["id"]
        for tag, classes in self.TAG_CLASSES.items():
            for element in div.find_all(tag):
                element = cast(Element, element)
                element["class"] = classes
        for tag, hook in self._hooks.items():
            for element in div.find_all(tag):
                hook(cast(Element, element))
        return cast(str, div.prettify())

    def render_plain_text(self, rst: str) -> str:
        doctree = docutils.core.publish_doctree(rst)
        lines = []
        elems = deque(doctree.children)
        while elems:
            elem = elems.popleft()
            if elem.tagname in ("bullet_list", "section"):
                elems.extendleft(elem.children[::-1])
            elif elem.tagname in ("title", "subtitle", "paragraph"):
                lines.append(elem.astext().strip())
            elif elem.tagname == "line_block":
                lines.append("\n".join(c.astext().strip() for c in elem.children))
            elif elem.tagname in ("list_item"):
                lines.append("- " + elem.astext().strip())
            elif elem.tagname in ("target", "comment", "substitution_definition"):
                pass
            else:
                raise ValueError(f"Unsupported tag {elem.tagname}: {elem}")
        return "\n\n".join(lines)
