from pathlib import Path
from rtnpy import download_latest_file


def main():
    data_dir = Path("data")
    filepath = download_latest_file(data_dir)
    if filepath:
        print(f"Downloaded: {filepath}")
    else:
        print("File already exists")


if __name__ == "__main__":
    main()
