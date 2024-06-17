<div id="top"></div>

<h1 align="center">Economy Watchers Survey data</h1>

<p align="center">
  <a href="https://github.com/retarfi/economy-watchers-survey/releases">
    <img alt="GitHub release" src="https://img.shields.io/github/v/release/retarfi/economy-watchers-survey.svg">
  </a>
  <a href="https://github.com/retarfi/economy-watchers-survey#license">
    <img alt="License" src="https://img.shields.io/badge/License_(code)-MIT-yellow">
  </a>
  <a href="https://github.com/retarfi/economy-watchers-survey/blob/main/data/LICENSE">
    <img alt="License" src="https://img.shields.io/badge/License_(data)-CC_BY_4.0-lightgrey.svg">
  </a><br>
  <a href="https://github.com/retarfi/economy-watchers-survey/actions/workflows/build-test.yml">
    <img alt="Test" src="https://github.com/retarfi/economy-watchers-survey/actions/workflows/build-test.yml/badge.svg">
  </a>
  <a href="https://github.com/retarfi/economy-watchers-survey/actions/workflows/release.yml">
    <img alt="Test" src="https://github.com/retarfi/economy-watchers-survey/actions/workflows/release.yml/badge.svg">
  </a>
  <a href="https://github.com/retarfi/economy-watchers-survey/actions/workflows/schedule.yml">
    <img alt="Test" src="https://github.com/retarfi/economy-watchers-survey/actions/workflows/schedule.yml/badge.svg">
  </a>
</p>


Auto uploader for [Economy Watchers Survey data](https://www5.cao.go.jp/keizai3/watcher-e/index-e.html).  
It is automatically updated by GitHub Actions as the economy watcher is updated.  
Dataset on HuggingFace: https://huggingface.co/datasets/retarfi/economy-watchers-survey  

[景気ウォッチャー調査](https://www5.cao.go.jp/keizai3/watcher/watcher_menu.html)のデータを自動更新・整形・抽出を行います。  
自動更新はGitHub Actionsによって月次で行われます。  
データセットはHuggingFaceからも利用可能です: https://huggingface.co/datasets/retarfi/economy-watchers-survey  


## Data Structure
The csv data of the economy watcher is stored as `data/2024/202401_watcher4.csv`.  
The `watcher4.csv` is a questionnaire about the current judgment of the economy and `watcher5.csv` is a questionnaire about the future judgment of the economy.  
The extracted data after filtering for current and future judgments in json format are stored as `data/current/202401.json` and `data/future/202401.json`, respectively.

景気ウォッチャーのcsvデータは`data/2024/202401_watcher4.csv`のように格納されています。  
`watcher4.csv`は景気の現状判断について、`watcher5.csv`は景気の先行き判断についてのアンケートです。  
json形式での現状・先行きの判断についてフィルタリングを行った後に抽出したものをそれぞれ`data/current/202401.json`や`data/future/202401.json`のように格納しています。


## License
The codes in this repository are distributed under MIT.  
The data is distributed under CC BY 4.0.


## Citation
TBA


## Usage for local download
```sh
poetry run python -m src.economy_watchers_survey.crawl
poetry run python -m src.economy_watchers_survey.create_json
```


## Format
```sh
poetry run black --check --diff --quiet --skip-magic-trailing-comma .
poetry run isort --check --diff --quiet .
```
