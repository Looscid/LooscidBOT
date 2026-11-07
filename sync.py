"""LooscidBOT role sync for the faith channels.

Discord permissions add up (OR), so a channel can't say "only people with English AND
Muslim". Instead each faith channel is open to one combined role, like "Muslim · English",
and this job keeps those combined roles in step for every member:

    has the language role AND the faith role  ->  gets the combined role
    otherwise                                 ->  loses the combined role

It only ever adds or removes the combined roles listed in faiths.json. It never touches
any other role. It only works in the Looscid server. Logs show counts only, no names.

Settings (environment variables):
- DISCORD_TOKEN: the bot token (GitHub Actions secret).
- DRY_RUN: "true" shows what would change and changes nothing.
"""

import json
import os
import sys
import time

import requests

LOOSCID_GUILD_ID = "1500332794327466076"
API = "https://discord.com/api/v10"
MAX_CHANGES_PER_RUN = 400  # a safety stop: something is off if a run wants more than this

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "faiths.json"), encoding="utf-8") as f:
    FAITHS = json.load(f)


def call(session, method, path, **kwargs):
    for attempt in range(6):
        r = session.request(method, API + path, timeout=30, **kwargs)
        if r.status_code == 429:
            time.sleep(float(r.json().get("retry_after", 2)) + 0.5)
            continue
        if r.status_code >= 500:
            time.sleep(2 + attempt * 2)
            continue
        return r
    return r


def wanted_roles(member_roles, plan):
    """The combined role ids this member should have."""
    return {combo for combo, (lang_id, faith_id) in plan.items() if lang_id in member_roles and faith_id in member_roles}


def main():
    dry_run = os.environ.get("DRY_RUN", "true").strip().lower() != "false"
    token = os.environ.get("DISCORD_TOKEN", "").strip()
    print(f"LooscidBOT role sync. Mode: {'DRY RUN, nothing will change' if dry_run else 'LIVE'}.")
    if not token:
        print("No DISCORD_TOKEN set. Stopping.")
        return 1
    s = requests.Session()
    s.headers.update({"Authorization": "Bot " + token, "User-Agent": "LooscidBOT-sync (https://github.com, 1.0)",
                      "X-Audit-Log-Reason": "LooscidBOT faith channel role sync"})

    guilds = call(s, "GET", "/users/@me/guilds").json()
    if not any(g["id"] == LOOSCID_GUILD_ID for g in guilds):
        print("LooscidBOT is not in the Looscid server. Stopping.")
        return 1

    roles = call(s, "GET", f"/guilds/{LOOSCID_GUILD_ID}/roles").json()
    by_name = {}
    for r in roles:
        by_name.setdefault(r["name"], []).append(r["id"])

    def one(name):
        ids = by_name.get(name, [])
        return ids[0] if len(ids) == 1 else None

    # plan: combined role id -> (language role id, faith role id)
    plan, skipped = {}, 0
    for faith in FAITHS["faiths"]:
        faith_id = one(faith)
        for language, info in FAITHS["languages"].items():
            lang_id = one(info["role"])
            combo_id = one(FAITHS["combined_role"].format(faith=faith, language=language))
            if faith_id and lang_id and combo_id:
                plan[combo_id] = (lang_id, faith_id)
            else:
                skipped += 1
    print(f"Combined roles managed: {len(plan)}. Skipped (a role is missing or has a duplicate name): {skipped}.")
    if not plan:
        return 1

    members, after = [], "0"
    while True:
        r = call(s, "GET", f"/guilds/{LOOSCID_GUILD_ID}/members", params={"limit": 1000, "after": after})
        if r.status_code != 200:
            print(f"Could not list members: {r.status_code}. Stopping, nothing changed.")
            return 1
        page = r.json()
        members += page
        if len(page) < 1000:
            break
        after = page[-1]["user"]["id"]
    humans = [m for m in members if not m["user"].get("bot")]

    changes = []
    for m in humans:
        have = set(m.get("roles", []))
        want = wanted_roles(have, plan)
        current = have & set(plan)
        changes += [("add", m["user"]["id"], rid) for rid in sorted(want - current)]
        changes += [("remove", m["user"]["id"], rid) for rid in sorted(current - want)]

    adds = sum(1 for c in changes if c[0] == "add")
    removes = len(changes) - adds
    people = len({c[1] for c in changes})
    with_any = sum(1 for m in humans if wanted_roles(set(m.get("roles", [])), plan))
    print(f"Members checked: {len(humans)}. Members who should be in at least one faith channel: {with_any}.")
    print(f"Changes needed: {adds} to add, {removes} to remove, for {people} members.")

    if len(changes) > MAX_CHANGES_PER_RUN:
        print(f"That is more than {MAX_CHANGES_PER_RUN} changes in one run, so this run changes nothing. Check the role names.")
        return 1
    if dry_run:
        print("Dry run: nothing changed.")
        return 0

    ok = failed = 0
    for action, user_id, role_id in changes:
        method = "PUT" if action == "add" else "DELETE"
        r = call(s, method, f"/guilds/{LOOSCID_GUILD_ID}/members/{user_id}/roles/{role_id}")
        if r.status_code in (200, 204):
            ok += 1
        else:
            failed += 1
        time.sleep(0.3)
    print(f"Done: {ok} changes made, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
