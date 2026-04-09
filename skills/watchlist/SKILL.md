---
name: watchlist
description: Manage a movie/show/documentary watchlist. When the user sends a title, recognize it and add it to the watchlist with the right category. When asked, show the list.
tags: [entertainment, movies, watchlist]
tools: [exec]
---

# Watchlist Skill

## Adding a title
When the user sends a plain text message that is a movie, TV show, documentary, or anime title, run:

python3 ~/.openclaw/workspace/skills/watchlist/scripts/watchlist.py add "<TITLE>" "<TYPE>" "<CATEGORY>" "<NOTE>"

- TYPE: film, series, documentary, or anime
- CATEGORY: Default to watch_together. ONLY use watch_alone for genuinely dark, disturbing, heavy horror, extreme violence, or deeply sad films (e.g. Requiem for a Dream, Hereditary, Se7en, The Road, Martyrs). If in doubt, it's watch_together.
- NOTE: one-line spoiler-free description

Example:
python3 ~/.openclaw/workspace/skills/watchlist/scripts/watchlist.py add "Oppenheimer" "film" "watch_alone" "Epic biographical thriller about the atomic bomb"

Do NOT ask, discuss, or recommend. Just add and confirm.

## Showing the list
When the user says "watchlist", "what should I watch", "reccos", "kuch dekhna hai", etc:

python3 ~/.openclaw/workspace/skills/watchlist/scripts/watchlist.py show

Send the output to the user.

## Removing a title
When the user says "watched X", "remove X", "done with X":

python3 ~/.openclaw/workspace/skills/watchlist/scripts/watchlist.py remove "<TITLE>"
