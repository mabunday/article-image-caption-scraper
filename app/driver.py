"""
Module for scraping publications.

"""

from typing import Any, Callable, Dict, List, Optional

from pandas import DataFrame
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from utils import extract_tweeted_urls, get_domain, read_csv
from article import Article
from domain_list import VALID_DOMAINS
from image import Image, delim_image, get_image
from publication import Kwargs, Publication
from stats import print_stats


class CustomDriver(webdriver.Chrome):
    """Driver class. Extends webdriver.Chrome."""

    def __init__(self, driver_path: str,
                 implicit_wait: int = 1,
                 messages: Optional[List[str]] = None) -> None:
        webdriver.Chrome.__init__(self, driver_path, chrome_options=Options())
        self.implicitly_wait(implicit_wait)
        if messages is None:
            self.messages = []
        else:
            self.messages = messages

    def _log_messages(self, msg: str) -> None:
        print(msg)
        self.messages.append(msg)

    def _get_article(self,
                     kwargs: Kwargs,
                     article_cache: Dict[str, Article] = None) -> Article:
        """

        :param kwargs:
        :param article_cache:
        :return:
        """

        if article_cache is None:
            article_cache = {}

        article_url = self.current_url
        # Strip unnecessary headers for memoization
        try:
            stripped_url = article_url[:article_url.index('?')]
        except ValueError:
            stripped_url = article_url

        # If article is cached
        if stripped_url in article_cache:
            self._log_messages('Memoized previously processed article')
            cached_article = article_cache[stripped_url]
            article = Article(**cached_article.asdict())
        else:
            date = self._get_date(kwargs['date']) if 'date' in kwargs else ''

            images: List[Image] = []
            for kwarg in kwargs['images']:
                images += self._get_images(**kwarg)

            article = Article(stripped_url,
                              date=date,
                              num_images=len(images),
                              images=images)

            # Cache article
            article_cache[stripped_url] = article
        return article

    def _get_date(self, date: str) -> str:
        """

        :param date:
        :return:
        """
        try:
            article_date = str(self.find_element_by_css_selector(date).text)
        except NoSuchElementException:
            article_date = ''
        return article_date

    def _wait_for_js_and_jquery(self, timeout: int = 5) -> Any:
        """

        :param timeout:
        :return:
        """

        wait = WebDriverWait(self, timeout)

        def _jquery_load() -> Any:
            try:
                return lambda x: x.execute_script(
                    "return window.jQuery != undefined && jQuery.active === 0")
            # Page does not have jQuery
            except Exception:
                return True

        def _js_load() -> Any:
            return lambda x: x.execute_script('return document.readyState')

        try:
            return wait.until(_jquery_load()) and wait.until(_js_load())
        except TimeoutException:
            return False

    def _log_in(self, pub: Publication) -> None:
        """

        :param pub:
        :return:
        """

        if not pub.logged_in:
            if isinstance(pub.cookies, dict):
                if pub.name in pub.cookies:
                    self._log_messages(
                        'Loading saved {} cookies'.format(pub.name))
                    for cookie in pub.cookies[pub.name]:
                        self.add_cookie(cookie)
                    pub.logged_in = True

                else:
                    input('Press Enter to begin after you have logged in...')
                    pub.cookies[pub.name] = self.get_cookies()
                    pub.logged_in = True

    def _get_images(
            self,
            parent_div: str,
            caption_span: Optional[str] = None,
            credit_span: Optional[str] = None,
            delimiter: Optional[Callable[[str], List[str]]] = None
    ) -> List[Image]:
        """

        :param parent_div:
        :param caption_span:
        :param credit_span:
        :param delimiter:
        :return:
        """

        images = []

        try:
            elements = self.find_elements_by_css_selector(parent_div)
            for element in elements:
                if isinstance(caption_span, str) and isinstance(credit_span, str):
                    image = get_image(element, caption_span, credit_span)
                elif (caption_span is None and credit_span is None
                      and delimiter is not None):
                    image = delim_image(element.text, delimiter)
                else:
                    break
                images.append(image)
            return images
        except NoSuchElementException:
            return images

    def scrape_articles(self,
                        publication: Publication,
                        data: DataFrame) -> List[Article]:
        """
        Scrape articles.

        :param publication
        :param data:
        :return:
        """
        # TODO: we should use some kind of logger

        articles = []

        for index, url in data.itertuples():

            self._log_messages('Processing {} article {}/{}...'.format(
                publication.name, index + 1, data.size))

            # if url is NaN
            if isinstance(url, float):
                self._log_messages('No URL for row '.format(index))
                continue

            try:
                self.get(url)
            except TimeoutException:
                self._log_messages('{} timed out'.format(url))
                continue

            current_domain = get_domain(self.current_url)
            # Redirects if link incorrectly goes to another
            # Tweet instead of article
            if current_domain == 'twitter.com':
                tweet_body = self.title
                url_index = tweet_body.find("https://t.co/")

                # If no link in Tweet
                if url_index == -1:
                    self._log_messages(
                        'No redirect in {}'.format(self.current_url))
                    continue

                redirect_url = tweet_body[url_index:url_index + 23]
                if not redirect_url[-10:].isalnum():
                    self._log_messages(
                        'invalid redirect {}'.format(redirect_url))
                    continue

                self._log_messages(
                    'Redirected to {}'.format(redirect_url))

                try:
                    self.get(redirect_url)
                    current_domain = get_domain(self.current_url)
                except TimeoutException:
                    self._log_messages('Twitter redirect timed out')
                    continue

            if current_domain not in VALID_DOMAINS:
                self._log_messages(
                    'Skipping invalid domain {}'.format(current_domain))
                continue

            self._log_in(publication)

            if not self._wait_for_js_and_jquery():
                self._log_messages('Javascript timed out')

            article = self._get_article(publication.kwargs)
            articles.append(article)
            article.print()
        return articles


def main() -> None:
    """
    Main method.

    :return:
    """

    # Fill in path here
    print('PATH TO CHROMEDRIVER NEEDS BE ADDED IN MAIN METHOD')
    _driver_path = ''
    driver = CustomDriver(_driver_path)

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
            'caption_span': 'span.wsj-article-caption-content',
            'credit_span': 'span.wsj-article-credit'}],
        'date': 'time.timestamp'
    }

    wsj = Publication('WSJ', cookies={}, kwargs=wsj_kwargs)
    wsj.articles = driver.scrape_articles(wsj, wsj_urls)
    # wsj.write('output.json')  # write output data
    # print_stats(wsj)

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
    # wapo.articles = driver.scrape_articles(wapo, wapo_urls)
    # wapo.write('output2.json')

    driver.quit()

    # TODO: add stats about collected data


if __name__ == "__main__":
    main()
