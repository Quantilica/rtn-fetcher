from rtnpy import fetcher
from pathlib import Path


def main():
    fetcher.fetch_file(data_dir=Path("data"))


if __name__ == "__main__":
    main()
