FACTOR = 11.8074


class Label:
    def __init__(self, width, offset):
        self.width = width
        self.offset = offset

    @property
    def name(self):
        return f'{self.width}mm endless'

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}({self.name})'

    @property
    def margin(self):
        return 35

    @property
    def total(self):
        return round(self.width * FACTOR)

    @property
    def printable(self):
        return self.total - self.margin - 1


# pylint: disable=bad-whitespace
LABELS = {f'{label.width}': label for label in (
    Label(12, 29),
    Label(29,  6),
    Label(38, 12),
    Label(50, 12),
    Label(54,  0),
    Label(62, 12),
)}
