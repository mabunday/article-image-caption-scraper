import dataclasses
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from image import Image


@dataclass(frozen=True)
class Article:
    """Article dataclass."""
    url: str
    body: str = ''
    date: str = ''
    num_images: int = 0
    images: Optional[List[Image]] = None

    def asdict(self) -> Dict[str, Union[str, int, List[Image], None]]:
        """Convert Article dataclass to dictionary."""
        return dataclasses.asdict(self)

    def json(self, indent: int = 4) -> str:
        return json.dumps(self.asdict(), indent=indent)

    def print(self) -> None:
        print(self.json())