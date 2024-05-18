class KhinsiderError(Exception):
    pass


class SearchError(KhinsiderError):
    pass


class NonexistentSongError(KhinsiderError):
    pass


class SoundtrackError(Exception):
    def __init__(self, soundtrack):
        self.soundtrack = soundtrack


class NonexistentSoundtrackError(SoundtrackError, ValueError):
    def __str__(self):
        ost = (
            '"{}" '.format(self.soundtrack.id) if len(self.soundtrack.id) <= 80 else ""
        )
        s = "The soundtrack {}does not exist.".format(ost)
        return s


class NonexistentFormatsError(SoundtrackError, ValueError):
    def __init__(self, soundtrack, requestedFormats):
        super(NonexistentFormatsError, self).__init__(soundtrack)
        self.requestedFormats = requestedFormats

    def __str__(self):
        ost = (
            '"{}" '.format(self.soundtrack.id) if len(self.soundtrack.id) <= 80 else ""
        )
        s = "The soundtrack {}is not available in the requested formats ({}).".format(
            ost,
            ", ".join('"{}"'.format(extension) for extension in self.requestedFormats),
        )
        return s


class InvalidPathError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
