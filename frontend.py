import glob
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Iterable

import docutils.core
import docutils.frontend
import docutils.parsers.rst
import jinja2
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
from PIL import Image


@dataclass
class ServiceInfo:
    basename: str
    title: str
    price: str
    duration: str
    short_text: str
    full_html: str


class Builder:
    SOURCE_DIR = "source"
    STYLES_DIR = f"{SOURCE_DIR}/styles"
    TEMPLATES_DIR = f"{SOURCE_DIR}/templates"
    SCRIPTS_DIR = f"{SOURCE_DIR}/scripts/dist/assets"
    PAGES_DIR = f"{SOURCE_DIR}/pages"
    BUILD_DIR = ".build"
    BUILD_ASSETS_DIR = f"{BUILD_DIR}/assets"
    PUBLIC_DIR = "public"
    PUBLIC_ASSETS_DIR = f"{PUBLIC_DIR}/assets"
    SERVICE_IMAGE_MAX_SIZE = (500, 500)
    RE_NUMBER = re.compile(r"(\d+).*")

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

    def build_public(self) -> None:
        if not os.path.exists(self.PUBLIC_ASSETS_DIR):
            os.makedirs(self.PUBLIC_ASSETS_DIR)
        if not os.path.exists(self.BUILD_ASSETS_DIR):
            os.makedirs(self.BUILD_ASSETS_DIR)
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
        # Render template with embedded tailwind css
        hours = list(self.iter_hours())
        cancellation_policy = self.load_cancellation_policy()
        self.export_images()
        self.render_index_with_style(
            script_name=script_name,
            style=style,
            hours=hours,
            cancellation_policy=cancellation_policy,
        )
        for service in self.iter_rst_services():
            self.render_details_with_style(
                service,
                script_name=script_name,
                style=style,
            )

    def render_index_with_style(self, **params) -> None:
        self.save_rendered_index(f"{self.BUILD_DIR}/index.html", **params)
        params["style"] = params.get("style", "") + self.gen_tailwind_css()
        self.save_rendered_index(f"{self.PUBLIC_DIR}/index.html", **params)

    def save_rendered_index(self, path: str, **params) -> None:
        with open(path, "wt", encoding="utf-8") as fobj:
            fobj.write(self.render_index(**params))

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

    def render_index(self, **kwargs) -> str:
        return self.env.get_template("01-index.html").render(
            services=list(self.iter_services()), **kwargs
        )

    def render_details_with_style(self, service: ServiceInfo, **kwargs) -> None:
        self.save_rendered_details(f"{self.BUILD_DIR}/index.html", service, **kwargs)
        kwargs["style"] = kwargs.get("style", "") + self.gen_tailwind_css()
        self.save_rendered_details(f"{self.PUBLIC_DIR}/{service.basename}.html", service, **kwargs)

    def save_rendered_details(self, path: str, service: ServiceInfo, **kwargs) -> None:
        with open(path, "wt", encoding="utf-8") as fobj:
            fobj.write(self.render_details(service, **kwargs))

    def render_details(self, service: ServiceInfo, **kwargs) -> str:
        return self.env.get_template("06-details.html").render(service=service, **kwargs)

    def render_services(self) -> str:
        return self.env.get_template("02-services.html").render(services=list(self.iter_services()))

    def load_cancellation_policy(self) -> str:
        with open(f"{self.PAGES_DIR}/52-cancellation.md", "rt", encoding="utf-8") as fobj:
            return self.markdown.render(fobj.read())

    def iter_hours(self) -> Iterable[dict]:
        with open(f"{self.PAGES_DIR}/51-hours.md", "rt", encoding="utf-8") as fobj:
            for line in fobj:
                day, hours = line.strip().split(None, 1)
                yield {"day": day, "hours": hours}

    def iter_services(self) -> Iterable[dict]:
        images = self.find_images()
        for path in sorted(glob.glob(f"{self.SOURCE_DIR}/services/*.md")):
            idx = self.get_file_index(path)
            with open(path, "rt", encoding="utf-8") as fobj:
                lines = [line.strip() for line in fobj]
                price, duration = lines[-1].split(None, 1)
                duration_min = 0
                if mobj := self.RE_NUMBER.match(duration):
                    duration_min = int(mobj.group(1))
                yield {
                    "image": images.get(idx, ""),
                    "title": lines[0].strip(" #"),
                    "description": lines[2],
                    "price": price,
                    "duration": duration,
                    "duration_min": duration_min,
                }

    def iter_rst_services(self) -> Iterable[ServiceInfo]:
        service_parser = ServiceParser()
        for path in sorted(glob.glob(f"{self.SOURCE_DIR}/[123]-*/[0-9][0-9]-*.rst")):
            yield service_parser.parse_rst(path)

    def export_images(self) -> None:
        for image in self.find_images().values():
            target_dir = os.path.dirname(image["public"])
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if os.path.basename(image["source"]).startswith("0"):
                shutil.copy(image["source"], image["public"])
            else:
                self.export_thumbnail(image["source"], image["public"])

    def export_thumbnail(self, source: str, target: str) -> None:
        image = Image.open(source)
        image.thumbnail(self.SERVICE_IMAGE_MAX_SIZE)
        image.save(target)

    def find_images(self) -> dict[str, dict[str, str]]:
        return {
            self.get_file_index(path): {
                "source": path,
                "public": os.path.join(self.PUBLIC_DIR, os.path.relpath(path, self.SOURCE_DIR)),
                "url": os.path.relpath(path, self.SOURCE_DIR),
            }
            for path in glob.glob(f"{self.SOURCE_DIR}/images/*")
            + glob.glob(f"{self.SOURCE_DIR}/[0-9]-*/images/*")
        }

    def get_file_index(self, path: str) -> str:
        return os.path.basename(path).split("-", 1)[0]


