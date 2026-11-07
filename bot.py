"""LooscidBOT holidays: posts a short celebration in each language's own channels
on that language's holidays. Runs once a day from GitHub Actions.

Settings come from environment variables:
- DISCORD_TOKEN: the bot token (a GitHub Actions secret, never in the code).
- DRY_RUN: "true" prints what would be posted and posts nothing. Leaves no servers either.
- PRETEND_DATE: YYYY-MM-DD, only honoured in a dry run, to test a given day.
"""

import json
import os
import sys
import time
import unicodedata
from datetime import date, datetime, timezone

import requests

from holidays_rules import HOLIDAYS, holidays_on, upcoming

# LooscidBOT is private to the Looscid server. The code is public, the bot is not.
LOOSCID_GUILD_ID = "1500332794327466076"

API = "https://discord.com/api/v10"

# Also post in the text chat of the language's voice channel.
ALSO_POST_IN_VOICE = True

# Every language's channel names live in channels.json (no channel ids are stored).
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "channels.json"), encoding="utf-8") as f:
    CHANNEL_LABELS = json.load(f)["languages"]

TEXT, VOICE, CATEGORY, ANNOUNCEMENT = 0, 2, 4, 5
VIEW_CHANNEL, SEND_MESSAGES, READ_HISTORY, ADMINISTRATOR = 1 << 10, 1 << 11, 1 << 16, 1 << 3


def norm(text):
    """Lowercase, no emoji or symbols, so "🇪🇸 Español" still matches "Español"."""
    text = unicodedata.normalize("NFC", text).casefold()
    return "".join(ch for ch in text if unicodedata.category(ch)[0] in "LMN").strip()


class Discord:
    def __init__(self, token):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": "Bot " + token,
            "User-Agent": "LooscidBOT-holidays (https://github.com, 1.0)",
        })

    def call(self, method, path, **kwargs):
        for attempt in range(6):
            r = self.session.request(method, API + path, timeout=30, **kwargs)
            if r.status_code == 429:
                time.sleep(float(r.json().get("retry_after", 2)) + 0.5)
                continue
            if r.status_code >= 500:
                time.sleep(2 + attempt * 2)
                continue
            return r
        return r


def effective_permissions(channel, roles, my_role_ids, my_id, guild):
    """Discord's permission math for one channel, so a dry run can say if posting would work."""
    if guild.get("owner_id") == my_id:
        return -1
    everyone = roles[LOOSCID_GUILD_ID]
    perms = int(everyone["permissions"])
    for rid in my_role_ids:
        perms |= int(roles[rid]["permissions"])
    if perms & ADMINISTRATOR:
        return -1
    overwrites = {o["id"]: o for o in channel.get("permission_overwrites", [])}
    if LOOSCID_GUILD_ID in overwrites:
        o = overwrites[LOOSCID_GUILD_ID]
        perms = (perms & ~int(o["deny"])) | int(o["allow"])
    allow = deny = 0
    for rid in my_role_ids:
        if rid in overwrites:
            allow |= int(overwrites[rid]["allow"])
            deny |= int(overwrites[rid]["deny"])
    perms = (perms & ~deny) | allow
    if my_id in overwrites:
        o = overwrites[my_id]
        perms = (perms & ~int(o["deny"])) | int(o["allow"])
    return perms


def can_post(perms):
    return perms == -1 or (perms & VIEW_CHANNEL and perms & SEND_MESSAGES)


def find_channels(channels):
    """For each language: its general text channel and its voice channel, found by name."""
    categories = [c for c in channels if c["type"] == CATEGORY]
    found = {}
    for language, labels in CHANNEL_LABELS.items():
        wanted = {
            "general": (TEXT, norm(labels["channels"]["general"])),
            "voice": (VOICE, norm(labels["channels"]["voice"])),
        }
        result = {"general": None, "voice": None}
        for cat_name in labels["categories"]:
            for cat in (c for c in categories if norm(c["name"]) == norm(cat_name)):
                inside = sorted((c for c in channels if c.get("parent_id") == cat["id"]), key=lambda c: c["position"])
                for kind, (ctype, name) in wanted.items():
                    if result[kind] is None:
                        match = [c for c in inside if c["type"] == ctype and norm(c["name"]) == name]
                        if match:
                            result[kind] = match[0]
        found[language] = result
    return found


def already_posted_today(api, channel_id, my_id, text, today):
    r = api.call("GET", f"/channels/{channel_id}/messages", params={"limit": 25})
    if r.status_code != 200:
        return False
    for m in r.json():
        if m["author"]["id"] == my_id and m["content"] == text and m["timestamp"][:10] == today.isoformat():
            return True
    return False


