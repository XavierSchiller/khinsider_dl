import re

BASE_URL = "downloads.khinsider.com"

URL_REGEX = re.compile(
    r"^https?://{}/game-soundtracks/album/(?P<soundtrack>[^/]+)$".format(BASE_URL),
    re.IGNORECASE,
)

# Although some of these are valid on Linux, keeping this the same
# across systems is nice for consistency AND it works on WSL.
FILENAME_INVALID_RE = re.compile(r'[<>:"/\\|?*]')
REMOVE_RE = re.compile(rb"^</td>\s*$", re.MULTILINE)
BAD_AMPERSAND_RE = re.compile(rb"&#([^0-9x]|x[^0-9A-Fa-f])")
SONGFILE_URL = re.compile(r"^https?://[^/]+/(?:soundtracks|ost)/.+$")
