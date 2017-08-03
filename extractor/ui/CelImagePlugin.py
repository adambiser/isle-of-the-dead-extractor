#
# Handles CEL graphic files used by the game Isle of the Dead.
#

from PIL import Image,ImageFile,ImagePalette
import os

class CelImageFile(ImageFile.ImageFile):
    format = "CEL"
    format_description = "CEL raster image"
    TOP = 0
    LEFT = 1 # Requires a square image to work correctly.

    def _open(self):
        # Must have .cel as the extension.
        if os.path.splitext(self.filename)[1].lower() != '.cel':
            raise SyntaxError("not a CEL file")
        self.mode = 'P'
        data = self.fp.read(2)
        if data == b'\x19\x91':
            width = int.from_bytes(self.fp.read(2), byteorder='little', signed=False)
            height = int.from_bytes(self.fp.read(2), byteorder='little', signed=False)
            self.fp.seek(0x20)
            self.loadvgapalette(self.fp)
            self.size = (width, height)
            self.tile = [('raw', (0, 0) + self.size, 0x320, (CelImageFile.TOP))]
        else:
            # This format must have a file size of 4096 (64x64).
            if os.stat(self.filename).st_size != 4096:
                raise SyntaxError("not a CEL file")
            self.loadpalette()
            self.size = (64, 64)
            self.tile = [('raw', (0, 0) + self.size, 0, (CelImageFile.LEFT))]

    def loadvgapalette(self, fp):
        pal = [x * 4 for x in fp.read(768)]
        self.palette = ImagePalette.raw(None, pal[0::3] + pal[1::3] + pal[2::3])

    def loadpalette(self):
        # There should be a PALETTE.PAL file in the same folder as the image file.
        palfile = os.path.join(os.path.dirname(self.filename), 'PALETTE.PAL')
        if not os.path.isfile(palfile):
            raise SyntaxError("could not find palette for CEL file")
        with open(palfile, 'rb') as f:
            self.loadvgapalette(f)

    def load(self):
        if self.tile is None:
            raise IOError("Cannot load this image")
        decoder_name, extents, offset, orientation = self.tile[0]
        self.im = Image.core.new(self.mode, self.size)
        self.fp.seek(offset)
        data = self.fp.read(self.size[0] * self.size[1])
        if orientation == CelImageFile.LEFT:
            data = bytes([x for y in [data[z::self.size[0]] for z in range(self.size[1])] for x in y])
        self.frombytes(data)

#
# Register
#

Image.register_open(CelImageFile.format, CelImageFile)
Image.register_extension(CelImageFile.format, '.cel')
