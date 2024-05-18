from functools import cached_property
from typing import Generator, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

from .consoleutils import printerr
from .errors import (
    NonexistentFormatsError,
    NonexistentSongError,
    NonexistentSoundtrackError,
)
from .file import File
from .song import Song


class Soundtrack:
    """Soundtrack represents a full list of songs with a specified format"""

    def __init__(self, soundtrack_url: str, content_soup: BeautifulSoup):
        """

        Args:
            soundtrackURL (str): URL of the album/soundtrack.
            content_soup (BeautifulSoup): The content soup of the page
        """
        self.url = soundtrack_url
        self._page_content = content_soup

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.url)

    @cached_property
    def _contentSoup(self) -> Tag:
        contentSoup = self._page_content.find(id="pageContent")

        if contentSoup is None or isinstance(contentSoup, NavigableString):
            raise NonexistentSoundtrackError(self)

        content = contentSoup.find("p")

        if not isinstance(content, Tag):
            raise NonexistentSoundtrackError(self)

        if content.string == "No such album":
            raise NonexistentSoundtrackError(self)

        return contentSoup

    @cached_property
    def get_name(self):
        inner_name = self._contentSoup.find("h2")

        if inner_name is None:
            raise NonexistentSoundtrackError(self)

        return next(inner_name.stripped_strings)

    @cached_property
    def get_available_formats(self) -> List[str]:
        table = self._contentSoup.find("table", id="songlist")

        if table is None or isinstance(table, NavigableString):
            raise NonexistentSoundtrackError(self)

        header = table.find("tr")

        if header is None or isinstance(header, NavigableString):
            raise NonexistentSoundtrackError(self)

        headings: List[str] = [td.get_text(strip=True) for td in header(["th", "td"])]
        formats = [
            s.lower()
            for s in headings
            if s not in {"", "Track", "Song Name", "Download", "Size"}
        ]
        formats = formats or ["mp3"]
        return formats

    @cached_property
    def get_songs(self):
        table = self._contentSoup.find("table", id="songlist")

        if table is None or isinstance(table, NavigableString):
            raise NonexistentSoundtrackError(self)

        rows: List[Tag] = table.find_all("tr")

        url_list: List[str] = []
        for row in rows:
            header = row.find("th")
            if header is not None:
                pass

            anchor = row.find("a", recursive=True)
            if isinstance(anchor, Tag):
                url = anchor.get("href")
                if isinstance(url, str):
                    url_list.append(url)

        songs = [Song(urljoin(self.url, url)) for url in url_list]
        return songs

    @cached_property
    def get_images(self):
        table = self._contentSoup.find("table")

        if table is None or isinstance(table, NavigableString):
            # Currently, the table is always present, but if it's ever removed
            # for imageless albums, it should be handled gracefully.
            return []

        image_urls: List[str] = []
        anchors: List[Tag] = table.find_all("a")
        for anchor in anchors:
            img_tag = anchor.find("img")
            if img_tag is not None and isinstance(img_tag, Tag):
                url = img_tag.get("href")
                if isinstance(url, str):
                    image_urls.append(url)

        images = [File(urljoin(self.url, url)) for url in image_urls]
        print(images)
        return images

    def get_files_to_download(
        self,
        http_client: requests.Session,
        formatOrder: List[str] = [],
    ) -> Generator[File, None, None]:
        """
        Set `formatOrder` to a list of file extensions to specify the order
        in which to prefer file formats. If set to ['flac', 'ogg', 'mp3'], for
        example, FLAC files will be downloaded if available - if not, Ogg
        files, and if those aren't available, MP3 files.

        Print progress along the way if `verbose` is set to True.

        Returns a `list[File]` of files that can be downloaded
        """

        if len(formatOrder) > 0:
            formatOrder = [extension.lower() for extension in formatOrder]
            if not set(self.get_available_formats) & set(formatOrder):
                raise NonexistentFormatsError(self, formatOrder)

        print("Getting song list...")

        for song in self.get_songs:
            try:
                yield song.get_appropriate_file(http_client, formatOrder)
            except NonexistentSongError:
                printerr("Files do not exist for song: {}".format(song.name))

        # Image files to also be returned here
        for file in self.get_images:
            yield file
