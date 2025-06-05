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


class BuildStep:
    _done = False

    def run_once(self) -> None:
        if self._done:
            return
        self.execute()
        print(f"Finished {self.__class__.__name__}")
        self._done = True

    def execute(self) -> None:
        raise NotImplementedError()


class StepFactory:
    def create_step(self) -> BuildStep:
        raise NotImplementedError()


class AggregationStep(BuildStep):

    def __init__(self, dependencies: list[BuildStep]) -> None:
        self._dependencies = dependencies

    def execute(self) -> None:
        for step in self._dependencies:
            step.run_once()
        self._after_dependencies()

    def _after_dependencies(self) -> None:
        pass


class CreateOutputDirectoryStep(BuildStep):
    def __init__(self, path: str) -> None:
        self._path = path

    def execute(self) -> None:
        if os.path.exists(self._path):
            return
        os.makedirs(self._path)


class LoadSnippetsStep(BuildStep):
    _RE_PHONE_NUMBER = re.compile(r"\+1\s\(\d{3}\)\s\d{3}-\d{4}")

    def __init__(self, media_ptrn: str) -> None:
        self._media_ptrn = media_ptrn
        self.snippets: list[Snippet] = []

    def execute(self) -> None:
        page = Page()
        for path in sorted(glob.glob(self._media_ptrn)):
            with open(path, encoding="utf-8") as fobj:
                rst = fobj.read()
            self.snippets.append(
                Snippet(
                    full_index=JohnnyDecimal(path).full_index,
                    html=page.render_html(self._highlight_phone_numbers(rst)),
                    plain_text=page.render_plain_text(rst),
                )
            )

    def _highlight_phone_numbers(self, rst: str) -> str:
        return self._RE_PHONE_NUMBER.sub(self._phone_markup, rst)

    def _phone_markup(self, mobj: re.Match) -> str:
        digits = "".join(c for c in mobj.group(0) if c.isdigit() or c == "+")
        return f"`{mobj.group(0)} <tel:{digits}>`_"


class ParseServicesStep(BuildStep):
    def __init__(self) -> None:
        self.services: list[ServiceInfo] = []
        self._service_parser = ServiceParser()

    def execute(self) -> None:
        self.services = self._service_parser.parse_all()


class DumpSnippetsStep(AggregationStep):

    def __init__(
        self, parse_services_step: ParseServicesStep, load_snippets_step: LoadSnippetsStep
    ) -> None:
        super().__init__([parse_services_step, load_snippets_step])
        self._parse_services_step = parse_services_step
        self._load_snippets_step = load_snippets_step

    def _after_dependencies(self) -> None:
        dump_content(
            self._parse_services_step.services,
            self._load_snippets_step.snippets,
        )


class LoadMediaStep(AggregationStep):

    def __init__(self, load_snippets_step: LoadSnippetsStep) -> None:
        super().__init__([load_snippets_step])
        self._load_snippets_step = load_snippets_step
        self.media: dict[str, Snippet] = {}

    def _after_dependencies(self) -> None:
        if self.media:
            return
        self.media.update(
            {snippet.full_index: snippet for snippet in self._load_snippets_step.snippets}
        )


class EmbedJavascriptStep(AggregationStep):
    def __init__(self, load_media_step: LoadMediaStep, target_ptrn: str) -> None:
        super().__init__([load_media_step])
        self._load_media_step = load_media_step
        self._target_ptrn = target_ptrn
        self._embed_js_template = JavascriptEmbedder()

    def _after_dependencies(self) -> None:
        for path in glob.glob(self._target_ptrn):
            self._embed_js_template(path, self._load_media_step.media)


class BuildJavascriptBundleStep(AggregationStep):
    SCRIPTS_DIR = f"{SOURCE_DIR}/scripts/dist/assets"
    BUILD_DIR = ".build"
    BUILD_ASSETS_DIR = f"{BUILD_DIR}/assets"
    PUBLIC_ASSETS_DIR = f"{PUBLIC_DIR}/assets"

    def __init__(self, embed_javascript_step: EmbedJavascriptStep, mode: str) -> None:
        super().__init__([embed_javascript_step])
        self._mode = mode
        self.script_name = ""
        self.style = ""

    def _after_dependencies(self) -> None:
        subprocess.run(
            ["npm", "run", self._mode],
            capture_output=True,
            check=True,
        )
        for path in glob.glob(f"{self.SCRIPTS_DIR}/*.js"):
            shutil.copy(path, f"{self.BUILD_ASSETS_DIR}/")
            shutil.copy(path, f"{self.PUBLIC_ASSETS_DIR}/")
            self.script_name = os.path.basename(path)
            break  # Just one bundle
        for path in glob.glob(f"{self.SCRIPTS_DIR}/*.css"):
            shutil.copy(path, f"{self.BUILD_ASSETS_DIR}/")
            shutil.copy(path, f"{self.PUBLIC_ASSETS_DIR}/")
            with open(path, "rt", encoding="utf-8") as fobj:
                self.style = fobj.read()
            break  # Just one bundle


