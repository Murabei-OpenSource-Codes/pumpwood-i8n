"""Define exceptions for Pumpwood I8n package."""


class PumpwoodI8nException(Exception):
    """Generic exception for PumpwoodI8n."""

    def __init__(self, message: str, payload: dict = {}):
        Exception.__init__(self)
        self.message = message.format(**payload)
        self.payload = payload


class PumpwoodI8nTranslationException(Exception):
    """Error when translating an sentence."""

    def __init__(self, message: str, payload: dict = {}):
        Exception.__init__(self)
        self.message = message.format(**payload)
        self.payload = payload
