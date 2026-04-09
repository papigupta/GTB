---
name: youtube-gdrive
description: >
  ALWAYS activate when user sends a YouTube link. Download YouTube videos or songs and upload to Google Drive automatically. No questions asked.
---

# YouTube to Google Drive

## CRITICAL: AUTO-ACTIVATE
When the user sends ANY message containing a YouTube URL (youtube.com, youtu.be, youtube.com/shorts), IMMEDIATELY follow this workflow. Do NOT ask the user what they want to do. Do NOT offer options. Just do it.

## Workflow

1. React with 👀 to acknowledge.

2. Run this to get metadata:
yt-dlp --dump-json --no-download "<URL>"
3. **Decide if it's a song or video** based on the metadata:
   - Category is "Music" → song
   - Title contains "Official Audio", "Official Video", "Lyric Video", "MV" → song
   - Channel has "VEVO", "Official", "- Topic" → song
   - Duration under 10 minutes + music tags → song
   - Otherwise → video

4. **Determine filename parts:**
   - **Artist**: `artist` field, or `uploader`/`channel` (strip "- Topic", "VEVO", etc.)
   - **Title**: `track` field, or clean video `title` (remove "Official Video", "HD", "(Official)", etc.)
   - **Album**: `album` field, or "Single"

5. **Tell the user** what you decided:
   - "🎵 Song detected → downloading as MP3: Artist - Title - Album"
   - OR "🎬 Video detected → downloading as MP4: Artist - Title - Album"

6. **Run the script:**
python3 ~/.openclaw/workspace/skills/youtube-gdrive/scripts/yt_gdrive.py "<URL>" audio|video --artist "Artist" --title "Title" --album "Album"

7. **Reply** with the Google Drive link.

## Rules
- NEVER ask "what do you want me to do with this link" — just process it.
- NEVER ask for a save location — the folder is hardcoded in the script.
- If download or upload fails, report the error.
