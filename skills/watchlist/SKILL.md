---
name: watchlist
description: Manage a movie/show/documentary watchlist. When the user sends a title, recognize it and add it to the watchlist with the right category. When asked, show the list.
tags: [entertainment, movies, watchlist]
tools: [fs]
---

# Watchlist Skill

## What this does
Maintains a watchlist at `watchlist.json` in the workspace root.

## When a user sends a movie / show / documentary title
1. Recognize it as a title (even if they just send "Oppenheimer" or "planet earth" with no other context — treat bare titles as watchlist additions).
2. Use your knowledge to categorize it:
   - **"Watch Alone"** → dark, twisted, disturbing, sad endings, heavy horror, extreme violence, psychologically intense, not fun for a casual couples' night. Examples: Requiem for a Dream, Hereditary, Se7en, The Road, Martyrs, Come and See.
   - **"Watch Together"** → everything else. Comedies, romances, adventure, light thrillers, documentaries (unless truly disturbing), feel-good, sci-fi, action, animated, etc.
3. Add an entry to `watchlist.json` with this structure:
```json
   {
     "title": "Oppenheimer",
     "type": "film",
     "category": "watch_alone",
     "added": "2026-04-09",
     "note": "Epic biographical thriller about the atomic bomb"
   }
```
   - `type` can be: `film`, `series`, `documentary`, `anime`
   - `category` is either `watch_alone` or `watch_together`
   - `note` is a one-line description (keep it short, no spoilers)
4. Confirm back with something like: "Added Oppenheimer to Watch Alone 🎬"
5. If the title is ambiguous (multiple movies with that name), ask which one.
6. If it's already on the list, say so.

## When the user asks to see their watchlist
Triggers: "watchlist", "what should I watch", "show me my list", "what's on my list", "movie suggestions", "send the list", "give me reccos", "kuch dekhna hai"

Read `watchlist.json` and send it formatted like:

🎬 YOUR WATCHLIST

🔥 WATCH ALONE (6)
- Oppenheimer — Epic biographical thriller
- Se7en — Two detectives hunt a serial killer

💕 WATCH TOGETHER (4)
- The Grand Budapest Hotel — Quirky Wes Anderson comedy
- Planet Earth III — Stunning nature documentary

## When the user says they watched something
Triggers: "watched Oppenheimer", "done with X", "remove X", "finished X"

Remove it from `watchlist.json` and confirm.

## File management
- The file lives at: `watchlist.json` (workspace root)
- If the file doesn't exist yet, create it as an empty array `[]`
- Always read the current file before writing (don't overwrite blindly)
- Keep the JSON valid

## Edge cases
- If the user sends something that could be a title OR a normal message, lean toward treating it as a title if it matches a known movie/show/documentary. If truly unclear, ask: "Want me to add that to your watchlist?"
- If they send a title with a note like "Oppenheimer - heard it's amazing", store the note.
- If they say "recommend something from my list" — pick one randomly from the appropriate category and suggest it.