def main():
    dry_run = os.environ.get("DRY_RUN", "true").strip().lower() != "false"
    token = os.environ.get("DISCORD_TOKEN", "").strip()
    today = datetime.now(timezone.utc).date()
    pretend = os.environ.get("PRETEND_DATE", "").strip()
    if pretend and dry_run:
        today = date.fromisoformat(pretend)
    print(f"LooscidBOT holidays. Date (UTC): {today}. Mode: {'DRY RUN, nothing will be posted' if dry_run else 'LIVE'}.")

    if not token:
        print("No DISCORD_TOKEN set, so only the holiday calendar is shown.")
        api = None
    else:
        api = Discord(token)

    # 1. Private to Looscid: leave any other server.
    if api:
        me = api.call("GET", "/users/@me").json()
        my_id = me["id"]
        print(f"Signed in as {me['username']} ({my_id}).")
        guilds = api.call("GET", "/users/@me/guilds").json()
        for g in guilds:
            if g["id"] != LOOSCID_GUILD_ID:
                if dry_run:
                    print(f"Would leave server '{g['name']}' ({g['id']}): LooscidBOT is only for Looscid.")
                else:
                    r = api.call("DELETE", f"/users/@me/guilds/{g['id']}")
                    print(f"Left server '{g['name']}' ({g['id']}): {r.status_code}.")
        if not any(g["id"] == LOOSCID_GUILD_ID for g in guilds):
            print("LooscidBOT is not in the Looscid server. Stopping.")
            return 1

        guild = api.call("GET", f"/guilds/{LOOSCID_GUILD_ID}").json()
        channels = api.call("GET", f"/guilds/{LOOSCID_GUILD_ID}/channels").json()
        roles = {r["id"]: r for r in api.call("GET", f"/guilds/{LOOSCID_GUILD_ID}/roles").json()}
        member = api.call("GET", f"/guilds/{LOOSCID_GUILD_ID}/members/{my_id}").json()
        my_roles = member.get("roles", [])

        # 2. Find each language's channels by name (no hard-coded channel ids).
        found = find_channels(channels)
        print("\nChannels found:")
        problems = 0
        for language, ch in found.items():
            parts = []
            for kind in ("general", "voice"):
                c = ch[kind]
                if c is None:
                    parts.append(f"{kind}: NOT FOUND")
                    if kind == "general":
                        problems += 1
                    continue
                ok = can_post(effective_permissions(c, roles, my_roles, my_id, guild))
                if not ok and kind == "general":
                    problems += 1
                parts.append(f"{kind}: #{c['name']} ({c['id']}){'' if ok else ' - bot CANNOT post here'}")
            print(f"- {language}: " + "; ".join(parts))
        print(f"General channels found: {sum(1 for c in found.values() if c['general'])} of {len(found)}. Problems: {problems}.")
    else:
        found = {}

    # 3. Today's holidays, posted only in their own language.
    todays = holidays_on(today)
    print(f"\nToday ({today}):" + ("" if todays else " no holidays."))
    for language, items in todays.items():
        text = "\n".join(message for _name, message in items)
        names = ", ".join(name for name, _m in items)
        targets = []
        ch = found.get(language, {})
        if ch.get("general"):
            targets.append(ch["general"])
        if ALSO_POST_IN_VOICE and ch.get("voice"):
            targets.append(ch["voice"])
        print(f"- {language}: {names}\n  Message: {text}")
        if not api:
            continue
        if not targets:
            print("  No channel found for this language, skipped.")
        for c in targets:
            if c.get("guild_id", LOOSCID_GUILD_ID) != LOOSCID_GUILD_ID:
                print(f"  Refusing #{c['name']}: not in Looscid.")
                continue
            if dry_run:
                print(f"  Would post in #{c['name']}.")
                continue
            if already_posted_today(api, c["id"], my_id, text, today):
                print(f"  Already posted in #{c['name']} today, skipped.")
                continue
            r = api.call("POST", f"/channels/{c['id']}/messages", json={"content": text, "allowed_mentions": {"parse": []}})
            print(f"  Posted in #{c['name']}: {r.status_code}{'' if r.ok else ' ' + r.text[:200]}")

    # 4. What's coming up.
    print("\nNext 60 days:")
    for d, language, name in upcoming(today, 60):
        print(f"- {d.isoformat()} {d.strftime('%A')}: {language}, {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
