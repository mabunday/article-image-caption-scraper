from dataclasses import dataclass
from typing import Callable, List

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement


@dataclass(frozen=True)
class Image:
    """Dataclass for images."""
    caption: str
    credit: str


def get_image(element: WebElement,
              caption: str,
              credit: str) -> Image:

    try:
        caption = element.find_element_by_css_selector(caption).text
    except NoSuchElementException:
        caption = ''

    try:
        credit = element.find_element_by_css_selector(credit).text
    except NoSuchElementException:
        credit = ''

    return Image(caption, credit)


def delim_image(
    inp_str: str,
    delimiter: Callable[[str], List[str]]
) -> Image:

    splits = delimiter(inp_str)

    if not inp_str.strip() or delimiter is None:
        image = Image('', '')
    elif len(splits) == 1:
        image = Image(splits[0], '')
    elif not splits[0].strip():
        image = Image('', splits[1])
    else:
        image = Image(splits[0], splits[1])
    return image
