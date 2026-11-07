"""Holiday rules for LooscidBOT.

Every language has its own list. A holiday only ever gets posted in its own
language's channels. Dates are computed every year from well-known libraries,
so nothing here needs updating when the year changes:

- Islamic dates: hijridate (Umm al-Qura calendar).
- Chinese lunar dates: lunardate.
- Korean lunar dates (Seollal, Chuseok): the holidays library's South Korea calendar.
- Hindu festivals (Holi, Raksha Bandhan, Dussehra, Diwali): the holidays library's India calendar.
- Easter and the days around it: dateutil (Western and Orthodox).
- Everything else is a fixed day or a simple rule, like "fourth Thursday of November".
"""

from datetime import date, timedelta

import holidays
from dateutil.easter import EASTER_ORTHODOX, EASTER_WESTERN, easter
from hijridate import Hijri
from lunardate import LunarDate


# ---------- date helpers (each takes a Gregorian year, returns a list of dates) ----------

def fixed(month, day):
    return lambda year: [date(year, month, day)]


def easter_offset(days, method=EASTER_WESTERN):
    return lambda year: [easter(year, method) + timedelta(days=days)]


def nth_weekday(month, weekday, n):
    """weekday: Monday=0 ... Sunday=6. n: 1 = first, 4 = fourth."""
    def rule(year):
        first = date(year, month, 1)
        shift = (weekday - first.weekday()) % 7
        return [first + timedelta(days=shift + 7 * (n - 1))]
    return rule


def hijri(month, day):
    """An Islamic calendar date, for every time it falls in this Gregorian year."""
    def rule(year):
        found = []
        approx = year - 579  # roughly the Hijri year that starts in this Gregorian year
        for hy in (approx - 1, approx, approx + 1):
            try:
                g = Hijri(hy, month, day).to_gregorian()
            except (ValueError, OverflowError):
                continue
            g = date(g.year, g.month, g.day)
            if g.year == year:
                found.append(g)
        return found
    return rule


def chinese_lunar(month, day):
    def rule(year):
        try:
            return [LunarDate(year, month, day).toSolarDate()]
        except ValueError:
            return []
    return rule


def from_holidays_lib(country, name, **kwargs):
    """Look up one holiday by its exact name in the holidays library."""
    def rule(year):
        cal = country(years=year, **kwargs)
        return sorted(d for d, n in cal.items() if name in [x.strip() for x in n.split(";")])
    return rule


INDIA = dict(categories=holidays.India.supported_categories, language="en_IN")


# ---------- the holidays, per language ----------
# Each entry: (name in English, rule, message in that language)

