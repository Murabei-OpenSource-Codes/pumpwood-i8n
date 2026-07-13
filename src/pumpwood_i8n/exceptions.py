"""Define exceptions for the Pumpwood I8n package."""


class PumpwoodI8nException(Exception):
    """Generic exception for PumpwoodI8n."""

    def __init__(self, message: str, payload: dict = {}):
        """Initialize PumpwoodI8nException.

        Args:
            message (str):
                Error message. May contain format placeholders filled from
                ``payload``.
            payload (dict):
                Values used to format ``message``. Defaults to ``{}``.
        """
        Exception.__init__(self)
        self.message = message.format(**payload)
        self.payload = payload


class PumpwoodI8nTranslationException(Exception):
    """Error raised when translating a sentence."""

    def __init__(self, message: str, payload: dict = {}):
        """Initialize PumpwoodI8nTranslationException.

        Args:
            message (str):
                Error message. May contain format placeholders filled from
                ``payload``.
            payload (dict):
                Values used to format ``message``. Defaults to ``{}``.
        """
        Exception.__init__(self)
        self.message = message.format(**payload)
        self.payload = payload
