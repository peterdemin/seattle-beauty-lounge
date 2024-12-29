import glob
import os
import shutil
import subprocess
import sys
import time
from typing import Iterable

import jinja2
from markdown_it import MarkdownIt
from PIL import Image


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

    def __init__(self):
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
            ["npm", "run", "build"],
            capture_output=True,
            check=True,
        )
        script_name = ""
        for path in glob.glob(f"{self.SCRIPTS_DIR}/*.js"):
            shutil.copy(path, f"{self.BUILD_ASSETS_DIR}/")
            shutil.copy(path, f"{self.PUBLIC_ASSETS_DIR}/")
            script_name = os.path.basename(path)
            break  # Just one bundle
        style_name = ""
        for path in glob.glob(f"{self.SCRIPTS_DIR}/*.css"):
            shutil.copy(path, f"{self.BUILD_ASSETS_DIR}/")
            shutil.copy(path, f"{self.PUBLIC_ASSETS_DIR}/")
            style_name = os.path.basename(path)
            break  # Just one bundle
        # Render template with embedded tailwind css
        hours = list(self.iter_hours())
        cancellation_policy = self.load_cancellation_policy()
        self.export_images()
        self.render_index_with_style(
            script_name=script_name,
            style_name=style_name,
            hours=hours,
            cancellation_policy=cancellation_policy,
        )

    def render_index_with_style(self, **params) -> None:
        self.save_rendered_index(f"{self.BUILD_DIR}/index.html", **params)
        style = self.gen_tailwind_css()
        self.save_rendered_index(f"{self.PUBLIC_DIR}/index.html", style=style, **params)

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
                yield {
                    "image": images.get(idx, ""),
                    "title": lines[0].strip(" #"),
                    "description": lines[2],
                    "price": lines[-1],
                }

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
            for path in glob.glob("source/images/*")
        }

    def get_file_index(self, path: str) -> str:
        return os.path.basename(path).split("-")[0]


if __name__ == "__main__":
    builder = Builder()
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        while True:
            try:
                builder.build_public()
            except jinja2.exceptions.TemplateNotFound:
                continue
            time.sleep(0.1)
    else:
        builder.build_public()
