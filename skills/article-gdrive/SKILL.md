# Article to Google Drive

Save a web article as a clean, ad-free PDF to Google Drive.

## When to use

Use this skill when the user sends a URL to a web article, blog post, or news story and wants it saved. Do NOT use for YouTube links (use youtube-gdrive instead).

## Command

```bash
python3 ~/.openclaw/workspace/skills/article-gdrive/scripts/article_gdrive.py "<URL>"
```

## What it does

1. Downloads the article
2. Strips ads, navigation, popups — keeps only the article text and images
3. Extracts: headline, author, publication date, publisher
4. Generates a clean, beautifully formatted PDF
5. Uploads to Google Drive > Articles folder
6. Filename format: `YYYY-MM-DD - Headline - Publisher.pdf`

## Tell the user

After running, tell the user:
- The article title
- The author and publisher
- That it's been saved to their Articles folder on Google Drive
