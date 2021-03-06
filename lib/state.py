from logging import getLogger

LOG = getLogger(__name__)

FIXD = [
    (0x00, 'null'),
    (0x30, 'zero'),
]
ERR1 = [
    (0x00, 'no media'),
    (0x01, 'end of media'),
    (0x02, 'tape cutter jam'),
    (0x03, 'not used'),
    (0x04, 'main unit in use'),
    (0x05, 'printer turned off'),
    (0x06, 'high-voltage adapter'),
    (0x07, 'fan issue'),
]
ERR2 = [
    (0x00, 'replace media'),
    (0x01, 'expansion buffer exhausted'),
    (0x02, 'communication error'),
    (0x03, 'communication buffer exhausted'),
    (0x04, 'cover open'),
    (0x05, 'cancel key'),
    (0x06, 'media feed'),
    (0x07, 'system error'),
]
MEDT = [
    (0x00, 'no media'),
    (0x0a, 'continuous length tape'),
    (0x0b, 'die-cut labels'),
]
STAT = [
    (0x00, 'reply to status request'),
    (0x01, 'printing completed'),
    (0x02, 'error occurred'),
    (0x05, 'notification'),
    (0x06, 'phase change'),
]
PHST = [
    (0x00, 'waiting to receive'),
    (0x01, 'printing state'),
]
BITS = [
    (0x80, 'head'),                     # 00
    (0x20, 'size'),                     # 01
    (0x42, 'fixed'),                    # 02
    (None, 'device dependent'),         # 03
    (None, 'device dependent'),         # 04
    (0x30, 'fixed'),                    # 05
    (FIXD, 'fixed'),                    # 06
    (0x00, 'fixed'),                    # 07
    (ERR1, 'error bit 1'),              # 08
    (ERR2, 'error bit 2'),              # 09
    (None, 'media width'),              # 10
    (MEDT, 'media type'),               # 11
    (0x00, 'fixed'),                    # 12
    (0x00, 'fixed'),                    # 13
    (None, 'reserved'),                 # 14
    (None, 'mode'),                     # 15
    (0x00, 'fixed'),                    # 16
    (None, 'media length'),             # 17
    (STAT, 'status type'),              # 18
    (PHST, 'phase type'),               # 19
    (None, 'phase number high'),        # 20
    (None, 'phase number low'),         # 21
    (None, 'notification number'),      # 22
    (None, 'reserved'),                 # 23
    (None, 'reserved'),                 # 24
    (None, 'padding'),                  # 25
    (None, 'padding'),                  # 26
    (None, 'padding'),                  # 27
    (None, 'padding'),                  # 28
    (None, 'padding'),                  # 29
    (None, 'padding'),                  # 30
    (None, 'padding'),                  # 31
]


class Bit:
    def __init__(self, pos, ident):
        self.pos = pos
        self.ident = ident

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(#{self.pos:02d} {self.ident})'

    def nested(self, ident):
        return Bit(self.pos, f'{self.ident} - {ident}')

    def format(self, value, payload=None):
        pay = f'0x{payload:02x}' if payload is not None else '----'
        return f'0x{value:02x} {pay} {self}'

    def unroll(self, value, payload):
        if payload is not None:
            if isinstance(payload, (list, tuple)):
                for val, ident in ((v, i) for v, i in payload if v == value):
                    return self.nested(ident).unroll(value, val)
                return self.nested('unknown value').unroll(value, 0xff)
            return payload == value, self.format(value, payload)
        return True, self.format(value)

    @classmethod
    def dump(cls, data):
        if data is None or len(data) != 32:
            return False

        result = [
            cls(pos, ident).unroll(data[pos], payload)
            for pos, (payload, ident) in enumerate(BITS)
        ]
        LOG.info('\n'.join(res[1] for res in result))
        return all(res[0] for res in result)
