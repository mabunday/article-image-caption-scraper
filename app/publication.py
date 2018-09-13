import json
from dataclasses import dataclass
from typing import Dict, Optional, Union
from typing import List

from article import Article

Kwargs = Dict[str, Union[str, List[Dict[str, str]]]]


@dataclass
class Publication:
    """Publication dataclass."""
    name: str
    cookies: Optional[Dict[str, str]] = None
    logged_in: bool = False
    articles: Optional[List[Article]] = None
    kwargs: Optional[Kwargs] = None

    def append(self, article: Article) -> None:
        """Append method."""
        if not self.articles:
            self.articles = []
        self.articles.append(article)

    def write(self, file_path: str, mode: str = 'w', indent: int = 4) -> None:
        articles = [a.asdict() for a in self.articles]
        with open(file_path, mode) as f:
            f.write(json.dumps(articles, indent=indent))
