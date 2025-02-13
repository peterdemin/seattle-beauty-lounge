import glob
import os
import re
import shutil
import subprocess
import sys
import time
from typing import Iterable

import docutils.core
import docutils.frontend
import docutils.parsers.rst
import jinja2
from bs4 import BeautifulSoup
from docutils.nodes import Element, TextElement, image
from markdown_it import MarkdownIt
from PIL import Image

from lib.service import PUBLIC_DIR, ImageInfo, ServiceInfo, dump_services

SOURCE_DIR = "source"


class Builder:
    STYLES_DIR = f"{SOURCE_DIR}/styles"
    TEMPLATES_DIR = f"{SOURCE_DIR}/templates"
    SCRIPTS_DIR = f"{SOURCE_DIR}/scripts/dist/assets"
    ADMIN_DIR = "admin/dist/assets"
    PAGES_DIR = f"{SOURCE_DIR}/pages"
    BUILD_DIR = ".build"
    BUILD_ASSETS_DIR = f"{BUILD_DIR}/assets"
    PUBLIC_ASSETS_DIR = f"{PUBLIC_DIR}/assets"

    def __init__(self, mode: str) -> None:
        self._mode = mode
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=jinja2.select_autoescape(),
        )
        self.markdown = MarkdownIt(
            "commonmark",
            {"breaks": True, "html": True},
        )
        self.image_publisher = ImagePublisher()

    def build_public(self) -> None:
        if not os.path.exists(self.PUBLIC_ASSETS_DIR):
            os.makedirs(self.PUBLIC_ASSETS_DIR)
        if not os.path.exists(self.BUILD_ASSETS_DIR):
            os.makedirs(self.BUILD_ASSETS_DIR)
        # Build Javascript for BookingWizard.jsx:
        script_name, style = self._build_javascript()
        services = ServiceParser().parse_all()
        hours = list(self.iter_hours())
        cancellation_policy = self.load_cancellation_policy()
        for service in services:
            self.render_details_with_style(
                service=service,
                script_name=script_name,
                style=style,
            )
        self.image_publisher.export_images()
        self.render_index_with_style(
            services=services,
            script_name=script_name,
            style=style,
            hours=hours,
            cancellation_policy=cancellation_policy,
        )
        dump_services(services)
        self.build_admin()

    def build_admin(self) -> None:
        subprocess.run(
            ["npm", "run", f"admin{self._mode}"],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            [
                "npx",
                "tailwindcss",
                "-c",
                "admin/tailwind.config.admin.js",
                "-o",
                "admin/dist/assets/admin.css",
                "-i",
                "source/styles/input.css",
            ],
            capture_output=True,
            check=True,
        )
        for path in glob.glob(f"{self.ADMIN_DIR}/*.js"):
            shutil.copy(path, f"{self.PUBLIC_ASSETS_DIR}/")
        shutil.copy("admin/dist/admin.html", f"{PUBLIC_DIR}/admin.html")
        shutil.copy(f"{self.ADMIN_DIR}/admin.css", f"{self.PUBLIC_ASSETS_DIR}/")

    def _build_javascript(self) -> tuple[str, str]:
        # Build Javascript for BookingWizard.jsx:
        subprocess.run(
            ["npm", "run", self._mode],
            capture_output=True,
            check=True,
        )
        script_name = ""
        for path in glob.glob(f"{self.SCRIPTS_DIR}/*.js"):
            shutil.copy(path, f"{self.BUILD_ASSETS_DIR}/")
            shutil.copy(path, f"{self.PUBLIC_ASSETS_DIR}/")
            script_name = os.path.basename(path)
            break  # Just one bundle
        style = ""
        for path in glob.glob(f"{self.SCRIPTS_DIR}/*.css"):
            shutil.copy(path, f"{self.BUILD_ASSETS_DIR}/")
            shutil.copy(path, f"{self.PUBLIC_ASSETS_DIR}/")
            with open(path, "rt", encoding="utf-8") as fobj:
                style = fobj.read()
            break  # Just one bundle
        return script_name, style

    def render_index_with_style(self, services: list[ServiceInfo], **params) -> None:
        self.save_rendered_index(f"{self.BUILD_DIR}/index.html", services, **params)
        params["style"] = params.get("style", "") + self.gen_tailwind_css()
        self.save_rendered_index(f"{PUBLIC_DIR}/index.html", services, **params)

    def save_rendered_index(self, path: str, services: list[ServiceInfo], **params) -> None:
        with open(path, "wt", encoding="utf-8") as fobj:
            fobj.write(self.render_index(services, **params))

    def gen_tailwind_css(self) -> str:
        """Must be called after index.html is rendered"""
        subprocess.run(
            [
                "npx",
                "tailwindcss",
                "-i",
                f"./{self.STYLES_DIR}/input.css",
                "-o",
                f"{self.BUILD_ASSETS_DIR}/style.css",
            ],
            capture_output=True,
            check=True,
        )
        with open(f"{self.BUILD_ASSETS_DIR}/style.css", "rt", encoding="utf-8") as fobj:
            return fobj.read()

    def render_index(self, services: list[ServiceInfo], **kwargs) -> str:
        return self.env.get_template("01-index.html").render(services=services, **kwargs)

    def render_details_with_style(self, service: ServiceInfo, **kwargs) -> None:
        if not service.url:
            return
        self.save_rendered_details(f"{self.BUILD_DIR}/index.html", service, **kwargs)
        kwargs["style"] = kwargs.get("style", "") + self.gen_tailwind_css()
        self.save_rendered_details(f"{PUBLIC_DIR}/{service.url}", service, **kwargs)

    def save_rendered_details(self, path: str, service: ServiceInfo, **kwargs) -> None:
        with open(path, "wt", encoding="utf-8") as fobj:
            fobj.write(self.env.get_template("06-details.html").render(service=service, **kwargs))

    def load_cancellation_policy(self) -> str:
        with open(f"{self.PAGES_DIR}/52-cancellation.md", "rt", encoding="utf-8") as fobj:
            return self.markdown.render(fobj.read())

    def iter_hours(self) -> Iterable[dict]:
        with open(f"{self.PAGES_DIR}/51-hours.md", "rt", encoding="utf-8") as fobj:
            for line in fobj:
                day, hours = line.strip().split(None, 1)
                yield {"day": day, "hours": hours}


