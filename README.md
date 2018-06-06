# publication-twitter-scraper

## A web scraper for news articles linked from Tweets

USAGE:

1. Get ChromeDriver from:
    [http://chromedriver.chromium.org/downloads](http://chromedriver.chromium.org/downloads)
2. Add path to driver in publication.py
3. Install requirements with:

    ```pip install -r requirements.txt```
4. Edit scrape.py main with Publication instances. Example: 
    ```python
    wsj = Publication(name='WSJ')

    wsj_args = [
                    {'parent_div': 'div.wsj-article-caption',
                     'caption_span': 'span.wsj-article-caption-content',
                     'credit_span': 'span.wsj-article-credit'
                     }
                ]

    wsj_inp_urls = get_workbook_urls(workbook='input_tweets.xlsx',
                                     row_start=990,
                                     row_end=1000
                                     )

    scrape_articles(publication=wsj,
                    input_urls=wsj_inp_urls,
                    kwargs_list=wsj_args,
                    date='time.timestamp',
                    start_index=990,
                    )

    write_output(publication=wsj,
                 output_workbook='output_articles.xlsx'
                 )
    ```
5. Run with 
    ```python
    python3 scrape.py
    ```