# twitter-news-scraper

## A web scraper for Tweeted news articles

### USAGE

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

    Example terminal output:
    ```

    Processing WSJ article 1 of 10...
    {
        [
            caption 1: Top trade officials, after meeting above in Buenos Aires in December, will convene again in Brussels on Saturday, a European official said. From left, Robert Lighthizer of the U.S., Japan's Hiroshige Seko and the EU’s Cecilia Malmstrom.
            credit 1: PHOTO: MARCOS BRINDICCI/REUTERS
        ]
    date: March 7, 2018 4:39 p.m. ET
    num_images: 1
    url: https://www.wsj.com/articles/u-s-japan-and-eu-trade-officials-to-meet-amid-steel-tariff-uproar-1520458765
    index: 992
    messages: []
    }

    Processing WSJ article 2 of 10...
    Going to twitter redirect... -> https://t.co/4ZVi4OkdBi
    {
        [
            caption 1: Univision CEO Randy Falco in New York in 2017.
            credit 1: PHOTO: EVAN VUCCI/ASSOCIATED PRESS
        ]
    date: Updated March 7, 2018 9:34 p.m. ET
    num_images: 1
    url: https://www.wsj.com/articles/univision-board-considers-replacing-ceo-randy-falco-1520467488
    index: 991
    messages: ['REDIRECTED']
    }
    ```

### NOTES & ASSUMPTIONS

* This program reads data from an input Excel workbook.
    By default the workbook is assumed to be formatted in the
    following manner:

    Index | Label | Tweet
    ------------ | ------------- | -------------
    990 | WSJ | Opinion: EU policy makers need to think carefully about what discretion the central bank should retain in a crisis https://t.co/nbtMGhLiNE
    991 | WSJ | Univision board is considering replacing its CEO and exploring cost cuts to prepare for a potential sale after scra‚Ä¶ https://t.co/bRr13ptgal
    ... | ... | ...

    Automating the collection of these Tweets from publication feeds into an Excel file is a WIP.

* For publications requiring a login, you will only need to log in the first time you run the program. After that your cookies will be pickled and saved locally and loaded in subsequent sessions.

    There is an automated login function included within Publication.py for the WSJ. For other publications Google reCAPTCHA makes automated login difficult, but there are methods to work around it (such as bottling and loading uBlock Origin into the webdriver.)



* Generally speaking, captions are formatted in 3 ways:
    1. With the caption/credit as children of a parent container
    and the caption/credit residing on the same depth. Example:

        ```
        PARENT_CONTAINER
        ↳ CHILD_CAPTION
        ↳ CHILD_CREDIT
        ```

    2. With the caption/credit formatted in a single text string.
        Examples:

        ```
        Some example caption (Some example credit)
        ```

        ```
        Some example caption \n Some example credit
        ```

        ```
        Some example caption PHOTO: Some example credit
        ```

        etc.

    3. With ALL caption/credit pairs residing underneath a single       parent. This is particularly common with galleries or slideshows. Example:
        ```
        PARENT_CONTAINER
        ↳ CHILD_CAPTION_1
        ↳ CHILD_CREDIT_1
        ↳ CHILD_CAPTION_2
        ↳ CHILD_CREDIT_2
        ↳ CHILD_CAPTION_3
        ↳ CHILD_CREDIT_3
        ...
        ```

    This program can efficiently extract captions of type 1 and 2 with the right keyword arguments and delimiter function.



    Extracting captions from galleries/slideshows is inconsistent depending on page structure and whether content is dynamically generated. This functionality is a WIP.
