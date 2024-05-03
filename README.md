# economy-watchers-survey
English:  
Auto uploader for [Economy Watchers Survey data](https://www5.cao.go.jp/keizai3/watcher-e/index-e.html).  
It is automatically updated by GitHub Actions as the economy watcher is updated.  
Dataset on HuggingFace: https://huggingface.co/datasets/retarfi/economy-watchers-survey  

日本語:  
[景気ウォッチャー調査](https://www5.cao.go.jp/keizai3/watcher/watcher_menu.html)のデータを自動更新・整形・抽出を行います。  
自動更新はGitHub Actionsによって月次で行われます。  
データセットはHuggingFaceからも利用可能です: https://huggingface.co/datasets/retarfi/economy-watchers-survey  

## Data Structure
English:  
The csv data of the economy watcher is stored as `data/2024/202401_watcher4.csv`.  
The `watcher4.csv` is a questionnaire about the current judgment of the economy and `watcher5.csv` is a questionnaire about the future judgment of the economy.  
The extracted data after filtering for current and future judgments in json format are stored as `data/current/202401.json` and `data/future/202401.json`, respectively.


日本語:  
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
poetry run python -m src.economy_watchers_survey.crawl.download
poetry run python -m src.economy_watchers_survey.create_json
```

## Format
```sh
poetry run black --check --diff --quiet --skip-magic-trailing-comma .
poetry run isort --check --diff --quiet .
```
