import requests
from bs4 import BeautifulSoup

from khinsider_dl.constants import BAD_AMPERSAND_RE, FILENAME_INVALID_RE, REMOVE_RE


def to_valid_filename(s):
    # Windows's Explorer doens't handle filenames that end in ' ' or '.'.
    s = s.rstrip(" .")

    if s in {
        "",
        ".",
        "..",
        "~",
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }:
        return s + "_"

    return FILENAME_INVALID_RE.sub("-", s)


def get_url_and_convert_to_soup(
    http_client: requests.Session, url: str
) -> BeautifulSoup:
    response = http_client.get(url)
    content = response.content

    content = REMOVE_RE.sub(b"", content)
    content = BAD_AMPERSAND_RE.sub(b"&amp;#\1", content)

    return BeautifulSoup(content, "html.parser")
