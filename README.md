# twitter-news-scraper
[![made-with-python-3.7](https://img.shields.io/badge/Made%20with-Python%203.7-1CABE2.svg)](https://www.python.org/) ![version](https://img.shields.io/badge/version-1.2-brightgreen.svg)

## A web scraper for Tweeted news articles

### v1.2 Changelog
* Updated to Python 3.7.0
* Refactored to use Dataclasses and Dataframes
* Now takes input Twitter data as CSV (handle, tweet)
* Now outputs scraped data as JSON 

### Requirements
1. Download ChromeDriver from [http://chromedriver.chromium.org/downloads](http://chromedriver.chromium.org/downloads)
2. Add path to driver in _scrape.py_
3. Install requirements `pip install -r requirements.txt`

### Usage
Run program with `python3 scrape.py`

### Examples

Scraping image captions from WSJ and WAPO articles 

##### Define Publication instances in _scrape.py_
```python
tweets = read_csv('../example_data.csv')

# WALL STREET JOURNAL
wsj_urls = extract_tweeted_urls(tweets).loc[0:2]

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
 wapo_urls = extract_tweeted_urls(tweets).loc[163:168]

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

##### Program Output
```json
Processing WSJ article 1/3...
Press Enter to begin after you have logged in...
{
    "url": "https://www.wsj.com/articles/johnson-johnson-says-discounts-cut-the-prices-for-its-drugs-though-revenue-rose-1520551413",
    "body": "",
    "date": "March 8, 2018 6:23 p.m. ET",
    "num_images": 1,
    "images": [
        {
            "caption": "Joaquin Duato, who heads J&J\u2019s pharmaceuticals business, is seen at a panel discussion in Washington in September.",
            "credit": "PHOTO: BLOOMBERG NEWS"
        }
    ]
}
Processing WSJ article 2/3...
{
    "url": "https://www.wsj.com/articles/wynn-resorts-to-pay-universal-entertainment-to-settle-litigation-1520551385",
    "body": "",
    "date": "Updated March 8, 2018 10:34 p.m. ET",
    "num_images": 2,
    "images": [
        {
            "caption": "Steve Wynn, the former CEO of Wynn Resorts, show in May 2017.",
            "credit": "PHOTO: MIKE BLAKE/REUTERS"
        },
        {
            "caption": "",
            "credit": ""
        }
    ]
}

...

Processing WAPO article 3/6...
{
    "url": "https://www.washingtonpost.com/news/capital-weather-gang/wp/2018/03/08/the-chance-of-a-major-winter-storm-in-washington-sunday-and-monday-has-markedly-decreased/",
    "body": "",
    "date": "March 8",
    "num_images": 5,
    "images": [
        {
            "caption": "European model shows storm well southeast of Washington on Monday morning, far enough for the storm to completely miss.",
            "credit": ""
        },
        {
            "caption": "The NAM model shows precipitation from the Sunday-Monday Mid-Atlantic storm remaining south and southeast of Washington.",
            "credit": ""
        },
        {
            "caption": "American (GFS) model shows the D.C. area on the northern edge of snow from a coastal storm Monday morning. ",
            "credit": "WeatherBell.com"
        },
        {
            "caption": "Snowfall forecasts from the group of simulations in the American (GEFS) modeling system. Note that these accumulations assume 10 inches of snow would fall for every inch of rain, whereas it would, in reality, be less given the wet nature of snow that falls. ",
            "credit": "WeatherBell.com"
        },
        {
            "caption": "The UKMet forecast created Wednesday for Monday in the Mid-Atlantic showed a big storm coming up the East Coast. Thursday\u2019s forecast has a much weaker storm headed out to sea. ",
            "credit": "Meteocentre.com"
        }
    ]
}
...
```
