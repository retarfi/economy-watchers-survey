import glob
import json
import os
import re
from pathlib import Path

import pandas as pd

from . import DATA_DIR

col_default: list[str] = ["id", "year-month", "地域", "関連", "業種・職種"]
COL_CURRENT: list[str] = col_default + [
    "景気の現状判断",
    "判断の理由",
    "追加説明及び具体的状況の説明",
]
COL_FUTURE: list[str] = col_default + [
    "景気の先行き判断",
    "景気の先行きに対する判断理由",
]


def filter_df_comment(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df = df[df[col_name].str.len() > 3]
    df.loc[:, col_name] = df[col_name].map(
        lambda text: "".join(map(lambda x: x.lstrip("・"), text.split("\n")))
    )
    return df


def extract_data(csv_path: str, do_filter: bool) -> pd.DataFrame:
    m: re.Match = re.match(r"(\d{6})_watcher(4|5)\.csv", os.path.basename(csv_path))
    year_month: str = m.group(1)
    num_type: str = m.group(2)
    df: pd.DataFrame
    try:
        df = pd.read_csv(csv_path, encoding="cp932", header=7)
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="utf-8", header=7)
    df["year-month"] = year_month
    if num_type == "4" and int(year_month) <= 200107:
        df.rename(
            columns={
                "景気の現状に対する判断理由": "判断の理由",
                "Unnamed: 5": "追加説明及び具体的状況の説明",
            },
            inplace=True,
        )
    df["地域"] = ""
    idx_col_region: int = df.columns.get_loc("地域")
    df["関連"] = ""
    idx_col_field: int = df.columns.get_loc("関連")
    for i in range(len(df)):
        if isinstance(df.iat[i, 0], str) and "関連" in df.iat[i, 0]:
            region: str = re.search(r"\((.*?)\)", df.iat[i, 0]).group(1)
            field: str = re.match(r"(.*?)関連", df.iat[i, 0].replace("\n", "")).group(1)
        df.iat[i, idx_col_region] = region
        df.iat[i, idx_col_field] = field
    df["id"] = ""  # temporary
    tpl_eval: tuple[str] = ("◎", "○", "□", "▲", "×")
    col_name: str
    id_prefix: str
    if num_type == "4":
        df = df[df["景気の現状判断"].isin(tpl_eval)][COL_CURRENT]
        col_name = "追加説明及び具体的状況の説明"
        id_prefix = "current"
    elif num_type == "5":
        df = df[df["景気の先行き判断"].isin(tpl_eval)][COL_FUTURE]
        col_name = "景気の先行きに対する判断理由"
        id_prefix = "future"
    else:
        raise ValueError()
    if do_filter:
        df = filter_df_comment(df, col_name)
    df.reset_index(drop=True, inplace=True)
    assert len(df) > 0
    df["id"] = df.apply(
        lambda row: "{}-{}-{:04d}".format(id_prefix, row["year-month"], row.name),
        axis=1,
    )
    return df


def output_df_in_jsonl(df: pd.DataFrame, dirname: str, year_month: str) -> None:
    lst: list[dict[str, str]] = df.where(df.notnull(), None).to_dict("records")
    p_dir: Path = DATA_DIR / dirname
    os.makedirs(p_dir, exist_ok=True)
    with open(p_dir / f"{year_month}.json", mode="w", encoding="utf-8") as f:
        json.dump(lst, f, indent=2, ensure_ascii=False, allow_nan=False)


def csv_to_json(do_filter: bool = True) -> None:
    for csv_path in sorted(glob.glob(str(DATA_DIR / "watcher" / "*" / "*.csv"))):
        print(f"\rProcessing {os.path.basename(csv_path)}", end="")
        df: pd.DataFrame = extract_data(csv_path, do_filter=do_filter)
        m: re.Match = re.match(r"(\d{6})_watcher(4|5)\.csv", os.path.basename(csv_path))
        year_month: str = m.group(1)
        num_type: str = m.group(2)
        if num_type == "4":  # 現状
            output_df_in_jsonl(df, "current", year_month)
        elif num_type == "5":  # 先行き
            output_df_in_jsonl(df, "future", year_month)
        else:
            raise ValueError()


if __name__ == "__main__":
    csv_to_json()
