import glob
import os
import re

import docutils.core
from docutils.nodes import Element, TextElement, image

from lib.service import ImageInfo, ServiceInfo

from .constants import SOURCE_DIR
from .page import Page


class ServiceParser:
    RE_NUMBER = re.compile(r"(\d+).*")
    SERVICE_PTRN = f"{SOURCE_DIR}/[123]-*/[0-9][0-9]-*.rst"

    def __init__(self) -> None:
        self._page = Page(hooks={"img": self._change_img_ext})

    def _change_img_ext(self, element: Element) -> None:
        path, _ = os.path.splitext(element["src"])
        element["src"] = f"{path}.webp"

    def parse_all(self) -> list[ServiceInfo]:
        result: list[ServiceInfo] = []
        for path in sorted(glob.glob(self.SERVICE_PTRN)):
            try:
                result.append(self.parse_rst(path))
            except ValueError as exc:
                print(f"Skipping {path}: {exc}")
        return result

    def parse_rst(self, path: str) -> ServiceInfo:
        result = ServiceInfo(source_path=path, image=ImageInfo.dummy())
        with open(path, "rt", encoding="utf-8") as fobj:
            rst = fobj.read()
        doctree = docutils.core.publish_doctree(rst)
        cutoff = 0
        for cutoff, child in enumerate(doctree.children):
            if child.tagname == "transition":
                break
            self._parse_info(child, result)
        doctree.children[: cutoff + 1] = []
        result.full_html = self._render_full_html(doctree)
        if result.full_html:
            result.url = f"{result.basename}.html"
        if missing_fields := result.check_missing_fields():
            raise ValueError(f"Service info is incomplete: {missing_fields}")
        return result

    def _parse_info(self, elem: TextElement, result: ServiceInfo) -> None:
        if elem.tagname == "title" and not result.title:
            result.title = elem.astext()  # First wins
        elif elem.tagname == "paragraph":
            if self._maybe_parse_kv(elem, result):
                return
            if elem.children and len(elem.children) == 1:
                child = elem.children[0]
                if isinstance(child, image):
                    result.set_image_from_uri(child["uri"])
                    return
            result.short_text = " ".join(c.astext().strip() for c in elem.children)

    def _maybe_parse_kv(self, elem: TextElement, result: ServiceInfo) -> bool:
        parts = elem.rawsource.split(":")
        if len(parts) == 2:
            if parts[0].lower().strip() in ("price", "cost"):
                result.price = parts[1].strip()
                if numbers := self.RE_NUMBER.findall(result.price):
                    if len(numbers) == 1:
                        result.price_cents = int(numbers[0]) * 100
                return True
            if parts[0].lower().strip() in ("time", "duration"):
                result.duration = parts[1].strip()
                if mobj := self.RE_NUMBER.match(result.duration):
                    result.duration_min = int(mobj.group(1))
                return True
        return False

    def _render_full_html(self, doctree: Element) -> str:
        if not doctree.children:
            return ""
        return self._page.render_from_doctree(doctree)

    def _make_image(self, path: str) -> ImageInfo:
        return ImageInfo.from_source(path)
