#!/usr/bin/env python3
"""Inventory public videos and request available English captions without video download."""
import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

TABS = ("videos", "shorts", "streams")


def extract_ids(data):
    return [e.get("id") for e in data.get("entries", []) if isinstance(e, dict) and e.get("id")]


def index_files(base):
    records = {}
    for path in sorted(base.glob("*/*.info.json")):
        try:
            info = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        video_id = info.get("id")
        if not video_id:
            continue
        subs = sorted(path.parent.glob(str(video_id) + ".*.vtt"))
        records[(path.parent.name, str(video_id))] = {
            "creator": path.parent.name, "video_id": str(video_id),
            "title": info.get("title", ""), "upload_date": info.get("upload_date", ""),
            "url": info.get("webpage_url") or "https://www.youtube.com/watch?v=" + str(video_id),
            "caption_status": "downloaded" if subs else "not_downloaded_or_unavailable",
            "caption_files": "|".join(p.name for p in subs)
        }
    outfile = base / "caption_index.csv"
    with outfile.open("w", newline="", encoding="utf-8") as f:
        cols = ("creator", "video_id", "title", "upload_date", "url", "caption_status", "caption_files")
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(records.values())
    return len(records), outfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=Path("private-youtube-research"))
    p.add_argument("--config", type=Path, default=Path(__file__).with_name("channels.json"))
    p.add_argument("--max-per-tab", type=int, default=0, help="Zero means all available items")
    p.add_argument("--only", nargs="*", default=[], help="Filter by channel name")
    p.add_argument("--catalog-only", action="store_true", help="List video IDs without captions")
    args = p.parse_args()
    if not shutil.which("yt-dlp"):
        sys.exit("yt-dlp not found. Install from https://github.com/yt-dlp/yt-dlp")
    channels = json.loads(args.config.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    failures = []
    for channel in channels:
        name = channel["name"]
        if args.only and name not in args.only:
            continue
        directory = args.out / name
        directory.mkdir(parents=True, exist_ok=True)
        for tab in TABS:
            url = channel["url"].rstrip("/") + "/" + tab
            extra = ["--playlist-end", str(args.max_per_tab)] if args.max_per_tab > 0 else []
            if args.catalog_only:
                cmd = ["yt-dlp", "--flat-playlist", "--dump-single-json", "--ignore-errors",
                       "--no-warnings"] + extra + [url]
                output = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if output.returncode or not output.stdout.strip():
                    failures.append((name, tab, output.returncode))
                    continue
                try:
                    catalog = json.loads(output.stdout)
                except ValueError:
                    failures.append((name, tab, "bad JSON"))
                    continue
                (directory / (tab + "_catalog.json")).write_text(
                    json.dumps({"name": name, "tab": tab, "video_ids": extract_ids(catalog),
                                "entries": catalog.get("entries", [])}, ensure_ascii=False, indent=2))
            else:
                cmd = ["yt-dlp", "--skip-download", "--write-info-json", "--write-subs",
                       "--write-auto-subs", "--sub-langs", "en.*,en", "--sub-format", "vtt",
                       "--ignore-errors", "--no-warnings", "--no-overwrites",
                       "--sleep-requests", "1", "--sleep-interval", "2", "--max-sleep-interval", "5",
                       "--download-archive", str(directory / "archive.txt"),
                       "-o", str(directory / "%(id)s.%(ext)s")] + extra + [url]
                rc = subprocess.run(cmd, check=False).returncode
                if rc:
                    failures.append((name, tab, rc))
    if not args.catalog_only:
        count, path = index_files(args.out)
        print(f"Indexed {count} local video records; audit CSV: {path}")
    if failures:
        print(f"Partial coverage; {len(failures)} tabs failed or were inaccessible")
        for failure in failures:
            print("WARNING", failure)
        return 2
    print("Requested tabs processed. Not proof of complete channel or subtitle coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
