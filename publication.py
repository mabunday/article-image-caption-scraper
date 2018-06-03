from typing import Callable, List, Dict

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from article import *


class Publication:
    """Create class for each Publication."""
    def __init__(self,
                 name: str = "",
                 implicit_wait: int = 1,
                 logged_in: bool = False
                 ):
        """
        Publication constructor.

        Parameters
        ----------
        name : str
            The name of the publication. Defaults to "".
        implicit_wait : int
            Implicit wait value of publication web driver. Defaults to 1.
        logged_in : bool
            Boolean for publication login status. Defaults to False.

        """
        self.__name = name
        self.__logged_in = logged_in
        self.__chrome_options = Options()
        # ADD PATH TO DRIVER HERE
        self.__driver = webdriver.Chrome(
            "/YOUR_PATH_TO/chromedriver", chrome_options=self.__chrome_options)
        self.__driver.implicitly_wait(implicit_wait)
        self.__articles = []
        # self.__input_urls = []
        # self.__kwargs = []

    @property
    def driver(self) -> webdriver:
        return self.__driver

    '''
    @property
    def kwargs(self) -> List[Dict[str, str]]:
        return self.__kwargs

    @kwargs.setter
    def kwargs(self, kwargs: List[Dict[str, str]]):
        self.__kwargs = kwargs


    @property
    def input_urls(self) -> List[str]:
        return self.__input_urls

    @input_urls.setter
    def input_urls(self, input_urls: List[str]):
        self.__input_urls = input_urls
    '''

    @property
    def name(self) -> str:
        return self.__name

    def quit(self):
        print("Closing %s driver..." % self.__name)
        self.__driver.quit()

    @property
    def articles(self) -> List[Article]:
        return self.__articles

    @articles.setter
    def articles(self, name: List[Article]):
        self.__articles = name

    def append(self, article):
        self.__articles.append(article)

    @property
    def logged_in(self) -> bool:
        return self.__logged_in

    @logged_in.setter
    def logged_in(self, value: bool):
        self.__logged_in = value

    @property
    def url(self) -> str:
        return self.__driver.current_url

    @url.setter
    def url(self, url: str):
        self.__driver.get(url)

    def compare_urls(self, url: str, timeout: int = 10) -> bool:
        """
        Compare current driver URL to input url for 10 seconds.

        Parameters
        ----------
        url : str
            URL to compare current URL to.
        timeout : int
            How long to do comparison. Defaults to 10 seconds.

        Return
        ------
        out : bool
            Returns whether the URLs are equal or not.

        """
        wait = WebDriverWait(self.__driver, timeout)
        return wait.until(
            lambda driver: self.__driver.current_url == url)

    def wait_for_js_and_jquery(self, timeout: int = 5) -> bool:
        """
        Wait for JavaScript and JQuery to finish loading.

        Parameters
        ----------
        timeout : int
            How long to wait for JavaScript and JQuery to load.
            Defaults to 5.

        Return
        ------
        out : bool
            True if finished loading, else False.

        """

        wait = WebDriverWait(self.__driver, timeout)

        def jquery_load():
            try:
                return lambda driver: driver.execute_script(
                    "return window.jQuery != undefined && jQuery.active === 0")
            # Page does not have jQuery
            except Exception:
                return True

        def js_load():
            return lambda driver: driver.execute_script(
                'return document.readyState')
        try:
            return wait.until(jquery_load()) and wait.until(js_load())
        except TimeoutException:
            return False

    def log_into_wsj(self):
        """Log into the WSJ."""
        article_url = self.__driver.current_url
        self.__driver.get(
            "https://accounts.wsj.com/login?target=" + article_url)
        try:
            self.__driver.find_element_by_id("username").send_keys('your_username')
            self.__driver.find_element_by_id("password").send_keys('your_password')
            login_ready = self.__driver.find_element_by_class_name("basic-login-submit")
            login_ready.submit()
            self.logged_in = True
            return self.compare_urls(article_url)
        except NoSuchElementException:
            print("COULD NOT LOG IN\n")

    @staticmethod
    def get_caption_and_credit(element: WebElement,
                               caption: str,
                               credit: str
                               ) -> Dict[str, str]:
        """
        Extract caption and credit from web element and return them
        as a dictionary pair.

        If no caption/credit can be found "NO_CAPTION"/"NO_CREDIT"
        are returned, respectively.

        Parameters
        ----------
        element : WebElement
            The parent WebElement to the child credit/caption elements.
        caption : str
            The css selector of the caption.
        credit : str
            The css selector of the credit.

        Returns
        -------
        out : Dict[str, str]
            Dictionary containing caption/credit.

        """
        try:
            caption = element.find_element_by_css_selector(caption).text
        except NoSuchElementException:
            caption = "NO_CAPTION"
        try:
            credit = element.find_element_by_css_selector(credit).text
        except NoSuchElementException:
            credit = "NO_CREDIT"
        if caption.strip() == "":
            caption = "NO_CAPTION"
        if credit.strip() == "":
            credit = "NO_CREDIT"
        return {
            'caption': caption,
            'credit': credit
        }

    @staticmethod
    def delim_caption(inp_str: str,
                      delimiter: Optional[Callable[[str], List[str]]]
                      ) -> Dict[str, str]:
        """
        Delimit combined caption and credit string and return individually
        as a dictionary pair.

        If no caption/credit can be found "NO_CAPTION"/"NO_CREDIT"
        are returned, respectively.

        Parameters
        ----------
        inp_str : str
            The combined caption/credit string to be delimited.
        delimiter : Optional[Callable[[str], List[str]]]
            String delimiting function.

        Returns
        -------
        out : Dict[str, str]
            Dictionary containing caption/credit.

        """
        if inp_str.strip() == '' or delimiter is None:
            return {
                    'caption': 'NO_CAPTION',
                    'credit': 'NO_CREDIT'
                   }
        splits = delimiter(inp_str)
        if len(splits) == 1:
            return {
                    'caption': (splits[0]),
                    'credit': 'NO_CREDIT'
                   }
        if splits[0].strip() == '':
            return {
                    'caption': 'NO_CAPTION',
                    'credit': (splits[1])
                   }
        else:
            return {
                    'caption': (splits[0]),
                    'credit': (splits[1])
                   }

    def get_images(self,
                   parent_div: str,
                   input_list: Optional[List[Dict[str, str]]] = None,
                   caption_span: Optional[str] = None,
                   credit_span: Optional[str] = None,
                   delimiter: Optional[Callable[[str], List[str]]] = None
                   ) -> List[Dict[str, str]]:
        """
        Return list of image caption/credit dictionaries.

        Parameters
        ----------
        parent_div : str
            The css selector of the parent div.
        input_list : Optional[List[Dict[str, str]]]
            List of "images" as caption/credit dictionaries. Defaults to None.
        caption_span : str
            The css selector of the caption span. Defaults to None.
        credit_span : str
            The css selector of the credit span. Defaults to None.
        delimiter : Optional[Callable[[str], List[str]]]
            String delimiting function. Defaults to None.

        Returns
        -------
        out : List[Dict[str, str]]
            List of dictionaries containing caption/credit.

        """
        if input_list is None:
            input_list = []
        try:
            elements = self.driver.find_elements_by_css_selector(parent_div)
            for element in elements:
                if caption_span is None and credit_span is None:
                    image = self.delim_caption(element.text, delimiter)
                else:
                    image = self.get_caption_and_credit(element,
                                                        caption_span,
                                                        credit_span
                                                        )
                input_list.append(image)
            return input_list
        except NoSuchElementException:
            return input_list

    __article_cache = {}

    def get_article(self,
                    images: List[Dict[str, str]],
                    date: str,
                    index: int,
                    messages: Optional[List[str]] = None
                    ) -> Article:
        """
        Return article object.

        If article object was already generated, return
        memoized article.

        Parameters
        ----------
        images : List[Dict[str, str]]
            List of "images" as caption/credit dictionaries.
        date : str
            The css selector of the article date.
        index : int
            Index corresponding to the sheet index from which the
            article url was extracted.
        messages : str
            String list of debug messages. Defaults to None.

        Returns
        -------
        out : Article
            Article object.

        """
        if messages is None:
            messages = []
        article_url = self.url
        # Strip unnecessary url headers for better memoization
        try:
            stripped_url = article_url[:article_url.index("?")]
        except ValueError:
            stripped_url = article_url
        if stripped_url in self.__article_cache:
            print("Memoized previously processed article")
            cached_article = self.__article_cache[stripped_url]
            cached_dict = cached_article.as_dictionary
            # Create a copy, not reference, of old article
            messages = list(cached_dict['messages'])
            messages.append("MEMOIZED")
            article = Article(images=cached_dict['images'],
                              date=cached_dict['date'],
                              num_images=cached_dict['num_images'],
                              url=cached_dict['url'],
                              index=index,
                              messages=messages
                              )
            return article

        try:
            article_date = self.driver.find_element_by_css_selector(date).text
        except NoSuchElementException:
            article_date = "NO_DATE"

        article = Article(images=images,
                          date=article_date,
                          num_images=len(images),
                          url=stripped_url,
                          index=index,
                          messages=messages
                          )
        self.__article_cache[stripped_url] = article
        return article
