#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pathlib
import sys
from typing import List

import requests
import requests.adapters

from khinsider_dl.dlutils import get_url_and_convert_to_soup

from .consoleutils import printerr
from .customargparse import KHInsiderParsedArguments, KHInsiderParser
from .errors import (
    InvalidPathError,
    NonexistentFormatsError,
    NonexistentSoundtrackError,
)
from .soundtrack import Soundtrack

SCRIPT_NAME = os.path.split(sys.argv[0])[-1]


def validate_path_exists_or_create(path: pathlib.Path):
    if path.is_file():
        raise InvalidPathError("Path is a file, which is invalid")

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def download(
    http_client: requests.Session,
    soundtrack_url: str,
    path: pathlib.Path,
    formatOrder: List[str] = [],
):
    """Download the soundtrack with the ID `soundtrackId`.
    See Soundtrack.download for more information.
    """
    page_content = get_url_and_convert_to_soup(http_client, soundtrack_url)

    soundtrack = Soundtrack(soundtrack_url, page_content)
    print('Downloading to "{}".'.format(path))

    validate_path_exists_or_create(path)

    for file in soundtrack.get_files_to_download(http_client, formatOrder):
        print("Fetched {}, Downloading...".format(file))
        file.download(http_client, path)


def main():
    http_client = requests.session()
    http_client.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0"
                "(Windows NT 10.0; Win64; x64; rv:126.0)"
                "Gecko/20100101 Firefox/126.0"
            )
        }
    )

    retry_policy = requests.adapters.Retry(total=5, backoff_factor=1)
    http_client.mount(
        "http://", requests.adapters.HTTPAdapter(max_retries=retry_policy)
    )

    parser = KHInsiderParser()
    parser.create_arguments()

    try:
        arguments = parser.parse_args(namespace=KHInsiderParsedArguments)
    except InvalidPathError as error_instance:
        print(str(error_instance), file=sys.stderr)
        sys.exit(1)
    except ValueError as error_instance:
        print(str(error_instance), file=sys.stderr)
        sys.exit(1)

    try:
        download(
            http_client,
            arguments.input_url,
            arguments.output_directory,
            formatOrder=arguments.format_list,
        )
    except NonexistentSoundtrackError:
        print(
            'The soundtrack "{}" does not seem to exist.'.format(arguments.input_url),
            file=sys.stderr,
        )

        return 1
    except NonexistentFormatsError as e:
        s = (
            "Format{} not available. " 'The soundtrack "{}" is only available in the '
        ).format("" if len(arguments.format_list) == 1 else "s", arguments.input_url)

        formats = e.soundtrack.availableFormats
        if len(formats) == 1:
            s += '"{}" format.'.format(formats[0])
        else:
            s += '{}{} and "{}" formats.'.format(
                ", ".join('"{}"'.format(extension) for extension in formats[:-1]),
                "," if len(formats) > 2 else "",
                formats[-1],
            )

        print(s, file=sys.stderr)

        return 1
    except InterruptedError | KeyboardInterrupt:
        print("Interupted! Stopped download...", file=sys.stderr)
    except (requests.ConnectionError, requests.Timeout):
        print("Could not connect to KHInsider.", file=sys.stderr)

    return 0


sys.exit(main())
