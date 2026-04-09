#!/usr/bin/env python3
"""Download an article, clean it, convert to PDF, upload to Google Drive."""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from readability import Document
from weasyprint import HTML


def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/131.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_metadata(html, url):
    soup = BeautifulSoup(html, "html.parser")
    meta = {}

    og = soup.find("meta", property="og:title")
    meta["title"] = og["content"] if og and og.get("content") else (
        soup.title.string.strip() if soup.title and soup.title.string else "Untitled"
    )

    for attr in [
        {"name": "author"},
        {"property": "article:author"},
        {"name": "twitter:creator"},
    ]:
        tag = soup.find("meta", attrs=attr)
        if tag and tag.get("content"):
            meta["author"] = tag["content"].strip()
            break
    if "author" not in meta:
        for script in soup.find_all("script", type="application/ld+json"):
            if script.string and '"author"' in script.string:
                try:
                    ld = json.loads(script.string)
                    if isinstance(ld, list):
                        ld = ld[0]
                    a = ld.get("author", {})
                    if isinstance(a, list):
                        a = a[0]
                    if isinstance(a, dict):
                        meta["author"] = a.get("name", "")
                    elif isinstance(a, str):
                        meta["author"] = a
                except Exception:
                    pass
                if meta.get("author"):
                    break
    meta.setdefault("author", "Unknown")

    for attr in [
        {"property": "article:published_time"},
        {"name": "publication_date"},
        {"property": "og:article:published_time"},
        {"name": "date"},
    ]:
        tag = soup.find("meta", attrs=attr)
        if tag and tag.get("content"):
            meta["date"] = tag["content"].strip()[:10]
            break
    if "date" not in meta:
        tag = soup.find("time", {"datetime": True})
        if tag:
            meta["date"] = tag["datetime"][:10]
    meta.setdefault("date", datetime.now().strftime("%Y-%m-%d"))

    og_site = soup.find("meta", property="og:site_name")
    if og_site and og_site.get("content"):
        meta["publisher"] = og_site["content"].strip()
    else:
        domain = urlparse(url).netloc.replace("www.", "")
        meta["publisher"] = domain

    return meta


def clean_article(html):
    doc = Document(html)
    return doc.summary()


def fix_images(html_content, base_url):
    soup = BeautifulSoup(html_content, "html.parser")
    for img in soup.find_all("img"):
        for attr in ["data-src", "data-lazy-src", "data-original"]:
            if img.get(attr):
                img["src"] = img[attr]
                break
        if img.get("src") and not img["src"].startswith("http"):
            img["src"] = urljoin(base_url, img["src"])
        if img.get("srcset"):
            del img["srcset"]
    return str(soup)


def build_pdf_html(meta, article_html):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 2.5cm 2cm;
  }}
  body {{
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a1a;
  }}
  .header {{
    border-bottom: 2px solid #333;
    padding-bottom: 16px;
    margin-bottom: 28px;
  }}
  .header h1 {{
    font-size: 22pt;
    margin: 0 0 12px 0;
    line-height: 1.25;
  }}
  .meta {{
    font-size: 9.5pt;
    color: #555;
    font-family: Helvetica, Arial, sans-serif;
  }}
  .meta span {{
    margin-right: 18px;
  }}
  img {{
    max-width: 100%;
    height: auto;
  }}
  a {{
    color: #1a5276;
  }}
  blockquote {{
    border-left: 3px solid #ccc;
    margin-left: 0;
    padding-left: 16px;
    color: #444;
  }}
</style>
</head>
<body>
  <div class="header">
    <h1>{meta["title"]}</h1>
    <div class="meta">
      <span><b>By</b> {meta["author"]}</span>
      <span><b>Published</b> {meta["date"]}</span>
      <span><b>Source</b> {meta["publisher"]}</span>
    </div>
  </div>
  <article>
    {article_html}
  </article>
</body>
</html>"""


def sanitize(text):
    return re.sub(r'[\\/*?:"<>|]', "", text).strip()[:80]


def upload_rclone(filepath, folder):
    dest = f"gdrive:{folder}/" if folder else "gdrive:"
    ret = os.system(f'rclone copy "{filepath}" "{dest}" --progress')
    if ret != 0:
        print("rclone upload failed", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Article URL")
    parser.add_argument("--folder", default="Articles")
    args = parser.parse_args()

    print("Fetching article...")
    html = fetch_page(args.url)

    print("Extracting metadata...")
    meta = extract_metadata(html, args.url)

    print(f"Title:     {meta['title']}")
    print(f"Author:    {meta['author']}")
    print(f"Date:      {meta['date']}")
    print(f"Publisher: {meta['publisher']}")

    print("Cleaning article...")
    article_html = clean_article(html)
    article_html = fix_images(article_html, args.url)

    print("Generating PDF...")
    pdf_html = build_pdf_html(meta, article_html)
    filename = f"{meta['date']} - {sanitize(meta['title'])} - {sanitize(meta['publisher'])}.pdf"
    output_path = f"/tmp/{filename}"
    HTML(string=pdf_html).write_pdf(output_path)

    print(f"Uploading to Google Drive ({args.folder})...")
    upload_rclone(output_path, args.folder)
    os.remove(output_path)
    print("Done!")
    print(f"RESULT: Saved '{filename}' to Google Drive > {args.folder}")


if __name__ == "__main__":
    main()
