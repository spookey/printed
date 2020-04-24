from collections import namedtuple
from logging import getLogger
from time import sleep

from usb.core import find
from usb.util import (
    ENDPOINT_IN, ENDPOINT_OUT, endpoint_direction, find_descriptor
)

DESCRS = namedtuple('Descriptors', ('push', 'pull'))
PRODID = 0x2015
VENDOR = 0x04f9


class Printer:
    def __init__(self):
        self._log = getLogger(self.__class__.__name__)

        self.device = find(idVendor=VENDOR, idProduct=PRODID)
        self.__desc = None
        self.__d_to = DESCRS(push=10, pull=15000)

        if self.device is not None:
            self.device.set_configuration()

    @property
    def present(self):
        return self.device is not None

    @property
    def product(self):
        return getattr(self.device, 'product', None)

    @property
    def serial_number(self):
        return getattr(self.device, 'serial_number', None)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}({self.product} {self.serial_number})'

    @property
    def _desc(self):
        def _locate(conf, direction):
            interface = find_descriptor(conf, bInterfaceClass=0x7)
            return find_descriptor(interface, custom_match=lambda dscr: (
                endpoint_direction(dscr.bEndpointAddress) == direction
            ))

        if not self.present:
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
        if not self.present:
            self._log.warning('Printer is not connected')
            return None

        tries = 3
        for num in range(1, 1 + tries):
            self._log.debug('reading data (attempt %d/%d)', num, tries)

            data = bytes(self._desc.pull.read(length))
            if data:
                return data
            sleep(self.__d_to.pull / 1000)

        self._log.info('nothing received')
        return None

    def push(self, data):
        if not self.present:
            self._log.warning('Printer is not connected')
            return
        self._desc.push.write(data, self.__d_to.push)
