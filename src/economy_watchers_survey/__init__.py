from pathlib import Path

from .version import __version__

DATA_DIR: Path = Path(__file__).parents[2] / "data"
