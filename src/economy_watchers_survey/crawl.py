import datetime
import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from . import DATA_DIR


def get_all_urls(url: str) -> list[str]:
    # webページ内の全urlを取得する関数
    res: requests.Response = requests.get(url)
    assert res.status_code == 200, res.status_code
    soup: BeautifulSoup = BeautifulSoup(res.text, "html.parser")
    links: list[str] = [
        x.attrs["href"]
        for x in soup.find_all("a")
        if hasattr(x, "attrs") and "href" in x.attrs.keys()
    ]
    return sorted(links)


def _download_file(url: str, local_path: os.PathLike) -> None:
    res = requests.get(url)
    assert res.status_code == 200, (url, res.status_code)
    with open(local_path, mode="wb") as f:
        f.write(res.content)


def download() -> None:
    base_url: str = "http://www5.cao.go.jp/keizai3/"
    # 2010年以降のデータのリンクを取得
    lst_url: list[str] = get_all_urls(urljoin(base_url, "watcher_index.html"))
    lst_url += get_all_urls(urljoin(base_url, "kako_watcher.html"))

    # 景気判断理由の現状（watcher4）と先行き（watcher5）をダウンロードし、yyyymm_watcher<4|5>.csvとして保存
    for url in filter(lambda x: "watcher/menu.html" in x, sorted(lst_url)):
        m: Optional[re.Match] = re.search(
            r"(2\d{3})/(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])", url
        )
        # ファイル名の年月は調査の1ヶ月後なので1ヶ月戻す
        dt: datetime.date = datetime.date(
            int(m.group(1)), int(m.group(2)), 1
        ) - relativedelta(months=1)
        if dt.year <= 2009:
            continue
        year: str = str(dt.year)
        month: str = f"{dt.month:02d}"

        p_year: Path = DATA_DIR / "watcher" / year
        os.makedirs(p_year, exist_ok=True)
        for i in (4, 5):
            p_csv: Path = p_year / f"{year}{month}_watcher{i}.csv"
            if p_csv.exists():
                continue
            print(f"{year}{month}_watcher{i}")
            _download_file(
                urljoin(base_url, url.replace("menu.html", f"watcher{i}.csv")), p_csv
            )

    # 2009年以前のデータのリンクを取得し2012年以降のデータと同様の形式で保存
    lst_url = get_all_urls(urljoin(base_url, "kako_csv/kako2_watcher.html"))
    for csv_name in lst_url:
        if m := re.match(r"h(1\d|2\d)(0[1-9]|1[0-2])_watcher(4|5).csv", csv_name):
            year = str(1988 + int(m.group(1)))
            month = m.group(2)
            p_year: Path = DATA_DIR / "watcher" / year
            p_csv: Path = p_year / f"{year}{month}_watcher{m.group(3)}.csv"
            if p_csv.exists():
                continue
            os.makedirs(p_year, exist_ok=True)
            print(f"{year}{month}_watcher{m.group(3)}")
            _download_file(urljoin(base_url, f"kako_csv/{csv_name}"), p_csv)


if __name__ == "__main__":
    download()
