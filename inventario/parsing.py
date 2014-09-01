import xlrd

from collections import defaultdict

ID = 'ID'
POS = 'POS'
TITLE = 'TEMA'
LANG = 'IDIOMA'
SUPPORT = 'SOPORTE'
ERROR = 'ERROR DE COPIA'
UNKNOWN = 'NO IDENTIFICADO'
REPEATED = 'SE REPITE EN EL INVENTARIO'


def parse_value(cell):
    if cell.ctype is 1:
        return cell.value.strip()
    elif cell.ctype is 2:
        return int(cell.value) if cell.value.is_integer() else cell.value

    return cell.value


def parse_row(row):
    return [parse_value(cell) for cell in row]


def parse_row_data(header, row):
    if len(row) != len(header):
        raise Exception('Row and header differs in size')

    return dict(zip(header, parse_row(row)))


def parse_rows(sheet):
    header = parse_row(sheet.row(0))

    nparsed = 0
    for line in range(1, sheet.nrows):
        try:
            data = parse_row_data(header, sheet.row(line))
            data[POS] = nparsed
            yield data
        except Exception as error:
            raise Exception('Error while parsing "{}" line "{}": {}'
                            .format(sheet.name, line, error))
        else:
            nparsed += 1


def get_entries_by_id(entries):
    d = defaultdict(list)

    for data in entries:
        d[data[ID]].append(data)

    return d


def get_diff(old, new):
    old, new = set(old), set(new)

    added = new - old
    removed = old - new
    unchanged = old & new

    return added, removed, unchanged


def open_book(filename):
    book = xlrd.open_workbook(filename)
    pages = book.nsheets
    return book, pages


class Page(object):
    def __init__(self, n, sheet):
        self.n = n
        self.sheet = sheet
        self.name  = sheet.name
        self.nrows = sheet.nrows
        self._entries = None
        self._entries_by_id = None

    @property
    def entries(self):
        if self._entries is None:
            self._entries = list(parse_rows(self.sheet))
        return self._entries

    @property
    def entries_by_id(self):
        if self._entries_by_id is None:
            self._entries_by_id = get_entries_by_id(self.entries)
        return self._entries_by_id

    def diff(self, page):
        return get_diff(self.entries_by_id.keys(), page.entries_by_id.keys())


class Book(object):
    def __init__(self, filename):
        self.filename = filename
        self.book, self.npages = open_book(filename)

    @property
    def pages(self):
        return (self.page(n) for n in range(self.npages))

    def page(self, n):
        return Page(n, self.book.sheet_by_index(n))
