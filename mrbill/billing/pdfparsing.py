import re
from dateutil.parser import parse
from decimal import Decimal, InvalidOperation


def parse_amt(txt):
    result = re.sub('[^0-9\,\.]', '', txt)
    result = result.replace(',', '.')
    try:
        return Decimal(result)
    except ValueError:
        return None
    except InvalidOperation:
        return None


def parse_date(txt):
    result = re.sub('[^0-9\/\\\]', '', txt)
    if '\\' in result:
        result = result.replace('\\', '/')
    try:
        return parse(result)
    except ValueError:
        return None
