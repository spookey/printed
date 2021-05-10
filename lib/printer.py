from collections import namedtuple
from time import sleep

from usb.core import find
from usb.util import (
    ENDPOINT_IN,
    ENDPOINT_OUT,
    endpoint_direction,
    find_descriptor,
)

from lib.device import Device

PRODID = 0x2015
VENDOR = 0x04f9

DESCRS = namedtuple('Descriptors', ('push', 'pull'))
TIMEOUT = DESCRS(push=15000, pull=10)


class Printer(Device):
    def __init__(self):
        super().__init__()

        self.device = find(idVendor=VENDOR, idProduct=PRODID)
        self.__desc = None

        if self.device is not None:
            self.device.set_configuration()

    def present(self, silent=False):
        if self.device is not None:
            return True
        if not silent:
            self._log.error('not connected')
        return False

    @property
    def product(self):
        return getattr(self.device, 'product', None)

    @property
    def serial_number(self):
        return getattr(self.device, 'serial_number', None)

    def __repr__(self):
        cls_name = self.__class__.__name__
        spec = ' '.join(el for el in (self.product, self.serial_number) if el)
        return f'{cls_name}({spec})'

    @property
    def bytes_per_row(self):
        return 90

    @property
    def pixel_width(self):
        return self.bytes_per_row * 8

    @property
    def _desc(self):
        def _locate(conf, direction):
            interface = find_descriptor(conf, bInterfaceClass=0x7)
            return find_descriptor(interface, custom_match=lambda dscr: (
                endpoint_direction(dscr.bEndpointAddress) == direction
            ))

        if not self.present(silent=True):
            return None
        if not self.__desc:
            self._log.debug('determining descriptors of %s', self)

            conf = self.device.get_active_configuration()
            self.__desc = DESCRS(
                push=_locate(conf, ENDPOINT_OUT),
                pull=_locate(conf, ENDPOINT_IN),
            )
        return self.__desc

    def pull(self, length=32):
        if not self.present(silent=False):
            return None

        tries = 3
        for num in range(1, 1 + tries):
            self._log.debug('reading data (attempt %d/%d)', num, tries)

            data = bytes(self._desc.pull.read(length))
            if data:
                return data
            sleep(TIMEOUT.pull / 1000)

        self._log.info('nothing received')
        return None

    def push(self, data):
        if not self.present(silent=False):
            return
        self._desc.push.write(data, TIMEOUT.push)

    def __call__(self, *, image, label, preview=False, **kwargs):
        payload = self.feed(
            image=image, label=label, preview=preview, **kwargs,
        )
        if preview:
            self._log.debug('preview mode - skipping print')
            return

        if not self.present(silent=False):
            return

        self.push(payload)
