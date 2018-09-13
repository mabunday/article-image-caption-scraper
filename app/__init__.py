"""
Header file that contains some useful utility functions.

"""

from urllib.parse import urlparse

import pandas as pd
from pandas import DataFrame


def get_domain(url: str) -> str:
    """Return domain of current_article."""
    return '{uri.netloc}'.format(uri=urlparse(url))


def read_csv(file_path: str) -> DataFrame:
    """Read csv file and return as Pandas DataFrame."""
    return pd.read_csv(file_path)


def extract_tweeted_urls(data: DataFrame) -> DataFrame:
    """Parse Tweets and return links as DataFrame."""
    return data['tweet'].str.extract('(https:\/\/t.co\/[a-zA-Z0-9]{10})')
