from logging import getLogger
from struct import pack

from PIL import Image, ImageOps


class Device:
    def __init__(self):
        self._log = getLogger(self.__class__.__name__)

    @property
    def pixel_width(self):
        raise NotImplementedError()

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}()'

    def _make_invalidate(self):
        self._log.info('creating invalidation statement')
        return b'\x00' * 200

    def _make_initialize(self):
        self._log.info('creating initialization statement')
        return b'\x1B\x40'  # ESC @

    def _make_status_info(self):
        self._log.info('creating status info request statement')
        return b'\x1B\x69\x53'  # ESC i S

    def _make_media_info(self, label_width, image_height):
        self._log.info(
            'creating media info statement (%d|%d)',
            label_width, image_height
        )

        flags = 0x80
        flags |= True << 1  # media type
        flags |= True << 2  # label width
        flags |= True << 3  # label length
        flags |= False << 6  # high quality

        data = b'\x1B\x69\x7A'  # ESC i z
        data += bytes([
            flags,
            0x0A & 0xFF,  # media type
            label_width & 0xFF,  # label width
            0x00 & 0xFF,  # label length
        ])
        data += pack('<L', image_height)
        data += b'\x00'  # page number
        data += b'\x00'

        return data

    def _make_margin(self, margin):
        self._log.info('creating margin statement (%d)', margin)
        data = b'\x1B\x69\x64'  # ESC i d
        data += pack('<H', margin)
        return data

    def _make_payload(self, stream, width):
        total = len(stream)
        self._log.info('creating payload statements (~%d)', total)

        data = b''
        curr = 0
        size = width // 8

        while curr + size <= total:
            line = stream[curr:curr + size]
            data += b'\x67\x00'
            data += bytes([len(line)])
            data += line
            curr += size

        return data

    def _make_finalize(self):
        self._log.info('creating finalization statement')
        return b'\x1A'  # EOF

    def convert(
            self, *,
            image, label, rotate=0, threshold=70.0
    ):
        rotate = rotate % 360
        threshold = min(
            255, max(0, int((100 - (threshold % 100)) / 100 * 255))
        )

        img = Image.open(image)

        if img.mode.endswith('A'):
            self._log.debug('dropping alpha channel of image')
            pst = Image.new('RGB', img.size, (255, 255, 255))
            pst.paste(img, box=None, mask=img.split()[-1])
            img = pst

        if img.mode == 'P':
            self._log.debug('converting image mode')
            img = img.convert('RGB')

        if rotate != 0:
            self._log.info('rotating image by %d°', rotate)
            img = img.rotate(rotate, expand=True)

        _wdt, _hgt = img.size
        if _wdt != label.printable:
            _ndt, _ngt = label.printable, int((label.printable / _wdt) * _hgt)
            self._log.info(
                'resizing image from (%d|%d) to (%d|%d)',
                _wdt, _hgt, _ndt, _ngt
            )
            img = img.resize((_ndt, _ngt), Image.ANTIALIAS)
            _wdt, _hgt = img.size

        if _wdt < self.pixel_width:
            _ndt, _ngt = self.pixel_width - _wdt - label.offset, 0
            self._log.info(
                'repositioning image to (%d|%d)',
                _ndt, _ngt
            )
            pst = Image.new('RGB', (self.pixel_width, _hgt), (255, 255, 255))
            pst.paste(img, box=(_ndt, _ngt))
            img = pst
            _wdt, _hgt = img.size

        self._log.debug('generating one-bit version of image')
        img = img.convert('L')
        img = ImageOps.invert(img)
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

        img = img.point(lambda v: 0 if v < threshold else 255, mode='1')

        return img.tobytes(encoder_name='raw'), _wdt, _hgt

    def feed(self, *, image, label, **kwargs):
        stream, width, height = self.convert(
            image=image, label=label, **kwargs
        )

        return b''.join((
            self._make_invalidate(),
            self._make_initialize(),
            self._make_status_info(),
            self._make_media_info(label.width, height),
            self._make_margin(label.margin),
            self._make_payload(stream, width),
            self._make_finalize(),
        ))
