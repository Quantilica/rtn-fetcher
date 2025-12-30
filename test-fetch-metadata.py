import json
from bs4 import BeautifulSoup
from pathlib import Path
from rtnpy import fetcher

from rtnpy.extract import extract_metadata


def load_metadata():
    filepath = Path("data", "metadata.html")
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            metadata = f.read()
    else:
        metadata = fetcher.fetch_metadata()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(metadata)
    return metadata


def main():
    metadata = load_metadata()
    soup = BeautifulSoup(metadata, "html.parser")
    cards_infos = extract_metadata(soup)
    with open("data/metadata.json", "w", encoding="utf-8") as f:
        json.dump(cards_infos, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
