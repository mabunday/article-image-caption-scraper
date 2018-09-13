import pandas as pd

from publication import Publication


def print_stats(publication: Publication) -> None:

    avg_images = pd.Series(
        [article.num_images for article in publication.articles])

    print(avg_images.describe())
