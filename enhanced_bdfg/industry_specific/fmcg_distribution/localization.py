"""Ethiopian calendar, ETB, and Amharic/English strings for Alarm CRM."""

from __future__ import annotations

from datetime import date, datetime
from typing import Union

STRINGS = {
    "en": {
        "assistant_name": "Alarm CRM assistant",
        "dark_territory": "Under-covered neighborhoods (low orders vs kiosk density)",
        "do_not_roll": "Do not dispatch: confirmed demand is below the batch threshold.",
        "dispatch_ok": "Batch threshold met — schedule a vehicle.",
    },
    "am": {
        "assistant_name": "የአላርም CRM ረዳት",
        "dark_territory": "ያነሰ ትዕዛዝ ያላቸው ሰፈሮች",
        "do_not_roll": "አትላክ፦ የተረጋገጠ ፍላጎት ከጭነት ደረጃ በታች ነው።",
        "dispatch_ok": "የጭነት ደረጃ ተሟልቷል — ተሽከርካሪ ቀጠሮ ይያዝ።",
    },
}

ETB = "ETB"


def t(key: str, language: str = "en") -> str:
    lang = "am" if language in ("am", "amh", "amharic") else "en"
    return STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))


def to_ethiopian_date(d: Union[date, datetime, None] = None) -> dict:
    """
    Convert a Gregorian date to Ethiopian calendar (approx. civil conversion).

    Ethiopian New Year is 11 September (12 September after Gregorian leap years).
    """
    if d is None:
        d = date.today()
    if isinstance(d, datetime):
        d = d.date()
    greg_new_year = date(d.year, 9, 12 if _gregorian_leap(d.year) else 11)
    if d >= greg_new_year:
        eth_year = d.year - 7
        start = greg_new_year
    else:
        eth_year = d.year - 8
        start = date(d.year - 1, 9, 12 if _gregorian_leap(d.year - 1) else 11)
    delta = (d - start).days
    month = min(13, delta // 30 + 1)
    day = delta % 30 + 1
    return {"year": eth_year, "month": month, "day": day, "iso": f"{eth_year:04d}-{month:02d}-{day:02d}"}


def format_etb(amount: float) -> str:
    return f"{amount:,.2f} {ETB}"


def _gregorian_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
