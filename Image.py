from PyQt5.QtGui import QImage
from PIL import Image as PILImage, ImageOps
import numpy as np

class Image:
    def __init__(self, path):
        self.original = PILImage.open(path).convert('RGBA')
        self.transformed = self.original.copy()
        self._qimage_cache = None

    def scale(self, sx, sy=None):
        if sy is None:
            sy = sx
        new_size = (int(self.original.width * sx), int(self.original.height * sy))
        self.transformed = self.original.resize(new_size, PILImage.ANTIALIAS)
        self._qimage_cache = None  # Invalida o cache
        return self

    def rotate(self, angle):
        self.transformed = self.transformed.rotate(angle, expand=True)
        self._qimage_cache = None
        return self

    def flip(self, horizontal=False, vertical=False):
        if horizontal:
            self.transformed = ImageOps.mirror(self.transformed)
        if vertical:
            self.transformed = ImageOps.flip(self.transformed)
        self._qimage_cache = None
        return self

    def to_qimage(self):
        if self._qimage_cache is None:
            data = self.transformed.tobytes("raw", "RGBA")
            w, h = self.transformed.size
            self._qimage_cache = QImage(data, w, h, QImage.Format_RGBA8888)
        return self._qimage_cache
