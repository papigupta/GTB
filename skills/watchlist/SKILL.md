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
- CATEGORY: **watch_together** unless the title is clearly one of these: psychological horror, extreme violence, torture, deeply depressing/nihilistic, body horror, or disturbing content that would ruin a date night. Only films like Se7en, Requiem for a Dream, Hereditary, The Road, Irreversible, A Serbian Film, Martyrs, Come and See qualify as **watch_alone**. Romcoms, comedies, dramas, thrillers, action, sci-fi, adventure, documentaries, animation, teen movies = **watch_together**. When in doubt = **watch_together**.
- NOTE: one-line spoiler-free description


## Showing the list
When the user says "watchlist", "what should I watch", "reccos", "kuch dekhna hai", etc:

python3 ~/.openclaw/workspace/skills/watchlist/scripts/watchlist.py show

Send the output to the user.

## Removing a title
When the user says "watched X", "remove X", "done with X":

python3 ~/.openclaw/workspace/skills/watchlist/scripts/watchlist.py remove "<TITLE>"
