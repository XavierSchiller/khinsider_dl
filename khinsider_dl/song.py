import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from khinsider_dl.constants import SONGFILE_URL
from khinsider_dl.dlutils import get_url_and_convert_to_soup

from .file import File


class Song:
    """A song on KHInsider.

    Properties:
    * url:   The full URL of the song page.
    * name:  The name of the song.
    * files: A list of the song's files - there may be several if the song
             is available in more than one format.
    """

    _page_content: BeautifulSoup | None

    def __init__(self, url: str):
        # TODO: Find name via URL directly, don't bother parsing
        self.url = url
        self._page_content = None

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.url)

    def get_page_content(self, http_client: requests.Session) -> BeautifulSoup:
        if self._page_content is None:
            self._page_content = get_url_and_convert_to_soup(http_client, self.url)
        return self._page_content

    def get_files(self, http_client: requests.Session):
        page_content = self.get_page_content(http_client)

        anchors = page_content.find_all("a", href=SONGFILE_URL)
        return [File(urljoin(self.url, a["href"])) for a in anchors]

    def get_appropriate_file(
        self, http_client: requests.Session, formatOrder: list[str]
    ) -> File | None:
        files = self.get_files(http_client)

        if len(formatOrder) == 0:
            return files[0]

        for extension in formatOrder:
            for file in files:
                if os.path.splitext(file.filename)[1].strip(".").lower() == extension:
                    return file

        return None
