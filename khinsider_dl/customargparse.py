import argparse
import os
import pathlib
import sys
from typing import List

from .consoleutils import printerr
from .constants import URL_REGEX
from .errors import InvalidPathError

SCRIPT_DESCRIPTION = """
Download entire soundtracks from KHInsider.\n\n"
Examples:
%(prog)s jumping-flash
%(prog)s katamari-forever "music{}Katamari Forever OST"
%(prog)s --search persona
%(prog)s --format flac mother-3"
""".format(
    os.sep
).strip(
    "\n\r"
)


class KHInsiderParsedArguments(argparse.Namespace):
    input_url: str
    output_directory: pathlib.Path
    format_list: List[str]


def _parse_input_url(url_string: str) -> str:
    matched = URL_REGEX.match(url_string)
    if matched is None or not isinstance(matched.group("soundtrack"), str):
        raise ValueError("The given input is not recognized as a proper URL.")

    return url_string


def _parse_output_path(string_path: str) -> pathlib.Path:
    path = pathlib.Path(string_path)
    absolute_path = path.absolute()

    if absolute_path.is_file():
        raise InvalidPathError(
            "Cannot create path because it is a file: {}".format(absolute_path)
        )

    return absolute_path


def _parse_format_list(song_format: str):
    return song_format.strip(".").lower()


class KHInsiderParser(argparse.ArgumentParser):

    def create_arguments(self):
        self.description = SCRIPT_DESCRIPTION

        self.add_argument(
            "-i", "--input_url", help="URL of the soundtrack.", type=_parse_input_url
        )

        self.add_argument(
            "-o",
            "--output_directory",
            help=("The directory to download the soundtrack to."),
            type=_parse_output_path,
        )

        self.add_argument(
            "-f",
            "--format_list",
            default=None,
            metavar="...",
            help=(
                "The file format in which to download"
                "the soundtrack (e.g. 'flac').\n"
                "You can also specify this argument"
                "multiple times to select the order of favour"
                "(for example, -f flac -f mp3 -f ogg)"
            ),
            action="append",
            type=_parse_format_list,
        )

    def error(self, message):
        printerr(message)
        sys.exit(1)
