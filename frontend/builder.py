import glob
import os
import shutil
import subprocess
from typing import Iterable

import jinja2
from markdown_it import MarkdownIt

from lib.service import PUBLIC_DIR, ServiceInfo, dump_services

from .constants import SOURCE_DIR
from .image_publisher import ImagePublisher
from .service_parser import ServiceParser


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
