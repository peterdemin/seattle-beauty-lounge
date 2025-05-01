import os
import pickle
import posixpath
from dataclasses import dataclass

HERE = os.path.dirname(__file__)
SERVICES_PICKLE = os.path.join(HERE, "services.pkl")
PUBLIC_DIR = "public"


@dataclass
class ImageInfo:
    source: str
    public: str
    url: str

    EXTENSION = ".webp"

    @classmethod
    def from_source(cls, path: str) -> "ImageInfo":
        target_basename = os.path.splitext(os.path.basename(path))[0] + cls.EXTENSION
        return ImageInfo(
            source=path,
            public=os.path.join(PUBLIC_DIR, "images", target_basename),
            url=posixpath.join("images", target_basename),
        )

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


def load_services() -> list[ServiceInfo]:
    with open(SERVICES_PICKLE, "rb") as fobj:
        return pickle.load(fobj)


def dump_services(services: list[ServiceInfo]) -> None:
    with open(SERVICES_PICKLE, "wb") as fobj:
        pickle.dump(services, fobj)
