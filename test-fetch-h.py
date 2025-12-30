import json
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


def main():
    with open("data/metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 "
            "Safari/537.36 "
            "Edg/131.0.0.0"
        )
    }
    with httpx.Client(headers=headers, timeout=600) as client:
        for pub in metadata:
            id_publicacao = pub["id_publicacao"]
            titulo = pub["titulo"]
            ano_publicacao = pub["ano_publicacao"]
            mes_publicacao = pub["mes_publicacao"]
            print(f"# {id_publicacao} {titulo} ({ano_publicacao}-{mes_publicacao:0>2})")
            dest_dir = Path(f"data/{ano_publicacao}-{mes_publicacao:0>2}")
            dest_dir.mkdir(parents=True, exist_ok=True)
            for file in pub["links"]:
                dest_file = dest_dir / file
                if dest_file.exists():
                    continue
                url = pub["links"][file]
                print(f"## {file}: {url}")
                r = client.get(url, follow_redirects=True)
                content_type = r.headers.get("Content-Type", "")
                print(f"## Content-Type: {content_type}")
                if content_type.startswith("text/html"):
                    soup = BeautifulSoup(r.text, "html.parser")
                    iframe = soup.find("iframe")
                    iframe_src = iframe["src"]
                    print(f"## {iframe_src}")
                    r = client.get(iframe_src)
                    dest_file.write_bytes(r.content)
                else:
                    print(f"## Unknown content type: {content_type}")
                    dest_file.write_bytes(r.content)


if __name__ == "__main__":
    main()
