#!/usr/bin/env python3
"""Download an article, clean it, convert to PDF, upload to Google Drive."""

import argparse
import base64
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

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36"
})


def fetch_page(url):
    resp = SESSION.get(url, timeout=30)
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


def extract_article_images(raw_html):
    """Get content images from raw HTML before readability strips them."""
    soup = BeautifulSoup(raw_html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        # Only keep large content images, skip avatars/icons
        if "w_1456" in src or "w_1272" in src or "w_848" in src:
            images.append(src)
        elif img.get("width") and int(img.get("width", 0)) > 200:
            images.append(src)
    return images


def download_image_as_base64(url):
    """Download an image and return as base64 data URI."""
    try:
        print(f"  Downloading image: {url[:80]}...")
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0]
        b64 = base64.b64encode(resp.content).decode("utf-8")
        return f"data:{content_type};base64,{b64}"
    except Exception as e:
        print(f"  Failed to download image: {e}")
        return None


def clean_article(raw_html, base_url):
    """Clean article and re-inject images that readability stripped."""
    # Grab content images before readability kills them
    article_images = extract_article_images(raw_html)

    # Run readability
    doc = Document(raw_html)
    cleaned = doc.summary()
    soup = BeautifulSoup(cleaned, "html.parser")

    # Check if readability kept any images
    existing = len(soup.find_all("img"))

    if existing == 0 and article_images:
        print(f"  Readability stripped images. Re-injecting {len(article_images)}...")
        # Find all paragraphs and distribute images evenly
        paragraphs = soup.find_all("p")
        if paragraphs:
            # Place images roughly evenly throughout the article
            interval = max(1, len(paragraphs) // (len(article_images) + 1))
            for i, img_url in enumerate(article_images):
                b64 = download_image_as_base64(img_url)
                if b64:
                    img_tag = soup.new_tag("img", src=b64, style="max-width:100%;height:auto;margin:16px 0;")
                    pos = min((i + 1) * interval, len(paragraphs) - 1)
                    paragraphs[pos].insert_after(img_tag)
        else:
            # No paragraphs, just append at the end
            for img_url in article_images:
                b64 = download_image_as_base64(img_url)
                if b64:
                    img_tag = soup.new_tag("img", src=b64, style="max-width:100%;height:auto;margin:16px 0;")
                    soup.append(img_tag)
    else:
        # Readability kept images — download and embed them as base64
        for img in soup.find_all("img"):
            src = get_best_image_url(img, base_url)
            if src:
                b64 = download_image_as_base64(src)
                if b64:
                    img["src"] = b64
            for attr in ["srcset", "data-src", "data-lazy-src", "loading"]:
                if img.get(attr):
                    del img[attr]

    return str(soup)


def get_best_image_url(img, base_url):
    """Try every possible source for an image URL."""
    for attr in ["data-src", "data-lazy-src", "data-original", "data-attrs-src"]:
        val = img.get(attr)
        if val and val.startswith("http"):
            return val

    srcset = img.get("srcset", "")
    if srcset:
        parts = srcset.split(",")
        for part in reversed(parts):
            url = part.strip().split()[0]
            if url.startswith("http"):
                return url

    src = img.get("src", "")
    if src and not src.startswith("data:"):
        if src.startswith("http"):
            return src
        return urljoin(base_url, src)

    return None


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

    print("Cleaning article and processing images...")
    article_html = clean_article(html, args.url)

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
