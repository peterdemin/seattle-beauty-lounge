import datetime
import os
import pickle
import posixpath
from dataclasses import dataclass

HERE = os.path.dirname(__file__)
CONTENT_PICKLE = os.path.join(HERE, "content.pkl")
PUBLIC_DIR = "public"
FAVICON = "favicon.ico"


@dataclass
class ImageInfo:
    source: str
    public: str
    url: str

    EXTENSION = ".webp"

    @classmethod
    def from_source(cls, path: str) -> "ImageInfo":
        target_basename = (
            os.path.basename(path)
            if os.path.basename(path).startswith("0")
            else os.path.splitext(os.path.basename(path))[0] + cls.EXTENSION
        )
        if target_basename.endswith(FAVICON):
            public = os.path.join(PUBLIC_DIR, FAVICON)
            url = FAVICON
        else:
            public = os.path.join(PUBLIC_DIR, "images", target_basename)
            url = posixpath.join("images", target_basename)
        return ImageInfo(source=path, public=public, url=url)

    @classmethod
    def dummy(cls) -> "ImageInfo":
        return cls(source="", public="", url="")


@dataclass
class ServiceInfo:
    source_path: str
    image: ImageInfo
    title: str = ""
    price: str = ""
    price_cents: int = 0
    duration: str = ""
    duration_min: int = 0
    short_text: str = ""
    full_html: str = ""
    url: str = ""

    CATEGORY_NAMES = {
        "1": "Facials",
        "2": "Lashes & Brows",
        "3": "Makeup",
    }
    REQUIRED_FIELDS = [
        "basename",
        "title",
        "price",
        "price_cents",
        "duration",
        "duration_min",
        "short_text",
    ]

    def check_missing_fields(self) -> list[str]:
        return [f for f in self.REQUIRED_FIELDS if not getattr(self, f)]

    def set_image_from_uri(self, uri: str) -> None:
        self.image = ImageInfo.from_source(os.path.join(os.path.dirname(self.source_path), uri))

    @property
    def basename(self) -> str:
        return os.path.splitext(os.path.basename(self.source_path))[0]

    @property
    def full_index(self) -> str:
        return f"{self.category_index}.{self.index}"

    @property
    def index(self) -> str:
        return os.path.basename(self.source_path).split("-")[0]

    @property
    def category_index(self) -> str:
        return os.path.basename(os.path.dirname(self.source_path)).split("-")[0]

    @property
    def category_name(self) -> str:
        return self.CATEGORY_NAMES[self.category_index]

    @property
    def delta(self) -> datetime.timedelta:
        return datetime.timedelta(minutes=self.duration_min)


@dataclass
class Snippet:
    full_index: str
    html: str
    plain_text: str


@dataclass
class Content:
    services: list[ServiceInfo]
    snippets: list[Snippet]

    def get_snippet(self, full_index: str) -> Snippet:
        return {s.full_index: s for s in self.snippets}[full_index]


def load_content() -> Content:
    with open(CONTENT_PICKLE, "rb") as fobj:
        return pickle.load(fobj)


def load_services() -> list[ServiceInfo]:
    return load_content().services


def dump_content(services: list[ServiceInfo], snippets: list[Snippet]) -> None:
    with open(CONTENT_PICKLE, "wb") as fobj:
        pickle.dump(Content(services=services, snippets=snippets), fobj)