HOLIDAYS = {
    "English": [
        ("New Year's Day", fixed(1, 1), "Happy New Year, Looscid! 🎆 Wishing everyone an amazing year ahead."),
        ("Pancake Day / Mardi Gras", easter_offset(-47), "Happy Pancake Day and Mardi Gras! 🥞 What's your favourite topping?"),
        ("Easter", easter_offset(0), "Happy Easter, everyone! 🐣 Hope your day is full of sunshine and chocolate."),
        ("Independence Day (US)", fixed(7, 4), "Happy Fourth of July! 🎆 Have a fun and safe day, everyone."),
        ("Halloween", fixed(10, 31), "Happy Halloween! 🎃 Tell us about your costume!"),
        ("Bonfire Night (UK)", fixed(11, 5), "Happy Bonfire Night! 🎇 Enjoy the fireworks, everyone."),
        ("Thanksgiving (US)", nth_weekday(11, 3, 4), "Happy Thanksgiving! 🦃 Thankful for every single one of you here."),
        ("Christmas", fixed(12, 25), "Merry Christmas, Looscid! 🎄 Wishing you a cosy, happy day."),
    ],
    "Español": [
        ("New Year's Day", fixed(1, 1), "¡Feliz Año Nuevo, Looscid! 🎆 Que este año venga lleno de cosas buenas."),
        ("Three Kings' Day", fixed(1, 6), "¡Feliz Día de Reyes! 👑 ¿A quién le tocó la sorpresa de la rosca?"),
        ("Easter", easter_offset(0), "¡Feliz Pascua! 🐣 Que tengan un día lleno de alegría."),
        ("Spanish Language Day", fixed(4, 23), "¡Feliz Día del Idioma Español! 📚 Gracias por hablar español aquí con nosotros."),
        ("Day of the Dead", fixed(11, 2), "¡Feliz Día de Muertos! 🌼🕯️ Hoy recordamos con cariño a nuestros seres queridos."),
        ("Christmas", fixed(12, 25), "¡Feliz Navidad, Looscid! 🎄 Les deseamos un día lleno de paz y alegría."),
    ],
    "Français": [
        ("New Year's Day", fixed(1, 1), "Bonne année, Looscid ! 🎆 Plein de bonnes choses pour cette nouvelle année."),
        ("Epiphany", fixed(1, 6), "Bonne Épiphanie ! 👑 Qui a trouvé la fève dans la galette ?"),
        ("Candlemas (crêpe day)", fixed(2, 2), "Joyeuse Chandeleur ! 🥞 Vous mettez quoi sur vos crêpes ?"),
        ("International Francophonie Day", fixed(3, 20), "Bonne Journée internationale de la Francophonie ! 🌍 Merci de faire vivre le français ici."),
        ("Easter", easter_offset(0), "Joyeuses Pâques ! 🐣 Bonne chasse aux œufs en chocolat !"),
        ("Fête de la Musique", fixed(6, 21), "Bonne Fête de la Musique ! 🎶 Partagez ce que vous écoutez aujourd'hui."),
        ("Bastille Day", fixed(7, 14), "Bonne fête nationale ! 🎆 Profitez bien du feu d'artifice."),
        ("Christmas", fixed(12, 25), "Joyeux Noël, Looscid ! 🎄 On vous souhaite une journée pleine de douceur."),
    ],
    "Deutsch": [
        ("New Year's Day", fixed(1, 1), "Frohes neues Jahr, Looscid! 🎆 Alles Gute für das neue Jahr."),
        ("Carnival (Rose Monday)", easter_offset(-48), "Helau und Alaaf! 🎭 Viel Spaß beim Karneval und Fasching!"),
        ("Easter", easter_offset(0), "Frohe Ostern! 🐣 Viel Spaß beim Eiersuchen!"),
        ("German Unity Day", fixed(10, 3), "Einen schönen Tag der Deutschen Einheit! 🎉"),
        ("St. Martin's Day", fixed(11, 11), "Schönen Martinstag! 🏮 Laterne, Laterne, Sonne, Mond und Sterne!"),
        ("St. Nicholas Day", fixed(12, 6), "Frohen Nikolaustag! 🎅 Habt ihr etwas in euren Stiefeln gefunden?"),
        ("Christmas Eve", fixed(12, 24), "Frohe Weihnachten, Looscid! 🎄 Schöne Feiertage euch allen."),
    ],
    "Português": [
        ("New Year's Day", fixed(1, 1), "Feliz Ano Novo, Looscid! 🎆 Que o novo ano venha cheio de coisas boas."),
        ("Carnival", easter_offset(-47), "Feliz Carnaval! 🎭 Aproveitem a folia!"),
        ("Easter", easter_offset(0), "Feliz Páscoa! 🐣 Um dia cheio de alegria (e chocolate) para todos."),
        ("Portugal Day", fixed(6, 10), "Feliz Dia de Portugal! 🇵🇹 Um abraço a todos os portugueses por aqui."),
        ("São João (Festa Junina)", fixed(6, 24), "Feliz São João! 🎉🌽 Bom arraial para quem vai à festa!"),
        ("Brazil Independence Day", fixed(9, 7), "Feliz Dia da Independência, Brasil! 🇧🇷"),
        ("Christmas", fixed(12, 25), "Feliz Natal, Looscid! 🎄 Um dia cheio de paz e alegria para todos."),
    ],
    "العربية": [
        ("Ramadan begins", hijri(9, 1), "رمضان كريم! 🌙 كل عام وأنتم بخير."),
        ("Eid al-Fitr", hijri(10, 1), "عيد فطر سعيد! 🎉 عيدكم مبارك، وكل عام وأنتم بخير."),
        ("Eid al-Adha", hijri(12, 10), "عيد أضحى مبارك! ✨ كل عام وأنتم بخير."),
        ("Islamic New Year", hijri(1, 1), "سنة هجرية سعيدة! 🌙 كل عام وأنتم بخير."),
        ("World Arabic Language Day", fixed(12, 18), "اليوم هو اليوم العالمي للغة العربية! 📚 شكراً لكم على الحديث بالعربية هنا."),
    ],
    "日本語": [
        ("New Year (Shōgatsu)", fixed(1, 1), "あけましておめでとうございます！🎍 今年もよろしくお願いします。"),
        ("Hinamatsuri", fixed(3, 3), "楽しいひな祭りを！🎎"),
        ("Children's Day", fixed(5, 5), "こどもの日おめでとう！🎏"),
        ("Tanabata", fixed(7, 7), "七夕だね！🎋 みんなの願いごとがかないますように。"),
        ("Obon", fixed(8, 13), "お盆休み、ゆっくり過ごしてね。🏮"),
        ("Christmas", fixed(12, 25), "メリークリスマス！🎄 素敵なクリスマスを。"),
        ("New Year's Eve (Ōmisoka)", fixed(12, 31), "今年も一年ありがとう！🎆 よいお年を。"),
    ],
    "한국어": [
        ("New Year's Day", fixed(1, 1), "새해 복 많이 받으세요! 🎆"),
        ("Seollal (Lunar New Year)", from_holidays_lib(holidays.SouthKorea, "설날"), "즐거운 설날 보내세요! 🎊 새해 복 많이 받으세요."),
        ("Children's Day", fixed(5, 5), "즐거운 어린이날 보내세요! 🎈"),
        ("Chuseok", from_holidays_lib(holidays.SouthKorea, "추석"), "풍성한 한가위 보내세요! 🌕 즐거운 추석 되세요."),
        ("Hangul Day", fixed(10, 9), "즐거운 한글날! 📚 오늘은 한글을 기념하는 날이에요."),
        ("Christmas", fixed(12, 25), "메리 크리스마스! 🎄 따뜻한 하루 보내세요."),
    ],
    "中文": [
        ("New Year's Day", fixed(1, 1), "元旦快乐！🎆 祝大家新年万事如意。"),
        ("Lunar New Year (Spring Festival)", chinese_lunar(1, 1), "新春快乐！🧧 祝大家新的一年身体健康、万事如意！"),
        ("Lantern Festival", chinese_lunar(1, 15), "元宵节快乐！🏮 记得吃汤圆哦！"),
        ("Dragon Boat Festival", chinese_lunar(5, 5), "端午安康！🐉 今天吃粽子了吗？"),
        ("Mid-Autumn Festival", chinese_lunar(8, 15), "中秋节快乐！🌕 月圆人团圆，祝大家阖家幸福。"),
    ],
    "हिंदी": [
        ("Republic Day (India)", fixed(1, 26), "गणतंत्र दिवस की हार्दिक शुभकामनाएँ! 🇮🇳"),
        ("Holi", from_holidays_lib(holidays.India, "Holi", **INDIA), "होली की हार्दिक शुभकामनाएँ! 🎨 आपका दिन रंगों और खुशियों से भरा हो।"),
        ("Independence Day (India)", fixed(8, 15), "स्वतंत्रता दिवस की हार्दिक शुभकामनाएँ! 🇮🇳"),
        ("Raksha Bandhan", from_holidays_lib(holidays.India, "Raksha Bandhan", **INDIA), "रक्षाबंधन की ढेर सारी शुभकामनाएँ! 🎀"),
        ("Hindi Day", fixed(9, 14), "हिंदी दिवस की शुभकामनाएँ! 📚 यहाँ हिंदी में बात करने के लिए धन्यवाद।"),
        ("Dussehra", from_holidays_lib(holidays.India, "Dussehra", **INDIA), "दशहरा की हार्दिक शुभकामनाएँ! 🏹 अच्छाई की हमेशा जीत हो।"),
        ("Diwali", from_holidays_lib(holidays.India, "Diwali (Deepavali)", **INDIA), "दीपावली की हार्दिक शुभकामनाएँ! 🪔 आपका जीवन रोशनी और खुशियों से भरा रहे।"),
    ],
    "Русский": [
        ("New Year's Day", fixed(1, 1), "С Новым годом, Looscid! 🎆 Пусть этот год будет счастливым!"),
        ("Orthodox Christmas", fixed(1, 7), "С Рождеством! ✨ Тепла и уюта вам и вашим близким."),
        ("Maslenitsa (pancake week) begins", easter_offset(-55, EASTER_ORTHODOX), "Масленица пришла! 🥞 Вкусных блинов всем!"),
        ("International Women's Day", fixed(3, 8), "С 8 Марта! 💐 С праздником весны!"),
        ("Orthodox Easter", easter_offset(0, EASTER_ORTHODOX), "Со Светлой Пасхой! 🐣 Мира и радости всем."),
    ],
    "Türkçe": [
        ("New Year's Day", fixed(1, 1), "Mutlu yıllar, Looscid! 🎆 Yeni yılınız kutlu olsun."),
        ("Ramadan begins", hijri(9, 1), "Hayırlı Ramazanlar! 🌙"),
        ("Children's Day", fixed(4, 23), "23 Nisan Ulusal Egemenlik ve Çocuk Bayramı kutlu olsun! 🎈"),
        ("Ramazan Bayramı (Eid al-Fitr)", hijri(10, 1), "Ramazan Bayramınız mübarek olsun! 🍬"),
        ("Kurban Bayramı (Eid al-Adha)", hijri(12, 10), "Kurban Bayramınız mübarek olsun! ✨"),
        ("Republic Day", fixed(10, 29), "Cumhuriyet Bayramımız kutlu olsun! 🇹🇷"),
    ],
    "Italiano": [
        ("New Year's Day", fixed(1, 1), "Buon anno, Looscid! 🎆 Che sia un anno pieno di cose belle."),
        ("Befana (Epiphany)", fixed(1, 6), "Buona Befana! 🧹 Avete trovato dolci o carbone nella calza?"),
        ("Carnival (Fat Tuesday)", easter_offset(-47), "Buon Carnevale! 🎭 A Carnevale ogni scherzo vale!"),
        ("Easter", easter_offset(0), "Buona Pasqua! 🐣 Tanti auguri a tutti voi!"),
        ("Republic Day", fixed(6, 2), "Buona Festa della Repubblica! 🇮🇹"),
        ("Ferragosto", fixed(8, 15), "Buon Ferragosto! ☀️ Godetevi la giornata!"),
        ("Christmas", fixed(12, 25), "Buon Natale, Looscid! 🎄 Tanti auguri di cuore a tutti."),
    ],
}


def holidays_on(day):
    """Everything to celebrate on this day: {language: [(name, message), ...]}."""
    found = {}
    for language, entries in HOLIDAYS.items():
        for name, rule, message in entries:
            if day in rule(day.year):
                found.setdefault(language, []).append((name, message))
    return found


def upcoming(start, days):
    """Every holiday from start for this many days: list of (date, language, name)."""
    out = []
    years = {start.year, (start + timedelta(days=days)).year}
    end = start + timedelta(days=days)
    for language, entries in HOLIDAYS.items():
        for name, rule, _message in entries:
            for year in years:
                for d in rule(year):
                    if start <= d <= end:
                        out.append((d, language, name))
    return sorted(set(out))
