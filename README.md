# twitter-news-scraper
[![made-with-python-3.7](https://img.shields.io/badge/Made%20with-Python%203.7-1CABE2.svg)](https://www.python.org/) ![version](https://img.shields.io/badge/version-1.2-brightgreen.svg)

## A dynamic web scraper for Tweeted news articles

#### v1.2 Changelog
* Updated to Python 3.7.0
* Refactored to use Dataclasses and Dataframes
* Now takes input Twitter data as CSV (handle, tweet)
* Now outputs scraped data as JSON 

#### Coming in v1.3
* More robust logging system 
* Automatic construction of data sets from Twitter feeds
* More analysis tools

### Requirements
1. Download ChromeDriver from [http://chromedriver.chromium.org/downloads](http://chromedriver.chromium.org/downloads)
2. Add path to driver in _scrape.py_
3. Install requirements `pip install -r requirements.txt`

### Usage
Run program with `python3 scrape.py`

### Example

_Scraping image captions from WSJ and WAPO articles_

##### Define Publication instances in _scrape.py_
```python
tweets = read_csv('../example_data.csv')
urls = extract_tweeted_urls(tweets)

# WALL STREET JOURNAL
wsj_urls = urls.loc[0:2]

# Captures image captions of the form
# PARENT_CONTAINER
# ↳ CAPTION
# ↳ CREDIT
wsj_kwargs = {
    'images': [{
        'parent_div': 'div.wsj-article-caption',
        'capt_span': 'span.wsj-article-caption-content',
        'cred_span': 'span.wsj-article-credit'}],
    'date': 'time.timestamp'
}

wsj = Publication('WSJ', cookies={}, kwargs=wsj_kwargs)
wsj.articles = driver.scrape_articles(wsj, wsj_urls)
wsj.write('output.json')  # write output data
print_stats(wsj)

# WASHINGTON POST
 wapo_urls = urls.loc[163:168]

# Captures image captions of the form
# "example caption (example credit)"
def wapo_delimiter(caption: str) -> List[str]:
    splits = caption.rsplit('(', 1)
    output_splits: List[str] = []
    for split in splits:
        if split != '':
            split = split[:-1] if split[-1] == ')' else split
        output_splits.append(split)
    return output_splits

wapo_kwargs = {
    'images': [{
        'parent_div': 'span.pb-caption',
        'delimiter': wapo_delimiter}],
    'date': 'span.pb-timestamp'
}

wapo = Publication('WAPO', cookies={}, kwargs=wapo_kwargs)
wapo.articles = driver.scrape_articles(wapo, wapo_urls)
wapo.write('output2.json')
```

##### Example Output
![carbon](carbon.png)