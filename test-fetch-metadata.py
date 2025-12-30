import json
from pathlib import Path

from bs4 import BeautifulSoup

from rtnpy import fetch_publications_metadata, extract_publication_metadata


def load_metadata():
    filepath = Path("data", "metadata.html")
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            metadata = f.read()
    else:
        metadata = fetch_publications_metadata()
        filepath.parent.mkdir(exist_ok=True, parents=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(metadata)
    return metadata


def main():
    metadata = load_metadata()
    soup = BeautifulSoup(metadata, "html.parser")
    publications = extract_publication_metadata(soup)

    output_path = Path("data/metadata.json")
    output_path.parent.mkdir(exist_ok=True, parents=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(publications, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(publications)} publications to {output_path}")


if __name__ == "__main__":
    main()
