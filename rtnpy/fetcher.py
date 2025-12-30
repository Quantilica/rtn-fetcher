import datetime as dt
from pathlib import Path

import httpx


def fetch_metadata() -> str:
    url = "https://apiapex.tesouro.gov.br/aria//v1/thot/custom/rtn?pageSize=9999999"
    r = httpx.get(url, timeout=60)
    return r.text


def get_destfilename(modified: dt.datetime) -> str:
    filename = f"rtn_{modified:%Y%m%d%H%M}.xlsx"
    return filename


def fetch_file(data_dir: Path):
    url = (
        "http://sisweb.tesouro.gov.br"
        "/apex/cosis/thot/link/rtn/serie-historica?conteudo=cdn"
    )
    r = httpx.get(url, follow_redirects=True)
    modified = dt.datetime.strptime(
        r.headers.get("Last-Modified"),
        "%a, %d %b %Y %H:%M:%S %Z",
    )
    filename = get_destfilename(modified)
    dest_filepath = data_dir / filename
    if dest_filepath.exists():
        return
    dest_filepath.parent.mkdir(exist_ok=True, parents=True)
    with dest_filepath.open("wb") as f:
        f.write(r.content)
