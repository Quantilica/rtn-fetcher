#!/usr/bin/env python3
"""Command-line tool merging metadata fetch and file download utilities.

Provides these subcommands:
- metadata: fetch/save metadata.html and metadata.json
- download: download files listed in metadata.json
- latest: call `download_latest_file` from `rtnpy`

Usage examples:
  python fetch.py metadata
  python fetch.py download
  python fetch.py latest
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict
import asyncio

import httpx
from bs4 import BeautifulSoup

from rtnpy import (
    fetch_publications_metadata,
    extract_publication_metadata,
    download_latest_file,
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 "
        "Safari/537.36 "
        "Edg/131.0.0.0"
    )
}

DEFAULT_DATA_DIR = Path("data")
DEFAULT_HTML = DEFAULT_DATA_DIR / "metadata.html"
DEFAULT_JSON = DEFAULT_DATA_DIR / "metadata.json"


def cmd_metadata(args: argparse.Namespace) -> int:
    out_html = Path(args.html)
    out_json = Path(args.json)

    if out_html.exists() and not args.force:
        with out_html.open("r", encoding=args.encoding) as f:
            metadata_html = f.read()
    else:
        metadata_html = fetch_publications_metadata()
        out_html.parent.mkdir(parents=True, exist_ok=True)
        with out_html.open("w", encoding=args.encoding) as f:
            f.write(metadata_html)

    soup = BeautifulSoup(metadata_html, "html.parser")
    publications = extract_publication_metadata(soup)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding=args.encoding) as f:
        json.dump(publications, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(publications)} publications to {out_json}")
    return 0


async def _download_link_async(
    pub: Dict,
    filename: str,
    url: str,
    client: httpx.AsyncClient,
    dest_root: Path,
    encoding: str,
) -> None:
    """Asynchronously download a single publication link to disk."""
    ano = pub.get("ano_publicacao")
    mes = pub.get("mes_publicacao")
    dest_dir = dest_root / f"{ano}-{mes:0>2}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_file = dest_dir / filename
    if dest_file.exists():
        return

    print(f"Downloading {url} -> {dest_file}")
    r = await client.get(url, follow_redirects=True)
    content_type = r.headers.get("Content-Type", "")
    if content_type.startswith("text/html"):
        soup = BeautifulSoup(r.text, "html.parser")
        iframe = soup.find("iframe")
        if iframe and iframe.get("src"):
            iframe_src = iframe["src"]
            print(f"Following iframe src: {iframe_src}")
            r2 = await client.get(iframe_src)
            data = r2.content
            await asyncio.to_thread(dest_file.write_bytes, data)
        else:
            # Save HTML text
            await asyncio.to_thread(dest_file.write_text, r.text, encoding)
    else:
        await asyncio.to_thread(dest_file.write_bytes, r.content)


def cmd_download(args: argparse.Namespace) -> int:
    metadata_path = Path(args.metadata)
    if not metadata_path.exists():
        print(f"Metadata file not found: {metadata_path}")
        return 2

    with metadata_path.open("r", encoding=args.encoding) as f:
        publications = json.load(f)

    # Run asynchronous downloads with concurrency control
    async def _run_async_downloads() -> None:
        semaphore = asyncio.Semaphore(args.concurrency)

        async with httpx.AsyncClient(headers=HEADERS, timeout=600) as client:
            tasks = []

            async def _bounded(pub: Dict, filename: str, url: str) -> None:
                async with semaphore:
                    try:
                        await _download_link_async(
                            pub, filename, url, client, Path(args.dest), args.encoding
                        )
                    except Exception as exc:
                        print(f"Error downloading {url}: {exc}")

            for pub in publications:
                for filename, url in pub.get("links", {}).items():
                    tasks.append(_bounded(pub, filename, url))

            if tasks:
                await asyncio.gather(*tasks)

    asyncio.run(_run_async_downloads())
    return 0


def cmd_latest(args: argparse.Namespace) -> int:
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    filepath = download_latest_file(dest)
    if filepath:
        print(f"Downloaded: {filepath}")
        return 0
    else:
        print("File already exists")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fetch", description="RTN data helper CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_meta = sub.add_parser(
        "metadata", help="Fetch metadata HTML and generate metadata.json"
    )
    p_meta.add_argument(
        "--html", default=str(DEFAULT_HTML), help="Output metadata HTML path"
    )
    p_meta.add_argument(
        "--json", default=str(DEFAULT_JSON), help="Output metadata JSON path"
    )
    p_meta.add_argument("--encoding", default="utf-8", help="File encoding")
    p_meta.add_argument(
        "--force", action="store_true", help="Refetch HTML even if it exists"
    )
    p_meta.set_defaults(func=cmd_metadata)

    p_dl = sub.add_parser("download", help="Download files referenced in metadata.json")
    p_dl.add_argument(
        "--metadata", default=str(DEFAULT_JSON), help="Input metadata JSON path"
    )
    p_dl.add_argument(
        "--dest", default=str(DEFAULT_DATA_DIR), help="Destination root directory"
    )
    p_dl.add_argument(
        "--encoding", default="utf-8", help="File encoding for HTML files"
    )
    p_dl.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Maximum concurrent downloads (default: 4)",
    )
    p_dl.set_defaults(func=cmd_download)

    p_latest = sub.add_parser("latest", help="Download latest single file")
    p_latest.add_argument(
        "--dest", default=str(DEFAULT_DATA_DIR), help="Destination directory"
    )
    p_latest.set_defaults(func=cmd_latest)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
