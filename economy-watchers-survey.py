import glob
import json
import os

import datasets
from datasets import DatasetInfo, SplitGenerator, Value

VERSION = "2024.03.0"
EWS_DESCRIPTION: str = (
    "The purpose of the survey is to promptly gain an accurate grasp of "
    "region-by-region economic trends. By enlisting the cooperation of people holding "
    "jobs that enable them to observe activity closely related to regional economy, "
    "these survey results can be used as basic material for assessing economic trends. "
    "2,050 people were selected from among those engaged in jobs in industries that "
    "enable them to observe any development that sensitively reflects economic "
    "activities, such as household activity, corporate activity, and employment."
)
col_default: list[str] = ["year-month", "地域", "関連", "業種・職種"]
COL_CURRENT: list[str] = col_default + [
    "景気の現状判断",
    "判断の理由",
    "追加説明及び具体的状況の説明",
]
COL_FUTURE: list[str] = col_default + [
    "景気の先行き判断",
    "景気の先行きに対する判断理由",
]


class EconomyWatchersSurveyConfig(datasets.BuilderConfig):
    def __init__(self, features: list[str], num_files_split_buffer: int, **kwargs):
        super().__init__(version=datasets.Version(VERSION), **kwargs)
        self.features = features
        self.test_ratio = 0.1
        self.num_files_split_buffer = num_files_split_buffer


class EconomyWatchersSurvey(datasets.GeneratorBasedBuilder):
    BUILDER_CONFIG_CLASS = EconomyWatchersSurveyConfig

    BUILDER_CONFIGS = [
        EconomyWatchersSurveyConfig(
            name="current",
            data_dir="data/current/",
            features=COL_CURRENT,
            num_files_split_buffer=23,
            description=(
                "The current subset contains the assessment of current economic "
                "conditions (direction), the reasons for the conditions, "
                "the additional explanation of the reasons, and the explanation of "
                "specific conditions."
            ),
        ),
        EconomyWatchersSurveyConfig(
            name="future",
            data_dir="data/future/",
            features=COL_FUTURE,
            num_files_split_buffer=46,
            description=(
                "The future subset contains the assessment of future economic "
                "conditions (direction) and the reasons for the conditions."
            ),
        ),
    ]

    def _info(self) -> DatasetInfo:
        features: dict[str, Value] = {
            feature: Value("string") for feature in self.config.features
        }
        return DatasetInfo(
            description=EWS_DESCRIPTION + self.config.description,
            features=datasets.Features(features),
            homepage="https://www5.cao.go.jp/keizai3/watcher-e/index-e.html",
            # citaion=CITATION,
        )

    def _split_generators(
        self, dl_manager: datasets.DownloadManager
    ) -> list[SplitGenerator]:
        data_files: list[str] = sorted(
            glob.glob(os.path.join("data", self.config.name, "*.json"))
        )
        num_test_files: int = int(
            (len(data_files) - self.config.num_files_split_buffer)
            * self.config.test_ratio
        )
        # downloaded_files = dl_manager.download(urls_to_download)
        return [
            SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"data_files": data_files[:-num_test_files]},
            ),
            SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"data_files": data_files[-num_test_files:]},
            ),
        ]

    def _generate_examples(self, data_files: list[str]):
        for filepath in data_files:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            for example in data:
                yield example["id"], example
