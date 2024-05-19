from enum import Enum


class DownloadResult(Enum):
    DownloadSuccess = 0
    FileExists = 1
    ConnectionFailed = 2
