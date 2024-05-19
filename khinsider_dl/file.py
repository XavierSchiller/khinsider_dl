import os
import urllib
import urllib.parse

import requests

from khinsider_dl.result import DownloadResult

from .dlutils import to_valid_filename


class File:
    """A file belonging to a soundtrack on KHInsider.

    Properties:
    * url:          The full URL of the file.
    * filename:     The file's... filename. You got it.
    * http_client:  A `requests.Session` object
    """

    def __init__(self, url: str):
        self.url = url
        self.filename = urllib.parse.unquote(url.rsplit(str("/"), 1)[-1])

    def __repr__(self):
        return "<File: {}>".format(self.filename)

    def download(
        self,
        http_client: requests.Session,
        path: str | os.PathLike,
    ) -> DownloadResult:

        filename = to_valid_filename(self.filename)
        path = os.path.join(path, filename)

        if os.path.exists(path):
            return DownloadResult.FileExists

        try:
            response = http_client.get(self.url, timeout=10)
        except requests.ConnectionError:
            return DownloadResult.ConnectionFailed

        with open(path, "wb") as out_file:
            out_file.write(response.content)

        return DownloadResult.DownloadSuccess
