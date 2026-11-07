import calendar
from datetime import date

from config import MONTHS, START_MONTH


def parse_ym(ym):
    year, month = ym.split("-")
    return int(year), int(month)


def add_months(ym, n):
    year, month = parse_ym(ym)
    total = year * 12 + (month - 1) + n
    return f"{total // 12:04d}-{total % 12 + 1:02d}"


def ym_of(d):
    return f"{d.year:04d}-{d.month:02d}"


def month_first(ym):
    year, month = parse_ym(ym)
    return date(year, month, 1)


def month_last(ym):
    year, month = parse_ym(ym)
    return date(year, month, calendar.monthrange(year, month)[1])


def month_label(ym):
    year, month = parse_ym(ym)
    return f"{MONTHS[month - 1]} {year}"


def month_short(ym):
    return MONTHS[parse_ym(ym)[1] - 1][:3]


def current_month():
    return max(START_MONTH, ym_of(date.today()))


def max_month():
    return add_months(current_month(), 36)


def money(x):
    sign = "-" if x < -0.004 else ""
    return f"{sign}${abs(x):,.2f}"


def money0(x):
    sign = "-" if x < -0.5 else ""
    return f"{sign}${abs(x):,.0f}"


def parse_amount(text):
    # returns None when the text is not a number
    if text is None:
        return None
    clean = str(text).replace("$", "").replace(",", "").strip()
    if clean == "":
        return None
    try:
        return float(clean)
    except ValueError:
        return None


def parse_iso(text):
    try:
        return date.fromisoformat(str(text)[:10])
    except (TypeError, ValueError):
        return None
