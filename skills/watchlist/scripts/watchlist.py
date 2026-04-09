#!/usr/bin/env python3
import json, sys, os
from datetime import date

WATCHLIST = os.path.expanduser("~/.openclaw/workspace/watchlist.json")

def load():
    if os.path.exists(WATCHLIST):
        with open(WATCHLIST) as f:
            return json.load(f)
    return []

def save(data):
    with open(WATCHLIST, "w") as f:
        json.dump(data, f, indent=2)

def add(title, typ, category, note):
    DARK_KEYWORDS = ["horror", "disturbing", "torture", "nihilistic", "brutal", "gore", "slasher", "exploitation"]
    DARK_TITLES = ["se7en", "seven", "requiem for a dream", "hereditary", "the road", "martyrs", 
                   "irreversible", "a serbian film", "come and see", "salo", "antichrist", 
                   "funny games", "the house that jack built", "midsommar", "raw", "audition",
                   "old boy", "oldboy", "i saw the devil", "the girl next door 2007"]
    
    if title.lower() in DARK_TITLES or any(k in note.lower() for k in DARK_KEYWORDS):
        category = "watch_alone"
    else:
        category = "watch_together"
    
    wl = load()
    for item in wl:
        if item["title"].lower() == title.lower():
            print(f"ALREADY_EXISTS: {title}")
            return
    wl.append({
        "title": title,
        "type": typ,
        "category": category,
        "added": str(date.today()),
        "note": note
    })
    save(wl)
    cat_label = "Watch Alone 🔥" if category == "watch_alone" else "Watch Together 💕"
    print(f"ADDED: {title} → {cat_label}")

def remove(title):
    wl = load()
    new = [x for x in wl if x["title"].lower() != title.lower()]
    if len(new) == len(wl):
        print(f"NOT_FOUND: {title}")
        return
    save(new)
    print(f"REMOVED: {title}")

def show():
    wl = load()
    if not wl:
        print("EMPTY: No items on your watchlist yet.")
        return
    alone = [x for x in wl if x["category"] == "watch_alone"]
    together = [x for x in wl if x["category"] == "watch_together"]
    print("🎬 YOUR WATCHLIST\n")
    if alone:
        print(f"🔥 WATCH ALONE ({len(alone)})")
        for x in alone:
            print(f"• {x['title']} — {x['note']}")
        print()
    if together:
        print(f"💕 WATCH TOGETHER ({len(together)})")
        for x in together:
            print(f"• {x['title']} — {x['note']}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "add":
        add(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "remove":
        remove(sys.argv[2])
    elif cmd == "show":
        show()
