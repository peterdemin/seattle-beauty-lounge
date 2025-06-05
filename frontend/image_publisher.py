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
            self.export_image(im)

    def export_image(self, im: ImageInfo) -> None:
        target_dir = os.path.dirname(im.public)
        os.makedirs(target_dir, exist_ok=True)
        if os.path.splitext(im.source)[1] != os.path.splitext(im.public)[1]:
            self._export_thumbnail(im.source, im.public)
        else:
            shutil.copy(im.source, im.public)

    def find_images(self) -> Iterable[ImageInfo]:
        for ptrn in self.IMAGE_GLOBS:
            for path in glob.glob(ptrn):
                yield ImageInfo.from_source(path)

    def _export_thumbnail(self, source: str, target: str) -> None:
        image = Image.open(source)
        image.thumbnail(self.SERVICE_IMAGE_MAX_SIZE)
        image.save(target)
