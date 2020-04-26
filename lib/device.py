from logging import getLogger
from struct import pack

from PIL import Image, ImageOps


class Device:
    def __init__(self):
        self._log = getLogger(self.__class__.__name__)

        self.data = bytes()
        self.reset()

    def reset(self):
        self.data = bytes()

    @property
    def pixel_width(self):
        raise NotImplementedError()

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(~{len(self.data)})'

    def _add_invalidate(self):
        self._log.info('adding invalidation statement')
        self.data += b'\x00' * 200

    def _add_initialize(self):
        self._log.info('adding initialization statement')
        self.data += b'\x1B\x40'  # ESC @

    def _add_status_info(self):
        self._log.info('adding status info request statement')
        self.data += b'\x1B\x69\x53'  # ESC i S

    def _add_media_info(self, l_wdt, i_hgt):
        self._log.info('adding media info statement (%d|%d)', l_wdt, i_hgt)
        self.data += b'\x1B\x69\x7A'  # ESC i z

        flags = 0x80
        mtype = bytes([0x0A & 0xFF])
        l_wdt = bytes([l_wdt & 0xFF])
        l_len = bytes([0x00 & 0xFF])
        flags |= (mtype is not None) << 1
        flags |= (l_wdt is not None) << 2
        flags |= (l_len is not None) << 3
        flags |= False << 6
        self.data += bytes([flags])
        self.data += b''.join(b'\x00' if val is None else val for val in (
            mtype, l_wdt, l_len
        ))
        self.data += pack('<L', i_hgt)
        self.data += b'\x00\x00'

    def _add_margin(self, marg):
        self._log.info('adding margin statement (%d)', marg)
        self.data += b'\x1B\x69\x64'  # ESC i d
        self.data += pack('<H', marg)

    def _add_payload(self, stream, width):
        stream = bytes(stream)
        length = len(stream)
        self._log.info('adding payload statements (~%d)', length)

        curr = 0
        row_len = width // 8

        while curr + row_len <= length:
            row = stream[curr:curr + row_len]
            self.data += b'\x67\x00'
            self.data += bytes([len(row)])
            self.data += row
            curr += row_len

    def _add_finalize(self):
        self._log.info('adding finalization statement')
        self.data += b'\x1A'  # EOF

    def feed(self, image, label, rotate=0, threshold=70.0):
        rotate = rotate % 360
        threshold = min(
            255, max(0, int((100 - (threshold % 100)) / 100 * 255))
        )
        self.reset()

        self._add_invalidate()
        self._add_initialize()

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

        self._add_status_info()
        self._add_media_info(label.width, _hgt)
        self._add_margin(label.margin)

        self._log.debug('generating one-bit version of image')
        img = img.convert('L')
        img = ImageOps.invert(img)
        img = img.point(lambda v: 0 if v < threshold else 255, mode='1')
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

        self._add_payload(img.tobytes(encoder_name='raw'), _wdt)
        self._add_finalize()

        return self.data