class ServiceParser:
    def parse_rst(self, path: str) -> ServiceInfo:
        with open(path, "rt", encoding="utf-8") as fobj:
            rst = fobj.read()
        doctree = docutils.core.publish_doctree(rst)
        title = ""
        price = ""
        duration = ""
        short_text = ""
        cutoff = 0
        for cutoff, child in enumerate(doctree.children):
            if child.tagname == "title" and not title:
                title = child.astext()  # First wins
            elif child.tagname == "transition":
                break
            elif child.tagname == "paragraph":
                parts = child.rawsource.split(":")
                if len(parts) == 2:
                    if parts[0].lower().strip() in ("price", "cost"):
                        price = parts[1].strip()
                        continue
                    if parts[0].lower().strip() in ("time", "duration"):
                        duration = parts[1].strip()
                        continue
                short_text = " ".join(c.astext().strip() for c in child.children)
        doctree.children[: cutoff + 1] = []
        soup = BeautifulSoup(
            docutils.core.publish_from_doctree(doctree, writer_name="html"), "html.parser"
        )
        div = soup.html.body.div
        assert div is not None
        div["class"] = "p-6 font-light text-black [AMP_p]:py-2"
        del div["id"]
        full_html = div.prettify().replace("AMP", "&")
        return ServiceInfo(
            basename=os.path.splitext(os.path.basename(path))[0],
            title=title,
            price=price,
            duration=duration,
            short_text=short_text,
            full_html=full_html,
        )


def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        raise RuntimeError("Pass mode [development|staging|production] as the first parameter")
    builder = Builder(mode)
    if len(sys.argv) > 2 and sys.argv[2] == "watch":
        while True:
            try:
                builder.build_public()
            except jinja2.exceptions.TemplateNotFound:
                print("F", end="")
                continue
            print(".", end="")
            time.sleep(0.1)
    elif len(sys.argv) > 2 and sys.argv[2] == "rst":
        for svc in builder.iter_rst_services():
            builder.render_details_with_style(svc)
    else:
        builder.build_public()


if __name__ == "__main__":
    main()
