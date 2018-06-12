import os
import pickle
from typing import List, Dict

from selenium.common.exceptions import TimeoutException

from article import Article
from publication import Publication
from utility import write_output, print_article, get_workbook_urls, get_domain

__VALID_DOMAINS = ["www.washingtonpost.com",
                   "www.wsj.com",
                   "blogs.wsj.com",
                   "twitter.com",
                   "www.nytimes.com",
                   "cooking.nytimes.com",
                   "nypost.com",
                   "www.houstonchronicle.com",
                   "www.chron.com",
                   "www.chicagotribune.com",
                   "www.startribune.com",
                   "www.bostonglobe.com",
                   "www.denverpost.com",
                   "theknow.denverpost.com",
                   "www.philly.com",
                   "www.seattletimes.com",
                   "www.nydailynews.com",
                   "www.amny.com",
                   "www.latimes.com",
                   "www.newsday.com",
                   "www.nj.com",
                   "www.tampabay.com",
                   "www.usatoday.com",
                   "www.azcentral.com",
                   "sportsday.dallasnews.com",
                   "www.dallasnews.com"
                   ]


def main():
    """Execute scraping."""

    def scrape_articles(publication: Publication,
                        input_urls: List[str],
                        kwargs_list: List[Dict[str, str]],
                        date: str,
                        start_index: int = 0,
                        ) -> List[Article]:
        """
        Scrape Publication articles according to kwargs and return
        list of articles with desired information.

        Parameters
        ----------
        publication : Publication
            Input publication to scrape.
        input_urls : List[str]
            List of publication urls.
        kwargs_list : List[Dict[str, str]]
            List of keyword arguments that specify which article
            elements to extract.
        date : str
            Element containing article date string.
        start_index : int
            Index corresponding to the sheet index from which the
            article url was extracted. Should match value of
            row_start from get_workbook_urls.

        Returns
        -------
        out : List[Article]
            List of articles with scraped information.

        Examples
        --------
        wsj = Publication(name='WSJ')

        wsj_args = [
                        {
                        'parent_div': 'div.wsj-article-caption',
                        'caption_span': 'span.wsj-article-caption-content',
                        'credit_span': 'span.wsj-article-credit'
                        }
                   ]

        wsj_inp_urls = get_workbook_urls(workbook='articles.xlsx',
                                         row_start=990,
                                         row_end=1000
                                         )
        scrape_articles(publication=wsj,
                        input_urls=wsj_inp_urls,
                        kwargs_list=wsj_args,
                        date='time.timestamp',
                        start_index=990,
                        )

        write_output(publication=wsj, output_workbook='output_test_3.xlsx')
        """
        urls = input_urls
        for url_index, url in enumerate(urls):
            print("Processing {} article {} of {}...".
                  format(publication.name, url_index, len(urls))
                  )
            messages = []
            sheet_index = url_index + start_index - 1
            if url == "NO_URL":
                article = Article(index=sheet_index,
                                  messages=["INVALID_URL"]
                                  )
                publication.append(article)
                print_article(article)
                continue
            if url == "INVALID_URL":
                article = Article(index=sheet_index,
                                  messages=["INVALID_URL"]
                                  )
                publication.append(article)
                print_article(article)
                continue
            try:
                publication.url = url
            except TimeoutException:
                messages.append("GET_TIMED_OUT")
                article = Article(url=url,
                                  index=sheet_index,
                                  messages=messages
                                  )
                publication.append(article)
                print_article(article)
                continue

            domain = get_domain(publication.url)
            # Redirects if link incorrectly goes to Tweet instead of article
            if domain == 'twitter.com':
                tweet = publication.driver.title
                link_index = tweet.find("https://t.co/")
                if link_index == -1:
                    messages.append("INVALID_REDIRECT")
                    article = Article(url=url,
                                      index=sheet_index,
                                      messages=messages
                                      )
                    publication.append(article)
                    print_article(article)
                    continue

                redirect_url = tweet[link_index:link_index+23]
                print("Going to twitter redirect... -> {}".format(redirect_url))
                messages.append("REDIRECTED")
                try:
                    publication.url = redirect_url
                    domain = get_domain(publication.url)
                except TimeoutException:
                    messages.append("GET_TIMED_OUT")
                    article = Article(url=url,
                                      index=sheet_index,
                                      messages=messages
                                      )
                    publication.append(article)
                    print_article(article)
                    continue

            if domain not in __VALID_DOMAINS:
                print("INVALID_DOMAIN: Skipping {}".format(domain))
                messages.append("INVALID_DOMAIN")
                article = Article(url=url,
                                  index=sheet_index,
                                  messages=messages
                                  )
                publication.append(article)
                print_article(article)
                continue

            if os.path.isfile("cookies.pkl"):
                cookies = pickle.load(open("cookies.pkl", "rb"))
                for cookie in cookies:
                    publication.driver.add_cookie(cookie)

            if not publication.logged_in:
                input("Press Enter to begin after you have logged in...")
                publication.logged_in = True
            pickle.dump(publication.driver.get_cookies(),
                        open("cookies.pkl", "w+b"))

            if not publication.wait_for_js_and_jquery():
                messages.append("JS_TIMED_OUT")

            def get_images_helper(kwargs: List[Dict[str, str]]) -> List[Dict[str, str]]:
                images = []
                for kwarg in kwargs:
                    images += publication.get_images(**kwarg)
                return images

            article = publication.get_article(images=get_images_helper(kwargs_list),
                                              date=date,
                                              index=sheet_index,
                                              messages=messages
                                              )
            publication.append(article)
            print_article(article)

        publication.quit()
        return publication.articles

    '''
    Examples:
    Note: Uncommented Publication instances may not work and
          may require tweaking of parameters.
    '''

    """WALL STREET JOURNAL"""
    #'''

    wsj = Publication(name='WSJ')

    wsj_args = [
                    {
                    'parent_div': 'div.wsj-article-caption',
                    'caption_span': 'span.wsj-article-caption-content',
                    'credit_span': 'span.wsj-article-credit'
                    }
               ]

    wsj_inp_urls = get_workbook_urls(workbook='articles.xlsx',
                                     row_start=990,
                                     row_end=1000
                                     )
    scrape_articles(publication=wsj,
                    input_urls=wsj_inp_urls,
                    kwargs_list=wsj_args,
                    date='time.timestamp',
                    start_index=990,
                    )

    write_output(publication=wsj, output_workbook='output_test_3.xlsx')
    #'''

    """STAR TRIBUNE"""
    '''
    args_st = [
                {
                    'parent_div': 'div.article-featured-media-wrapper.is-photo',
                    'caption_span': "figcaption[class*='tease-photo-caption']",
                    'credit_span': 'figcaption[class*="author"]'
                },
                {
                    'parent_div': 'div.related-media',
                    'caption_span': 'div.related-caption',
                    'credit_span': 'div.related-byline'
                },
                {
                    'parent_div': 'div.photo'
                }
              ]

    st = Publication(name="Star Tribune")

    st_inp_urls = get_workbook_urls(workbook='articles.xlsx',
                                    row_start=1200,
                                    row_end=1219
                                    )

    scrape_articles(publication=st,
                    kwargs_list=args_st,
                    input_urls=st_inp_urls,
                    date='div.article-dateline',
                    start_index=1200
                    )
    write_output(publication=st, output_workbook='output_test_3.xlsx')
    '''
    # 1157, 1219

    """BOSTON GLOBE"""
    '''
    def bg_delimiter(inp_str):
        splits = inp_str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    args_bg = [
                {
                    'parent_div': 'figcaption.lead-media__info',
                    'caption_span': 'div.lead-media__caption',
                    'credit_span': 'div.lead-media__credit'
                },
                {
                    'parent_div': 'figcaption.inline-media__info',
                    'caption_span': 'div.lead-inline__caption',
                    'credit_span': 'div.lead-inline__credit'
                },
                {
                    'parent_div': 'div.gcaption.geor',
                    'delimiter': bg_delimiter,
                }
              ]

    bg = Publication(name="Boston Globe")
    scrape_articles(publication=bg,
                    args=args_bg,
                    date_div='time.article-header__pubdate',
                    start_index=1342,
                    end_index=1493,
                    )
    write_output(publication=bg, output_workbook='output_test.xlsx')
    '''

    """CHICAGO TRIBUNE"""
    '''
    def chi_trib_str(str):
        splits = str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    args_chi_trib = [
                        {
                            'parent_div': 'div.trb_em_r_cc',
                            'delimiter': chi_trib_str
                        }
                    ]

    chi_trib = Publication(name="Chicago Tribune")
    scrape_articles(publication=chi_trib,
                    args=args_chi_trib,
                    date_div='time.trb_ar_dateline_time',
                    start_index=1493,
                    end_index=1570)
    write_output(publication=chi_trib, output_workbook='output_test.xlsx')
    '''

    """DENVER POST"""
    '''
    def denv_post_delim(inp_str):
        try:
            credit = denv_post.driver.find_element_by_css_selector('div.photo-credit').text
        except NoSuchElementException as e:
            credit = "NO_CREDIT"
        caption = inp_str.replace(credit, "")
        return [caption, credit]

    denv_post_args = [
        {
            'parent_div': 'figcaption',
            'delimiter': denv_post_delim
        }
    ]

    denv_post = Publication(name="Denver Post")
    scrape_articles(publication=denv_post,
                    kwargs_list=denv_post_args,
                    date='time',
                    start_index=218,
                    end_index=271)
    write_output(publication=denv_post, output_workbook='output_test.xlsx')
    '''

    """PHILLY INQUIRER"""
    '''
    philly_inq_kwargs = [
        {
            'parent_div': 'div.unify__caption-credit',
            'caption_span': 'span.caption',
            'credit_span': 'a.credit.upper'
        },
        {
            'parent_div': 'figcaption[class*="wp-caption"]',
            'caption_span': 'div[class*="caption"]',
            'credit_span': 'span[class*="credit"]'
        },
    ]

    philly_inq = Publication(name="Philly Inquirer")
    scrape_articles(publication=philly_inq,
                    kwargs_list=philly_inq_kwargs,
                    date='time.date',
                    start_index=271,
                    end_index=323)
    write_output(publication=philly_inq, output_workbook='output_test.xlsx')
    '''

    """SEATTLE TIMES"""
    '''
    def seattle_times_delimiter(inp_str):
        splits = inp_str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    seattle_times_kwargs = [
                {
                    'parent_div': 'span.caption-full',
                    'delimiter': seattle_times_delimiter,
                },
                {
                    'parent_div': 'span.slide-caption',
                    'delimiter': seattle_times_delimiter,
                },
                {
                    'parent_div': 'figcaption.article-figure-caption',
                    'delimiter': seattle_times_delimiter,
                }
              ]

    seattle_times = Publication(name="Seattle Times")
    scrape_articles(publication=seattle_times,
                    kwargs_list=seattle_times_kwargs,
                    date='time.line.published',
                    start_index=323,
                    end_index=411,
                    )
    write_output(publication=seattle_times, output_workbook='output_test.xlsx')
    '''

    """NY DAILY NEWS"""
    '''
    def ny_daily_news_delimiter(inp_str):
        splits = inp_str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    ny_daily_news_kwargs = [
        {
            'parent_div': 'figcaption.caption-text.spaced.spaced-top.spaced-sm.flex-container-row.justify-space-between',
            'delimiter': ny_daily_news_delimiter,
        }
    ]


    ny_daily_news = Publication(name="NY Daily News")
    scrape_articles(publication=ny_daily_news,
                    kwargs_list=ny_daily_news_kwargs,
                    date='span.timestamp',
                    start_index=205,
                    end_index=218,
                    )
    write_output(publication=ny_daily_news, output_workbook='output_test.xlsx')
    '''

    """AM NEW YORK"""
    '''
    def am_ny_delimiter(inp_str):
        splits = inp_str.rsplit('Photo Credit: ', 1)
        output_splits = []
        for split in splits:
            split.strip()
            output_splits.append(split)
        return output_splits

    am_ny_kwargs = [
        {
            'parent_div': 'p.caption',
            'delimiter': am_ny_delimiter,
        },
        {
            'parent_div': 'figcaption.caption',
            'delimiter': am_ny_delimiter,
        }
    ]

    am_ny_news = Publication(name="AM New York")
    scrape_articles(publication=am_ny_news,
                    kwargs_list=am_ny_kwargs,
                    date='time[itemprop="datePublished"]',
                    start_index=2,
                    end_index=29,
                    )
    write_output(publication=am_ny_news, output_workbook='output_test.xlsx')
    '''

    """LA TIMES"""
    '''
    def la_times_delimiter(inp_str):
        splits = inp_str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    la_times_kwargs = [
        {
            'parent_div': 'figcaption.caption-text.spaced.spaced-top.spaced-sm.flex-container-row.justify-space-between',
            'delimiter': la_times_delimiter,
        }
    ]

    la_times = Publication(name="LA Times")
    scrape_articles(publication=la_times,
                    kwargs_list=la_times_kwargs,
                    date='span.timestamp',
                    start_index=29,
                    end_index=105,
                    )
    write_output(publication=la_times, output_workbook='output_test.xlsx')
    '''

    """NEWSDAY"""
    '''
    def newsday_delimiter(inp_str):
        splits = inp_str.rsplit('Photo Credit: ', 1)
        output_splits = []
        for split in splits:
            split.strip()
            output_splits.append(split)
        return output_splits

    newsday_kwargs = [
        {
            'parent_div': 'p.caption',
            'delimiter': newsday_delimiter,
        },
        {
            'parent_div': 'figcaption.caption',
            'delimiter': newsday_delimiter,
        }
    ]

    newsday = Publication(name="Newsday")
    scrape_articles(publication=newsday,
                    kwargs_list=newsday_kwargs,
                    date='time[itemprop="datePublished"]',
                    start_index=105,
                    end_index=131,
                    )
    write_output(publication=newsday, output_workbook='output_test.xlsx')
    '''

    """STARLEDGER"""
    '''
    def starledger_delimiter(inp_str):
        splits = inp_str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    starledger_kwargs = [
        {
            'parent_div': 'figcaption[class*="__caption"]',
            'delimiter': starledger_delimiter,
        }
    ]

    starledger = Publication(name="Starledger")
    scrape_articles(publication=starledger,
                    kwargs_list=starledger_kwargs,
                    date='time',
                    start_index=411,
                    end_index=415,
                    )
    write_output(publication=starledger, output_workbook='output_test.xlsx')
    '''

    """TAMPA TIMES"""
    '''
    def tampa_times_delimiter(inp_str):
        splits = inp_str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    def tampa_times_delimiter_2(inp_str):
        splits = inp_str.rsplit('[', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ']' else split
            output_splits.append(split)
        return output_splits

    tampa_times_kwargs = [
        {
            'parent_div': 'span.caption.credit',
            'delimiter': tampa_times_delimiter,
        },
        {
            'parent_div': 'figcaption.caption',
            'delimiter': tampa_times_delimiter,
        },
        {
            'parent_div': 'div.blog-photo-caption',
            'delimiter': tampa_times_delimiter_2,
        }
    ]

    tampa_times = Publication(name="Tampa Times")
    scrape_articles(publication=tampa_times,
                    kwargs_list=tampa_times_kwargs,
                    date='div.story-byline-published',
                    start_index=415,
                    end_index=570,
                    )
    write_output(publication=tampa_times, output_workbook='output_test.xlsx')
    '''

    """USA TODAY & AZ Central"""
    '''
    def usa_today_delimiter(inp_str):
        splits = inp_str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    usa_today_kwargs = [
        {
            'parent_div': 'p.image-credit-wrap',
            'delimiter': usa_today_delimiter
        }
    ]
    
    usa_today = Publication(name="USA Today")
    scrape_articles(publication=usa_today,
                    kwargs_list=usa_today_kwargs,
                    date='span.asset-metabar-time',
                    start_index=570,
                    end_index=708,
                    )
    write_output(publication=usa_today, output_workbook='output_test.xlsx')
    
    az_central = Publication(name="AZ Central")
    scrape_articles(publication=az_central,
                    kwargs_list=usa_today_kwargs,
                    date='span.asset-metabar-time',
                    start_index=1000,
                    end_index=1157,
                    )
    write_output(publication=az_central, output_workbook='output_test.xlsx')
    '''

    """DALLAS NEWS"""
    '''
    def dallas_news_delimiter(inp_str):
        splits = inp_str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    dallas_news_kwargs = [
        {
            'parent_div': 'figcaption[class*="image__figcaption"]',
            'caption_span': 'div[class*="__caption"]',
            'credit_span': 'div[class*="__credit"]'
        },
        {
            'parent_div': 'figcaption[class*="__figure__figcaption"]',
            'caption_span': 'p.mtm',
            'credit_span': 'p[class*="__attribution"]'
        },
    ]

    dallas_news = Publication(name="Dallas News")
    scrape_articles(publication=dallas_news,
                    kwargs_list=dallas_news_kwargs,
                    date='time',
                    start_index=1570,
                    end_index=1691,
                    )
    write_output(publication=dallas_news, output_workbook='output_test.xlsx')
    '''

    """NY POST"""
    '''
    def ny_post_delimiter(inp_str):
        splits = inp_str.rsplit('\n', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split.strip()
            output_splits.append(split)
        return output_splits

    ny_post_kwargs = [
        {
            'parent_div': '[class*="wp-caption-text"]',
            'delimiter': ny_post_delimiter
        }
    ]

    ny_post = Publication(name="NY Post")
    scrape_articles(publication=ny_post,
                    kwargs_list=ny_post_kwargs,
                    date='p.byline-date',
                    start_index=1811,
                    end_index=2033,
                    )
    write_output(publication=ny_post, output_workbook='output_test.xlsx')
    '''

    """HOUSTON CHRON"""
    '''
    def houston_chron_delim(inp_str):
        try:
            credit = houston_chron.driver.find_element_by_css_selector('span.credit').text
        except NoSuchElementException as e:
            credit = "NO_CREDIT"
        caption = inp_str
        return [caption, credit]

    houston_chron_kwargs = [
        {
            'parent_div': 'div.caption',
            'delimiter': houston_chron_delim
        }
    ]

    houston_chron = Publication(name="Houston Chronicle")
    scrape_articles(publication=houston_chron,
                    kwargs_list=houston_chron_kwargs,
                    date='h5.timestamp',
                    start_index=1691,
                    end_index=1811,
                    )
    write_output(publication=houston_chron, output_workbook='output_test.xlsx')
    '''

    """WASHINGTON POST"""
    '''
    def wapo_str(str):
        splits = str.rsplit('(', 1)
        output_splits = []
        for split in splits:
            if split != '':
                split = split[:-1] if split[-1] == ')' else split
            output_splits.append(split)
        return output_splits

    wapo = Publication('Washington Post')
    scrape_articles(publication=wapo,
                    start_index=708,
                    end_index=860,
                    parent_div='span.pb-caption',
                    delimiter=wapo_str,
                    date_div='span.pb-timestamp')
    write_output(publication=wapo, output_workbook='output_test.xlsx')
    '''

    """NEW YORK TIMES"""
    '''
    def nyt_str(str):
        return str.rsplit("\nCredit\n", 1)



    nyt = Publication()
    scrape_articles(nyt, 1219, 1342, "figcaption[itemprop='caption description']", None, None, nyt_str, "time")
    write_output(nyt, 'output_test.xlsx', 'Sheet1', 'NYTimes')
    '''


if __name__ == "__main__":
    main()