class RenderDetailsStep(AggregationStep):
    def __init__(
        self,
        *,
        parse_services_step: ParseServicesStep,
        build_javascript_bundle_step: BuildJavascriptBundleStep,
        create_build_dir_step: CreateOutputDirectoryStep,
        create_public_dir_step: CreateOutputDirectoryStep,
        mode: str,
        renderer: Renderer,
        build_dir: str,
        tailwind: Tailwind,
    ) -> None:
        # pylint: disable=too-many-arguments
        super().__init__(
            [
                parse_services_step,
                build_javascript_bundle_step,
                create_build_dir_step,
                create_public_dir_step,
            ]
        )
        self._parse_services_step = parse_services_step
        self._build_javascript_bundle_step = build_javascript_bundle_step
        self._mode = mode
        self._renderer = renderer
        self._build_dir = build_dir
        self._tailwind = tailwind

    def _after_dependencies(self) -> None:
        for service in self._parse_services_step.services:
            self._render(
                service,
                script_name=self._build_javascript_bundle_step.script_name,
                style=self._build_javascript_bundle_step.style,
            )

    def _render(self, service: ServiceInfo, **kwargs) -> None:
        if not service.url:
            return
        kwargs.update({"mode": self._mode, "service": service})
        self._renderer.render_details(f"{self._build_dir}/index.html", **kwargs)
        kwargs["style"] = kwargs.get("style", "") + self.gen_tailwind_css()
        self._renderer.render_details(f"{PUBLIC_DIR}/{service.url}", **kwargs)

    def gen_tailwind_css(self) -> str:
        """Must be called after index.html is rendered"""
        return self._tailwind(
            [f"./{self._build_dir}/index.html", f"./{SOURCE_DIR}/scripts/*.jsx"],
            f"{self._build_dir}/assets/style.css",
        )


class RenderIndexStep(AggregationStep):
    PAGES_DIR = f"{SOURCE_DIR}/pages"

    def __init__(
        self,
        *,
        parse_services_step: ParseServicesStep,
        build_javascript_bundle_step: BuildJavascriptBundleStep,
        create_build_dir_step: CreateOutputDirectoryStep,
        create_public_dir_step: CreateOutputDirectoryStep,
        mode: str,
        renderer: Renderer,
        build_dir: str,
        tailwind: Tailwind,
        load_media_step: LoadMediaStep,
    ) -> None:
        # pylint: disable=too-many-arguments
        super().__init__(
            [
                parse_services_step,
                build_javascript_bundle_step,
                create_build_dir_step,
                create_public_dir_step,
            ]
        )
        self._parse_services_step = parse_services_step
        self._build_javascript_bundle_step = build_javascript_bundle_step
        self._mode = mode
        self._renderer = renderer
        self._build_dir = build_dir
        self._tailwind = tailwind
        self._load_media_step = load_media_step
        self._markdown = MarkdownIt(
            "commonmark",
            {"breaks": True, "html": True},
        )

    def _after_dependencies(self) -> None:
        self._render(
            services=self._parse_services_step.services,
            script_name=self._build_javascript_bundle_step.script_name,
            style=self._build_javascript_bundle_step.style,
            hours=list(self._iter_hours()),
            cancellation_policy=self._load_cancellation_policy(),
            media=self._load_media_step.media,
        )

    def _render(self, **kwargs) -> None:
        kwargs.update({"mode": self._mode})
        self._renderer.render_index(f"{self._build_dir}/index.html", **kwargs)
        kwargs["style"] = kwargs.get("style", "") + self.gen_tailwind_css()
        self._renderer.render_index(f"{PUBLIC_DIR}/index.html", **kwargs)

    def _iter_hours(self) -> Iterable[dict]:
        for line in self._load_media_step.media["7.05"].plain_text.splitlines()[1:]:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                day, hours = parts
                yield {"day": day, "hours": hours}

    def _load_cancellation_policy(self) -> str:
        with open(f"{self.PAGES_DIR}/52-cancellation.md", "rt", encoding="utf-8") as fobj:
            return self._markdown.render(fobj.read())

    def gen_tailwind_css(self) -> str:
        """Must be called after index.html is rendered"""
        return self._tailwind(
            [f"./{self._build_dir}/index.html", f"./{SOURCE_DIR}/scripts/*.jsx"],
            f"{self._build_dir}/assets/style.css",
        )


