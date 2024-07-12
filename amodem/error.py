class AmodemError(Exception):

    msg: str
    _PREFIX: str

    def __init__(self, message: str):
        self._PREFIX = "\n *** ERROR: "
        self.msg = self._PREFIX + message


class DecodingError(AmodemError):

    _PREFIX: str = "Decoding - "

    def __init__(self, message: str):
        super().__init__(self._PREFIX + message)


class ChecksumError(AmodemError):

    _PREFIX: str = "Checksum - "

    def __init__(self, message: str):
        super().__init__(self._PREFIX + message)


class PrefixError(AmodemError):

    _PREFIX: str = "Prefix - "

    def __init__(self, message: str):
        super().__init__(self._PREFIX + message)
