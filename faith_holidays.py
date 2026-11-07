"""Faith holidays for LooscidBOT.

These are posted only in the faith channels (for example English #muslim-community),
which only people who picked BOTH that language and that faith can see. No pings, ever.

Dates are computed every year from libraries, nothing is hand-typed per year:
- Islamic dates: hijridate (Umm al-Qura calendar). Moon sighting can move them by a day.
- Christian: dateutil's Western and Orthodox Easter, fixed Christmas dates.
- Hindu and Sikh: the holidays library's India calendar (optional categories).
- Jewish: the holidays library's Israel calendar (first day of each holiday).
  Jewish holidays begin at sundown the evening before.
- Buddhist: Vesak from the holidays library's Singapore calendar, Magha Puja and
  Asalha Puja from its Thailand calendar. Some countries mark Vesak on a different day.
"""

import json
import os
from datetime import date, timedelta

import holidays
from dateutil.easter import EASTER_ORTHODOX, EASTER_WESTERN, easter

from holidays_rules import fixed, hijri

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "faiths.json"), encoding="utf-8") as f:
    FAITHS = json.load(f)


def first_days(country, name, **kwargs):
    """The first day of each run of days the holidays library calls `name`."""
    def rule(year):
        cal = country(years=[year - 1, year], **kwargs)
        days = {d for d, n in cal.items() if name in [x.strip() for x in n.split(";")]}
        return sorted(d for d in days if d.year == year and d - timedelta(days=1) not in days)
    return rule


def orthodox_easter(year):
    d = easter(year, EASTER_ORTHODOX)
    return [] if d == easter(year, EASTER_WESTERN) else [d]  # same day as Easter: one post


INDIA = dict(categories=holidays.India.supported_categories, language="en_IN")
ISRAEL = dict(categories=holidays.Israel.supported_categories, language="en_US")
THAI = dict(categories=holidays.Thailand.supported_categories, language="en_US")

RULES = {
    "christmas": fixed(12, 25),
    "orthodox_christmas": fixed(1, 7),
    "easter": lambda y: [easter(y, EASTER_WESTERN)],
    "orthodox_easter": orthodox_easter,
    "ramadan_start": hijri(9, 1),
    "eid_al_fitr": hijri(10, 1),
    "eid_al_adha": hijri(12, 10),
    "islamic_new_year": hijri(1, 1),
    "maha_shivaratri": first_days(holidays.India, "Maha Shivaratri", **INDIA),
    "holi": first_days(holidays.India, "Holi", **INDIA),
    "raksha_bandhan": first_days(holidays.India, "Raksha Bandhan", **INDIA),
    "janmashtami": first_days(holidays.India, "Janmashtami (Vaishnava)", **INDIA),
    "ganesh_chaturthi": first_days(holidays.India, "Ganesh Chaturthi / Vinayak Chaturthi", **INDIA),
    "dussehra": first_days(holidays.India, "Dussehra", **INDIA),
    "diwali": first_days(holidays.India, "Diwali (Deepavali)", **INDIA),
    "magha_puja": first_days(holidays.Thailand, "Makha Bucha", **THAI),
    "vesak": lambda y: first_days(holidays.Singapore, "Vesak Day")(y)
    or first_days(holidays.India, "Buddha Purnima", **INDIA)(y),  # India's date where Singapore's runs out
    "asalha_puja": first_days(holidays.Thailand, "Asarnha Bucha", **THAI),
    "purim": first_days(holidays.Israel, "Purim", **ISRAEL),
    "passover": first_days(holidays.Israel, "Pesach", **ISRAEL),
    "shavuot": first_days(holidays.Israel, "Shavuot", **ISRAEL),
    "rosh_hashanah": first_days(holidays.Israel, "Rosh Hashanah", **ISRAEL),
    "sukkot": first_days(holidays.Israel, "Sukkot", **ISRAEL),
    "hanukkah": first_days(holidays.Israel, "Hanukkah", **ISRAEL),
    "guru_gobind_singh": first_days(holidays.India, "Guru Gobind Singh's Jayanti", **INDIA),
    "vaisakhi": first_days(holidays.India, "Vaisakhi", **INDIA),
    "bandi_chhor": first_days(holidays.India, "Diwali (Deepavali)", **INDIA),  # same day as Diwali
    "guru_nanak": first_days(holidays.India, "Guru Nanak's Jayanti", **INDIA),
}


def message(language, holiday):
    template = FAITHS["languages"][language]["message"]
    return template.format(e=holiday["emoji"], n=holiday["names"][language])


def faith_holidays_on(day):
    """{faith: [holiday, ...]} for this day."""
    found = {}
    for faith, entries in FAITHS["holidays"].items():
        for h in entries:
            if day in RULES[h["key"]](day.year):
                found.setdefault(faith, []).append(h)
    return found


def faith_upcoming(start, days):
    """[(date, faith, English name)] from start for this many days."""
    end = start + timedelta(days=days)
    out = set()
    for faith, entries in FAITHS["holidays"].items():
        for h in entries:
            for year in {start.year, end.year}:
                for d in RULES[h["key"]](year):
                    if start <= d <= end:
                        out.add((d, faith, h["names"]["English"]))
    return sorted(out)