class ImagePublisher:
    IMAGE_GLOBS = (f"{SOURCE_DIR}/images/*", f"{SOURCE_DIR}/[0-9]-*/images/*")
    SERVICE_IMAGE_MAX_SIZE = (500, 500)

    def export_images(self) -> None:
        for im in self.find_images():
            target_dir = os.path.dirname(im.public)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if os.path.basename(im.source).startswith("0"):
                shutil.copy(im.source, im.public)
            else:
                self.export_thumbnail(im.source, im.public)

    def export_thumbnail(self, source: str, target: str) -> None:
        image = Image.open(source)
        image.thumbnail(self.SERVICE_IMAGE_MAX_SIZE)
        image.save(target)

    def find_images(self) -> Iterable[ImageInfo]:
        for ptrn in self.IMAGE_GLOBS:
            for path in glob.glob(ptrn):
                yield ImageInfo.from_source(path)


class ServiceParser:
    RE_NUMBER = re.compile(r"(\d+).*")
    SERVICE_PTRN = f"{SOURCE_DIR}/[123]-*/[0-9][0-9]-*.rst"

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
                if type(child) is image:
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
        soup = BeautifulSoup(
            docutils.core.publish_from_doctree(doctree, writer_name="html"), "html.parser"
        )
        div = soup.html.body.div  # pyright: ignore
        assert div is not None
        div["class"] = "p-6 font-light text-black"
        del div["id"]
        for element in div.find_all("p"):
            element["class"] = "py-2"
        for element in div.find_all("h1"):
            element["class"] = "py-2 text-2xl text-primary"
        for element in div.find_all("h2"):
            element["class"] = "py-2 text-xl"
        for element in div.find_all("h3"):
            element["class"] = "py-2 text-lg"
        for element in div.find_all("img"):
            path, _ = os.path.splitext(element["src"])
            element["src"] = f"{path}.webp"
            element["class"] = "w-full"

        return div.prettify()

    def _make_image(self, path: str) -> ImageInfo:
        return ImageInfo.from_source(path)


def main(mode: str = "development", watch: bool = False):
    builder = Builder(mode)
    if watch:
        while True:
            try:
                builder.build_public()
            except jinja2.exceptions.TemplateNotFound:
                print("F", end="")
                continue
            print(".", end="")
            time.sleep(0.1)
    else:
        builder.build_public()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        raise RuntimeError("Pass mode [development|staging|production] as the first parameter")
    watch = False
    if len(sys.argv) > 2 and sys.argv[2] == "watch":
        watch = True
    main(mode, watch)
