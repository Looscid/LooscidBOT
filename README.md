# LooscidBOT holidays

Made by [2three1y](https://2three1y.github.io/).

LooscidBOT celebrates holidays in the [Looscid](https://github.com/Looscid) Discord server. Once a day it checks the calendar, and when one of a language's holidays is today, it posts one short, happy message in that language's general chat and in the text chat of that language's voice channel.

Each language only gets its own holidays. Ramadan and Eid are posted in the Arabic channels, Diwali in the Hindi channels, Día de Muertos in the Spanish channels, and so on.

## The bot is private to Looscid

The code is public so anyone can read it and learn from it. The bot itself only works in Looscid:

- "Public Bot" is turned off in the Discord developer settings, so nobody else can add LooscidBOT to a server.
- The Looscid server id is written into the code. The bot never posts anywhere else.
- If the bot ever finds itself in another server, it leaves that server on its next run.
- The bot's token is stored as a GitHub Actions secret. It is not in this repository.

If you want a bot like this for your own server, you are welcome to copy the code and make your own bot with your own token.

## How it works

1. A GitHub Actions workflow runs every day at 12:00 UTC. At that moment it is the same date almost everywhere in the world, from Hawaii to New Zealand.
2. The bot reads the server's channel list and finds each language's category, general channel and voice channel by the names listed in channels.json. No channel ids are stored, so channels can be moved or recreated. If a channel is renamed on Discord, rename it in channels.json too.
3. It works out today's holidays for each language and posts the message.
4. Before posting, it checks it has not already posted the same message today, so a repeated run does not post twice.

## Files

- bot.py: finds the channels and posts the messages.
- channels.json: the names of every language's channels, like rules, announcements, general and voice, in that language.
- holidays_rules.py: every language's holidays, how each date is worked out, and the messages.
- faiths.json: the faith channels: which faiths, every language's channel names, the faith holiday names and messages.
- faith_holidays.py: how each faith holiday date is worked out.
- sync.py: keeps the "faith · language" roles in step (see Faith channels).
- requirements.txt: the Python libraries used.
- .github/workflows/holidays.yml: the daily schedule.
- .github/workflows/sync.yml: the role sync, every 15 minutes.

## How dates are worked out

No dates are typed in by hand for a particular year. Each holiday is a rule, so future years work on their own:

- Fixed days, like Christmas on 25 December.
- Simple rules, like Thanksgiving on the fourth Thursday of November.
- Easter and the days around it (Carnival, Pancake Day), Western and Orthodox, from the dateutil library.
- Islamic dates (Ramadan, both Eids, Islamic New Year) from the hijridate library, which uses the Umm al-Qura calendar.
- Chinese lunar dates (Lunar New Year, Lantern Festival, Dragon Boat Festival, Mid-Autumn Festival) from the lunardate library.
- Korean Seollal and Chuseok from the holidays library's South Korea calendar.
- Holi, Raksha Bandhan, Dussehra and Diwali from the holidays library's India calendar.

### Things to know about dates

- Islamic holidays begin when the new moon is seen, so in some countries they start a day earlier or later than the calendar says. Turkey, for example, follows its own official calendar. The bot uses one calendar for everyone, so a post can be a day off for some members.
- The holidays library currently has Hindu festival dates up to 2035. Updating the library version in requirements.txt adds later years.
- hijridate covers dates up to 2077, and lunardate up to 2099.

## The holidays

### English

- New Year's Day: “Happy New Year, Looscid! 🎆 Wishing everyone an amazing year ahead.”
- Pancake Day / Mardi Gras: “Happy Pancake Day and Mardi Gras! 🥞 What's your favourite topping?”
- Easter: “Happy Easter, everyone! 🐣 Hope your day is full of sunshine and chocolate.”
- Independence Day (US): “Happy Fourth of July! 🎆 Have a fun and safe day, everyone.”
- Halloween: “Happy Halloween! 🎃 Tell us about your costume!”
- Bonfire Night (UK): “Happy Bonfire Night! 🎇 Enjoy the fireworks, everyone.”
- Thanksgiving (US): “Happy Thanksgiving! 🦃 Thankful for every single one of you here.”
- Christmas: “Merry Christmas, Looscid! 🎄 Wishing you a cosy, happy day.”

### Español

- New Year's Day: “¡Feliz Año Nuevo, Looscid! 🎆 Que este año venga lleno de cosas buenas.”
- Three Kings' Day: “¡Feliz Día de Reyes! 👑 ¿A quién le tocó la sorpresa de la rosca?”
- Easter: “¡Feliz Pascua! 🐣 Que tengan un día lleno de alegría.”
- Spanish Language Day: “¡Feliz Día del Idioma Español! 📚 Gracias por hablar español aquí con nosotros.”
- Day of the Dead: “¡Feliz Día de Muertos! 🌼🕯️ Hoy recordamos con cariño a nuestros seres queridos.”
- Christmas: “¡Feliz Navidad, Looscid! 🎄 Les deseamos un día lleno de paz y alegría.”

### Français

- New Year's Day: “Bonne année, Looscid ! 🎆 Plein de bonnes choses pour cette nouvelle année.”
- Epiphany: “Bonne Épiphanie ! 👑 Qui a trouvé la fève dans la galette ?”
- Candlemas (crêpe day): “Joyeuse Chandeleur ! 🥞 Vous mettez quoi sur vos crêpes ?”
- International Francophonie Day: “Bonne Journée internationale de la Francophonie ! 🌍 Merci de faire vivre le français ici.”
- Easter: “Joyeuses Pâques ! 🐣 Bonne chasse aux œufs en chocolat !”
- Fête de la Musique: “Bonne Fête de la Musique ! 🎶 Partagez ce que vous écoutez aujourd'hui.”
- Bastille Day: “Bonne fête nationale ! 🎆 Profitez bien du feu d'artifice.”
- Christmas: “Joyeux Noël, Looscid ! 🎄 On vous souhaite une journée pleine de douceur.”

### Deutsch

- New Year's Day: “Frohes neues Jahr, Looscid! 🎆 Alles Gute für das neue Jahr.”
- Carnival (Rose Monday): “Helau und Alaaf! 🎭 Viel Spaß beim Karneval und Fasching!”
- Easter: “Frohe Ostern! 🐣 Viel Spaß beim Eiersuchen!”
- German Unity Day: “Einen schönen Tag der Deutschen Einheit! 🎉”
- St. Martin's Day: “Schönen Martinstag! 🏮 Laterne, Laterne, Sonne, Mond und Sterne!”
- St. Nicholas Day: “Frohen Nikolaustag! 🎅 Habt ihr etwas in euren Stiefeln gefunden?”
- Christmas Eve: “Frohe Weihnachten, Looscid! 🎄 Schöne Feiertage euch allen.”

### Português

- New Year's Day: “Feliz Ano Novo, Looscid! 🎆 Que o novo ano venha cheio de coisas boas.”
- Carnival: “Feliz Carnaval! 🎭 Aproveitem a folia!”
- Easter: “Feliz Páscoa! 🐣 Um dia cheio de alegria (e chocolate) para todos.”
- Portugal Day: “Feliz Dia de Portugal! 🇵🇹 Um abraço a todos os portugueses por aqui.”
- São João (Festa Junina): “Feliz São João! 🎉🌽 Bom arraial para quem vai à festa!”
- Brazil Independence Day: “Feliz Dia da Independência, Brasil! 🇧🇷”
- Christmas: “Feliz Natal, Looscid! 🎄 Um dia cheio de paz e alegria para todos.”

### العربية

- Ramadan begins: “رمضان كريم! 🌙 كل عام وأنتم بخير.”
- Eid al-Fitr: “عيد فطر سعيد! 🎉 عيدكم مبارك، وكل عام وأنتم بخير.”
- Eid al-Adha: “عيد أضحى مبارك! ✨ كل عام وأنتم بخير.”
- Islamic New Year: “سنة هجرية سعيدة! 🌙 كل عام وأنتم بخير.”
- World Arabic Language Day: “اليوم هو اليوم العالمي للغة العربية! 📚 شكراً لكم على الحديث بالعربية هنا.”

### 日本語

- New Year (Shōgatsu): “あけましておめでとうございます！🎍 今年もよろしくお願いします。”
- Hinamatsuri: “楽しいひな祭りを！🎎”
- Children's Day: “こどもの日おめでとう！🎏”
- Tanabata: “七夕だね！🎋 みんなの願いごとがかないますように。”
- Obon: “お盆休み、ゆっくり過ごしてね。🏮”
- Christmas: “メリークリスマス！🎄 素敵なクリスマスを。”
- New Year's Eve (Ōmisoka): “今年も一年ありがとう！🎆 よいお年を。”

### 한국어

- New Year's Day: “새해 복 많이 받으세요! 🎆”
- Seollal (Lunar New Year): “즐거운 설날 보내세요! 🎊 새해 복 많이 받으세요.”
- Children's Day: “즐거운 어린이날 보내세요! 🎈”
- Chuseok: “풍성한 한가위 보내세요! 🌕 즐거운 추석 되세요.”
- Hangul Day: “즐거운 한글날! 📚 오늘은 한글을 기념하는 날이에요.”
- Christmas: “메리 크리스마스! 🎄 따뜻한 하루 보내세요.”

### 中文

- New Year's Day: “元旦快乐！🎆 祝大家新年万事如意。”
- Lunar New Year (Spring Festival): “新春快乐！🧧 祝大家新的一年身体健康、万事如意！”
- Lantern Festival: “元宵节快乐！🏮 记得吃汤圆哦！”
- Dragon Boat Festival: “端午安康！🐉 今天吃粽子了吗？”
- Mid-Autumn Festival: “中秋节快乐！🌕 月圆人团圆，祝大家阖家幸福。”

### हिंदी

- Republic Day (India): “गणतंत्र दिवस की हार्दिक शुभकामनाएँ! 🇮🇳”
- Holi: “होली की हार्दिक शुभकामनाएँ! 🎨 आपका दिन रंगों और खुशियों से भरा हो।”
- Independence Day (India): “स्वतंत्रता दिवस की हार्दिक शुभकामनाएँ! 🇮🇳”
- Raksha Bandhan: “रक्षाबंधन की ढेर सारी शुभकामनाएँ! 🎀”
- Hindi Day: “हिंदी दिवस की शुभकामनाएँ! 📚 यहाँ हिंदी में बात करने के लिए धन्यवाद।”
- Dussehra: “दशहरा की हार्दिक शुभकामनाएँ! 🏹 अच्छाई की हमेशा जीत हो।”
- Diwali: “दीपावली की हार्दिक शुभकामनाएँ! 🪔 आपका जीवन रोशनी और खुशियों से भरा रहे।”

### Русский

- New Year's Day: “С Новым годом, Looscid! 🎆 Пусть этот год будет счастливым!”
- Orthodox Christmas: “С Рождеством! ✨ Тепла и уюта вам и вашим близким.”
- Maslenitsa (pancake week) begins: “Масленица пришла! 🥞 Вкусных блинов всем!”
- International Women's Day: “С 8 Марта! 💐 С праздником весны!”
- Orthodox Easter: “Со Светлой Пасхой! 🐣 Мира и радости всем.”

### Türkçe

- New Year's Day: “Mutlu yıllar, Looscid! 🎆 Yeni yılınız kutlu olsun.”
- Ramadan begins: “Hayırlı Ramazanlar! 🌙”
- Children's Day: “23 Nisan Ulusal Egemenlik ve Çocuk Bayramı kutlu olsun! 🎈”
- Ramazan Bayramı (Eid al-Fitr): “Ramazan Bayramınız mübarek olsun! 🍬”
- Kurban Bayramı (Eid al-Adha): “Kurban Bayramınız mübarek olsun! ✨”
- Republic Day: “Cumhuriyet Bayramımız kutlu olsun! 🇹🇷”

### Italiano

- New Year's Day: “Buon anno, Looscid! 🎆 Che sia un anno pieno di cose belle.”
- Befana (Epiphany): “Buona Befana! 🧹 Avete trovato dolci o carbone nella calza?”
- Carnival (Fat Tuesday): “Buon Carnevale! 🎭 A Carnevale ogni scherzo vale!”
- Easter: “Buona Pasqua! 🐣 Tanti auguri a tutti voi!”
- Republic Day: “Buona Festa della Repubblica! 🇮🇹”
- Ferragosto: “Buon Ferragosto! ☀️ Godetevi la giornata!”
- Christmas: “Buon Natale, Looscid! 🎄 Tanti auguri di cuore a tutti.”

## Faith channels

Every language also has one channel per faith, for example #muslim-community in English and #comunidad-musulmana in Español. Only people who picked BOTH that language and that faith can see it, plus that language's mods. Faith holidays are posted there, in that language, with no pings. Nobody gets a holiday they didn't pick.

### How people join or leave

- When joining the server there is an optional question: "Do you celebrate any of these?" Pick as many as you like, or none.
- To change it later: tap the server name, then Channels & Roles, and change your answers. Your channels show up or disappear within about 15 minutes.
- Nobody else can see what you picked.

### Why there is a sync job

Discord permissions add up: a channel can be opened to the English role OR the Muslim role, but not to "English AND Muslim". So each faith channel is opened to one combined role, like "Muslim · English", and sync.py gives that role to everyone who has both the language role and the faith role, and takes it away from anyone who no longer has both.

- It runs on GitHub Actions every 15 minutes, and can be started by hand (dry run by default).
- It only ever adds or removes the combined roles listed in faiths.json. It never touches any other role.
- It only works in the Looscid server.
- Its logs show counts only, never member names.
- If one run would make more than 400 changes, it stops and changes nothing, because that means something is wrong.

### Which faiths, and why

The list comes from Pew Research Center's global religious composition report (June 2025, data for 2020): Christians 28.8% of the world, Muslims 25.6%, Hindus 14.9%, Buddhists 4.1%, Jews about 0.2% (14.8 million). Pew groups Sikhs with "other religions"; Pew's earlier report quotes about 25 million Sikhs worldwide. The rule used: at least about 10 million people and its own holiday calendar. Smaller faiths (Daoist, Baha'i, Shinto, Jain) can be added later the same way. 24.2% of the world has no religion; there is no channel for that because there are no holidays to post, and everyone already sees the normal channels.

- Source: https://www.pewresearch.org/religion/2025/06/09/how-the-global-religious-landscape-changed-from-2010-to-2020/
- Sikh number: https://www.pewresearch.org/religion/2012/12/18/global-religious-landscape-other/

### Faith holidays

Each one goes to that faith's channel in all 13 languages. The language general chats keep their own holidays as listed above.

- Christian: Christmas, Orthodox Christmas, Easter, Orthodox Easter (only when it is on a different day).
- Muslim: start of Ramadan, Eid al-Fitr, Eid al-Adha, Islamic New Year. Moon sighting can move these by a day.
- Hindu: Maha Shivaratri, Holi, Raksha Bandhan, Janmashtami, Ganesh Chaturthi, Dussehra, Diwali.
- Buddhist: Magha Puja, Vesak, Asalha Puja (Dharma Day). Some countries mark Vesak on a different day.
- Jewish: Purim, first day of Passover, Shavuot, Rosh Hashanah, Sukkot, first day of Hanukkah. Jewish holidays begin at sundown the evening before.
- Sikh: Guru Gobind Singh Gurpurab, Vaisakhi, Bandi Chhor Divas, Guru Nanak Gurpurab.

Dates come from libraries: hijridate for Islamic dates, dateutil for Easter, and the holidays library's India, Israel, Singapore and Thailand calendars for the rest.

## Running it yourself

Every change to the code also runs a dry run automatically, so you can check the results in the Actions tab before the next real post.

Run the workflow by hand from the Actions tab: choose "Holiday posts", then "Run workflow". "Dry run" is on by default: the bot then only prints which channels it found, what it would post today, and every holiday in the next 60 days. It posts nothing and leaves no servers. You can also type a date to see what the bot would post on that day.

To run it on your own computer:

1. Install Python 3.
2. Run: pip install -r requirements.txt
3. Run: python bot.py

Without a token it only prints the calendar. With DISCORD_TOKEN set it also checks the channels. DRY_RUN is on unless you set it to false.

## Adding a holiday

Open holidays_rules.py, find the language, and add a line with the holiday's English name, its date rule, and the message in that language. Keep messages short, friendly, and with one emoji.

## Keeping the schedule on

GitHub turns off scheduled workflows in a repository that has had no activity for 60 days. On the first day of each month, the workflow asks GitHub to keep itself turned on. If it ever does get turned off, open the Actions tab, choose "Holiday posts", and choose "Enable workflow".

## License

MIT. See the LICENSE file.
