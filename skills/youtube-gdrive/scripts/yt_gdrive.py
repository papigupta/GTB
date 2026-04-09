#!/usr/bin/env python3
"""Download YouTube video/audio and upload to Google Drive via rclone."""

import sys, os, subprocess, argparse, re, glob

def download(url, mode, output_path):
    if mode == "audio":
        cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", output_path, url]
    else:
        cmd = ["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4", "-o", output_path, url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Download error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

def upload_rclone(filepath, folder):
    cmd = ["rclone", "copy", filepath, f"gdrive:{folder}", "--progress"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Upload error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"Uploaded to Google Drive: {folder}/{os.path.basename(filepath)}")

def sanitize(s):
    return re.sub(r'[\\/*?:"<>|]', '', s).strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("mode", choices=["audio", "video"])
    parser.add_argument("--artist", default="Unknown Artist")
    parser.add_argument("--title", default="Unknown Title")
    parser.add_argument("--album", default="Single")
    parser.add_argument("--folder", default="")
    args = parser.parse_args()

    ext = "mp3" if args.mode == "audio" else "mp4"
    filename = f"{sanitize(args.artist)} - {sanitize(args.title)} - {sanitize(args.album)}.{ext}"
    output_path = f"/tmp/{filename}"

    print(f"Downloading as {args.mode}...")
    download(args.url, args.mode, output_path)

    actual = output_path
    if not os.path.exists(actual):
        candidates = glob.glob(output_path + "*") + glob.glob(output_path.rsplit(".", 1)[0] + ".*")
        if candidates:
            actual = candidates[0]
        else:
            print("Error: file not found", file=sys.stderr)
            sys.exit(1)

    folder = args.folder if args.folder else ("Music" if args.mode == "audio" else "Videos")	
    print(f"Uploading {os.path.basename(actual)} to {folder}...")
    upload_rclone(actual, folder)
    os.remove(actual)
    print("Done!")

if __name__ == "__main__":
    main()
