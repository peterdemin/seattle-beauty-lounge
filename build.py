import glob
import os
import shutil
import subprocess
import sys
import time
from typing import Iterable

import jinja2


class Builder:
    SOURCE_DIR = "source"
    PUBLIC_DIR = "public"
    PUBLIC_ASSETS_DIR = f"{PUBLIC_DIR}/assets"
    TEMPLATES_DIR = f"{SOURCE_DIR}/templates"
    SCRIPTS_DIR = f"{SOURCE_DIR}/scripts/dist/assets"

    def __init__(self):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=jinja2.select_autoescape(),
        )

    def build_public(self) -> None:
        if not os.path.exists(self.PUBLIC_ASSETS_DIR):
            os.makedirs(self.PUBLIC_ASSETS_DIR)
        subprocess.run(
            ["npm", "run", "build"],
            capture_output=True,
            check=True,
        )
        for path in glob.glob(f'{self.SCRIPTS_DIR}/*.js'):
            shutil.copy(path, f'{self.PUBLIC_ASSETS_DIR}/book.js')
            break  # Just one bundle
        with open(f"{self.PUBLIC_DIR}/index.html", "wt", encoding="utf-8") as fobj:
            fobj.write(self.render_index())
        for image in self.find_images().values():
            target_dir = os.path.dirname(image["public"])
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            shutil.copy(image["source"], image["public"])
        subprocess.run(
            [
                "npx",
                "tailwindcss",
                "-i",
                "./source/styles/input.css",
                "-o",
                "./public/assets/style.css",
            ],
            capture_output=True,
            check=True,
        )

    def render_index(self) -> str:
        return self.env.get_template("01-index.html").render(
            services=list(self.iter_services())
        )

    def render_services(self) -> str:
        return self.env.get_template("02-services.html").render(
            services=list(self.iter_services())
        )

    def iter_services(self) -> Iterable[dict]:
        images = self.find_images()
        for path in sorted(glob.glob("source/services/*.md")):
            idx = self.get_file_index(path)
            with open(path, "rt", encoding="utf-8") as fobj:
                lines = [line.strip() for line in fobj]
                yield {
                    "image": images.get(idx, ""),
                    "title": lines[0].strip(" #"),
                    "description": lines[2],
                    "price": lines[-1],
                }

    def find_images(self) -> dict[str, str]:
        return {
            self.get_file_index(path): {
                "source": path,
                "public": os.path.join(
                    self.PUBLIC_DIR, os.path.relpath(path, self.SOURCE_DIR)
                ),
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