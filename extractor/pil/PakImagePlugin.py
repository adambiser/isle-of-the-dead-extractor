#
# PAK file handler for Pillow.
#

from PIL import Image, ImageFile, ImagePalette
import os
from .CelImagePlugin import CelImageFile


class PakImageFile(CelImageFile):
    """
    Image plugin for PAK graphic files used by the game Isle of the Dead V1.29.

    These files group a bunch of column-major CEL images together.
    """
    format = "PAK"
    format_description = "PAK raster image"

    def _open(self):
        # Must have .pak as the extension.
        if os.path.splitext(self.filename)[1].lower() != ".pak":
            raise SyntaxError("not a PAK file")
        # This format must have a file size of 4096 (64x64).
        filesize = os.stat(self.filename).st_size
        if filesize % 4096 != 0:
            raise SyntaxError("not a PAK file")
        self._frameocunt = filesize // 4096
        self._frame = -1
        self.mode = "P"
        self.loadpalette()
        self.size = (64, 64)
        #
        self.seek(0)

    @property
    def n_frames(self):
        return self._frameocunt


    @property
    def is_animated(self):
        return self._frameocunt > 1


    def seek(self, frame):
        if frame == self._frame:
            return
        if frame >= self._frameocunt:
            raise EOFError("no more images in PAK file")
        self._frame = frame
        self.tile = [("raw", (0, 0) + self.size, frame * 4096, CelImageFile.LEFT)]
#
# Register
#

Image.register_open(PakImageFile.format, PakImageFile)
Image.register_extension(PakImageFile.format, ".pak")
