import glob
import os
import re
import shutil
import subprocess
from typing import Iterable

from markdown_it import MarkdownIt

from lib.jd import JohnnyDecimal
from lib.service import PUBLIC_DIR, ServiceInfo, Snippet, dump_content

from .constants import SOURCE_DIR
from .image_publisher import ImagePublisher
from .javascript_embedder import JavascriptEmbedder
from .page import Page
from .renderer import Renderer
from .service_parser import ServiceParser
from .tailwind import Tailwind


class Builder:
    SCRIPTS_DIR = f"{SOURCE_DIR}/scripts/dist/assets"
    ADMIN_DIR = "admin/dist/assets"
    PAGES_DIR = f"{SOURCE_DIR}/pages"
    MEDIA_PTRN = f"{SOURCE_DIR}/7-media/[0-9][0-9]-*.rst"
    BUILD_DIR = ".build"
    BUILD_ASSETS_DIR = f"{BUILD_DIR}/assets"
    PUBLIC_ASSETS_DIR = f"{PUBLIC_DIR}/assets"
    _RE_PHONE_NUMBER = re.compile(r"\+1\s\(\d{3}\)\s\d{3}-\d{4}")

    def __init__(self, mode: str, renderer: Renderer, tailwind: Tailwind) -> None:
        self._mode = mode
        self._renderer = renderer
        self._tailwind = tailwind
        self.markdown = MarkdownIt(
            "commonmark",
            {"breaks": True, "html": True},
        )
        self.image_publisher = ImagePublisher()
        self._embed_js_template = JavascriptEmbedder()

    def build_public(self) -> None:
        if not os.path.exists(self.PUBLIC_ASSETS_DIR):
            os.makedirs(self.PUBLIC_ASSETS_DIR)
        if not os.path.exists(self.BUILD_ASSETS_DIR):
            os.makedirs(self.BUILD_ASSETS_DIR)
        snippets = self.load_snippets()
        media: dict[str, Snippet] = {snippet.full_index: snippet for snippet in snippets}
        # Build Javascript for BookingWizard.jsx:
        script_name, style = self._build_javascript(media)
        services = ServiceParser().parse_all()
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
            hours=list(self.iter_hours(media)),
            cancellation_policy=self.load_cancellation_policy(),
            media=media,
        )
        dump_content(services, snippets)
        self.build_admin()

    def build_admin(self) -> None:
        subprocess.run(
            ["npm", "run", f"admin{self._mode}"],
            capture_output=True,
            check=True,
        )
        self._tailwind(
            "admin/tailwind.config.admin.js",
            "admin/dist/assets/admin.css",
        )
        for path in glob.glob(f"{self.ADMIN_DIR}/*.js"):
            shutil.copy(path, f"{self.PUBLIC_ASSETS_DIR}/")
        shutil.copy("admin/dist/admin.html", f"{PUBLIC_DIR}/admin.html")
        shutil.copy(f"{self.ADMIN_DIR}/admin.css", f"{self.PUBLIC_ASSETS_DIR}/")

    def _build_javascript(self, media: dict[str, Snippet]) -> tuple[str, str]:
        for path in glob.glob(f"{SOURCE_DIR}/scripts/*Template.js"):
            self._embed_js_template(path, media)

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

    def render_index_with_style(self, **kwargs) -> None:
        kwargs["mode"] = self._mode
        self._renderer.render_index(f"{self.BUILD_DIR}/index.html", **kwargs)
        kwargs["style"] = kwargs.get("style", "") + self.gen_tailwind_css()
        self._renderer.render_index(f"{PUBLIC_DIR}/index.html", **kwargs)

    def render_details_with_style(self, service: ServiceInfo, **kwargs) -> None:
        if not service.url:
            return
        kwargs.update({"mode": self._mode, "service": service})
        self._renderer.render_details(f"{self.BUILD_DIR}/index.html", **kwargs)
        kwargs["style"] = kwargs.get("style", "") + self.gen_tailwind_css()
        self._renderer.render_details(f"{PUBLIC_DIR}/{service.url}", **kwargs)

    def gen_tailwind_css(self) -> str:
        """Must be called after index.html is rendered"""
        return self._tailwind(
            "tailwind.config.js",
            f"{self.BUILD_ASSETS_DIR}/style.css",
        )

    def load_cancellation_policy(self) -> str:
        with open(f"{self.PAGES_DIR}/52-cancellation.md", "rt", encoding="utf-8") as fobj:
            return self.markdown.render(fobj.read())

    def iter_hours(self, media: dict[str, Snippet]) -> Iterable[dict]:
        for line in media["7.05"].plain_text.splitlines()[1:]:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                day, hours = parts
                yield {"day": day, "hours": hours}

    def load_snippets(self) -> list[Snippet]:
        page = Page()
        snippets: list[Snippet] = []
        for path in sorted(glob.glob(self.MEDIA_PTRN)):
            with open(path, encoding="utf-8") as fobj:
                rst = fobj.read()
            snippets.append(
                Snippet(
                    full_index=JohnnyDecimal(path).full_index,
                    html=page.render_html(self._highlight_phone_numbers(rst)),
                    plain_text=page.render_plain_text(rst),
                )
            )
        return snippets

    def _highlight_phone_numbers(self, rst: str) -> str:
        return self._RE_PHONE_NUMBER.sub(self._phone_markup, rst)

    def _phone_markup(self, mobj: re.Match) -> str:
        digits = "".join(c for c in mobj.group(0) if c.isdigit() or c == "+")
        return f"`{mobj.group(0)} <tel:{digits}>`_"