class BuildAdminStep(AggregationStep):
    ADMIN_DIR = "admin/dist/assets"
    PUBLIC_ASSETS_DIR = f"{PUBLIC_DIR}/assets"

    def __init__(
        self,
        create_public_dir_step: CreateOutputDirectoryStep,
        mode: str,
        tailwind: Tailwind,
    ) -> None:
        super().__init__([create_public_dir_step])
        self._mode = mode
        self._tailwind = tailwind

    def execute(self) -> None:
        subprocess.run(
            ["npm", "run", f"admin{self._mode}"],
            capture_output=True,
            check=True,
        )
        self._tailwind(
            ["./admin/admin.html", "./admin/*.jsx"],
            "admin/dist/assets/admin.css",
        )
        for path in glob.glob(f"{self.ADMIN_DIR}/*.js"):
            shutil.copy(path, f"{self.PUBLIC_ASSETS_DIR}/")
        shutil.copy("admin/dist/admin.html", f"{PUBLIC_DIR}/admin.html")
        shutil.copy(f"{self.ADMIN_DIR}/admin.css", f"{self.PUBLIC_ASSETS_DIR}/")


class PublishImagesStep(AggregationStep):
    def __init__(self, create_public_dir_step: CreateOutputDirectoryStep) -> None:
        super().__init__([create_public_dir_step])
        self.image_publisher = ImagePublisher()

    def execute(self) -> None:
        self.image_publisher.export_images()


class BuildAnythingFactory(StepFactory):
    BUILD_DIR = ".build"
    BUILD_ASSETS_DIR = f"{BUILD_DIR}/assets"
    PUBLIC_ASSETS_DIR = f"{PUBLIC_DIR}/assets"

    def __init__(self, mode: str) -> None:
        self._mode = mode
        self._renderer = Renderer()
        self._tailwind = Tailwind()
        self._load_snippets_step = LoadSnippetsStep(f"{SOURCE_DIR}/7-media/[0-9][0-9]-*.rst")
        self._parse_services_step = ParseServicesStep()
        self._load_media_step = LoadMediaStep(load_snippets_step=self._load_snippets_step)
        self._create_public_dir_step = CreateOutputDirectoryStep(self.PUBLIC_ASSETS_DIR)
        self._create_build_dir_step = CreateOutputDirectoryStep(self.BUILD_ASSETS_DIR)
        self._build_javascript_bundle_step = BuildJavascriptBundleStep(
            embed_javascript_step=EmbedJavascriptStep(
                load_media_step=self._load_media_step,
                target_ptrn=f"{SOURCE_DIR}/scripts/*Template.js",
            ),
            mode=self._mode,
        )

    def create_step(self) -> BuildStep:
        raise NotImplementedError()


class DumpSnippetsFactory(BuildAnythingFactory):
    def create_step(self) -> BuildStep:
        return DumpSnippetsStep(
            parse_services_step=self._parse_services_step,
            load_snippets_step=self._load_snippets_step,
        )


class BuildAdminFactory(BuildAnythingFactory):
    def create_step(self) -> BuildStep:
        return BuildAdminStep(
            create_public_dir_step=self._create_public_dir_step,
            mode=self._mode,
            tailwind=self._tailwind,
        )


class BuildAllFactory(BuildAnythingFactory):
    def create_step(self) -> BuildStep:
        return AggregationStep(
            [
                BuildAdminStep(
                    create_public_dir_step=self._create_public_dir_step,
                    mode=self._mode,
                    tailwind=self._tailwind,
                ),
                RenderDetailsStep(
                    parse_services_step=self._parse_services_step,
                    build_javascript_bundle_step=self._build_javascript_bundle_step,
                    create_public_dir_step=self._create_public_dir_step,
                    create_build_dir_step=self._create_build_dir_step,
                    mode=self._mode,
                    renderer=self._renderer,
                    build_dir=self.BUILD_DIR,
                    tailwind=self._tailwind,
                ),
                RenderIndexStep(
                    parse_services_step=self._parse_services_step,
                    build_javascript_bundle_step=self._build_javascript_bundle_step,
                    create_public_dir_step=self._create_public_dir_step,
                    create_build_dir_step=self._create_build_dir_step,
                    mode=self._mode,
                    renderer=self._renderer,
                    build_dir=self.BUILD_DIR,
                    tailwind=self._tailwind,
                    load_media_step=self._load_media_step,
                ),
                DumpSnippetsStep(
                    parse_services_step=self._parse_services_step,
                    load_snippets_step=self._load_snippets_step,
                ),
                PublishImagesStep(create_public_dir_step=self._create_public_dir_step),
            ]
        )


class Builder:
    FACTORY_CLASSES = {
        "all": BuildAllFactory,
        "admin": BuildAdminFactory,
        "snippets": DumpSnippetsFactory,
    }

    def __init__(self, mode: str) -> None:
        self._factories: dict[str, StepFactory] = {
            name: factory_class(mode=mode) for name, factory_class in self.FACTORY_CLASSES.items()
        }

    @classmethod
    def get_choices(cls) -> list[str]:
        return list(cls.FACTORY_CLASSES)

    def build(self, target: str = "all") -> None:
        self._factories[target].create_step().run_once()
