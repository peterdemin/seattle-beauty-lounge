import glob
import os
import shutil
from typing import Iterable

from PIL import Image

from lib.service import ImageInfo

from .constants import SOURCE_DIR


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
