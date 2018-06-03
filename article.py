from typing import List, Dict, Optional, Union


class Article:
    def __init__(self,
                 images: Optional[List[Dict[str, str]]] = None,
                 date: str = "",
                 num_images: int = -1,
                 url: str = "",
                 index: int = -1,
                 messages: Optional[List[str]] = None
                 ):
        """
        Article constructor.

        Parameters
        ----------
        images : List[Dict[str, str]]
            List of "images" as caption/credit dictionaries. Defaults to None.
        date : str
            The css selector of the article date. Defaults to "".
        num_images : int
            The length of 'images'. Defaults to -1.
        url : str
            The URL of the article. Defaults to "".
        index : int
            Index corresponding to the sheet index from which the
            article url was extracted.
        messages : str
            String list of debug messages. Defaults to None.

        """
        if messages is None:
            messages = []
        if images is None:
            images = []
        self.__images = images
        self.__date = date
        self.__num_images = num_images
        self.__url = url
        self.__index = index
        self.__messages = messages

    @property
    def index(self) -> int:
        return self.__index

    @index.setter
    def index(self, index: int):
        self.__index = index

    @property
    def images(self) -> List[Dict[str, str]]:
        return self.__images

    @images.setter
    def images(self, images: List[Dict[str, str]]):
        self.__images = images

    @property
    def date(self) -> str:
        return self.__date

    @date.setter
    def date(self, date: str):
        self.__date = date

    @property
    def url(self) -> str:
        return self.__url

    @url.setter
    def url(self, url: str):
        self.__url = url

    @property
    def num_images(self) -> int:
        return self.__num_images

    @num_images.setter
    def num_images(self, num_images: int):
        self.__num_images = num_images

    @property
    def messages(self) -> List[str]:
        return self.__messages

    @messages.setter
    def messages(self, messages: List[str]):
        self.__messages = messages

    @property
    def as_dictionary(self) -> Dict[str,
                                    Union[str,
                                          int,
                                          List[str],
                                          List[Dict[str, str]]
                                          ]
                                    ]:
        """Return article object as dictionary."""
        return {
                'images': self.images,
                'date': self.date,
                'num_images': self.num_images,
                'url': self.url,
                'index': self.index,
                'messages': self.messages
               }

    def append_message(self, message: str):
        self.__messages.append(message)
