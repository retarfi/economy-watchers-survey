---
dataset_info:
- license: cc-by-4.0
- config_name: current
  features:
  - name: year-month
    dtype: string
  - name: 地域
    dtype: string
  - name: 関連
    dtype: string
  - name: 業種・職種
    dtype: string
  - name: 景気の現状判断
    dtype: string
  - name: 判断の理由
    dtype: string
  - name: 追加説明及び具体的状況の説明
    dtype: string
  splits:
  - name: train
    num_bytes: 81698032
    num_examples: 294757
  - name: test
    num_bytes: 9625470
    num_examples: 32585
  download_size: 0
  dataset_size: 91323502
- config_name: future
  features:
  - name: year-month
    dtype: string
  - name: 地域
    dtype: string
  - name: 関連
    dtype: string
  - name: 業種・職種
    dtype: string
  - name: 景気の先行き判断
    dtype: string
  - name: 景気の先行きに対する判断理由
    dtype: string
  splits:
  - name: train
    num_bytes: 77291445
    num_examples: 305257
  - name: test
    num_bytes: 9336368
    num_examples: 34915
  download_size: 0
  dataset_size: 86627813
---
# economy-watchers-survey
Auto uploader for Economy Watchers Survey data


## Information for GitHub
### Usage
```sh
poetry run python -m src.economy_watchers_survey.crawl.download
poetry run python -m src.economy_watchers_survey.create_datset.dataset
poetry run datasets-cli test economy-watchers-survey.py --save_info --all_configs
```

### Format
```sh
poetry run black --check --diff --quiet --skip-magic-trailing-comma .
poetry run isort --check --diff --quiet .
```
