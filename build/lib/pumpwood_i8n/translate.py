"""Internationalization for Pumpwood."""
import os
import datetime
import warnings
from pumpwood_i8n.exceptions import (
    PumpwoodI8nException, PumpwoodI8nTranslationException)


class PumpwoodI8n:
    """
    Class for internationalization of Pumpwood.

    Constant:
        CACHE_KEY_TEMPLATE [str]: Template to create key for store
            translation  cash.
    """

    CACHE_KEY_TEMPLATE: str = (
        "{sentence}||{tag}||{plural}||{language}||{user_type}")

    # Django model for internationalization
    # pumpwood_djangoauth.i8n.models.PumpwoodI8nTranslation
    _i8n_model: object = None

    # Pumpwood _microservice to ask translation using API calls
    _microservice: object = None

    # Keeps a translations cache to reduce calls to backend,
    _translation_cache: dict = {}

    # Time in hours until invalidate translation cache
    _cache_expiry: float = None

    def __init__(self, microservice: object = None, tag: str = None):
        """
        __init__.

        Class can be loaded later using init method.

        Use PUMPOOD__I8N__CACHE_EXPIRY (hours [float] of expirity) enviroment
        variable to set expirity time for translation.

        Kargs:
            use_i8n_model [bool]: Lazy load PumpwoodI8nTranslation from
                pumpwood_djangoauth.i8n.models and use it as backend. Used
                when extending Pumpwood Auth App that is in Django,
            microservice [object]: PumpwoodMicroservice object, PumpwoodI8n
                will use API to retrieve translation.
            cache_expiry [float]: Time (hours) to expire class cache for
                translation calls.
        """
        self.init(microservice=microservice, tag=tag)

    def init(self, microservice: object = None, tag: str = None):
        """
        Init model.

        Class can be loaded later using init method.

        Use PUMPOOD__I8N__CACHE_EXPIRY (hours [float] of expirity) enviroment
        variable to set expirity time for translation.

        Kargs:
            use_i8n_model [bool]: Lazy load PumpwoodI8nTranslation from
                pumpwood_djangoauth.i8n.models and use it as backend. Used
                when extending Pumpwood Auth App that is in Django,
            microservice [object]: PumpwoodMicroservice object, PumpwoodI8n
                will use API to retrieve translation.
            cache_expiry [float]: Time (hours) to expire class cache for
                translation calls.
            tag [str]: Set a default tag to translations.
        """
        # Lazy load PumpwoodI8nTranslation
        self._microservice = microservice
        self._cache_expiry = float(os.getenv(
            "PUMPOOD__I8N__CACHE_EXPIRY", "1"))

        # Set default tag
        self._tag = tag

        # Check if object was not initializated corretly
        is_none__i8n_model = self._i8n_model is None
        is_none__microservice = self._microservice is None
        if not is_none__i8n_model and not is_none__microservice:
            raise PumpwoodI8nException(
                "PumpwoodI8n initializate with both backends, please choose "
                "junt one")

    def t(self, sentence: str, tag: str = "",
          plural: bool = False, language: str = "",
          user_type: str = "") -> str:
        """
        Translate sentence using PumpwoodI8n backend.

        It will try to translate sentence, if not possible will return
        the same string as sentence and add a new entry for translation on
        backend.

        It is possible  to set other parameters for translation such as
        plural, language, user_type. The macth must be equal to present on
        I8n database.

        Args:
            sentence [str]: Sentence to be translated.
        Kwargs:
            tag [str] = "": A tag to indentify context of a sentence, it is
                possible that the same sentence should be translated
                differently according to context.
            plural [str] = "": Set if the sentence should be translated as
                plural.
            language [str] = "": Set the language that the sentence should be
                translated.
            user_type [str] = "": Using user_type it is possible to return
                different names for the same object according to end-user
                knowloge. This might be helpfull on Pumpwood since the
                Modeling Unit might be a product or a costumer or other
                unit. Using user_type it is possible to translate
                DescriptionModelingUnit different to each user.
        Return [str | None]:
            Translated sentence according to parameters. If sentence is None
            translation will always be None and will no call backend.
        """
        if sentence is None:
            return None

        # Set a default tag
        tag = tag or self._tag

        now_time = datetime.datetime.utcnow()
        #############################################################
        # Get translation cache not to make too many calls on backend
        cache_key = self.CACHE_KEY_TEMPLATE.format(
            sentence=sentence, tag=tag, plural=plural, language=language,
            user_type=user_type)
        cache_results = self._translation_cache.get(cache_key, {})

        # Check if translation can be considered expired or is not set yet
        translation = cache_results.get("translation")
        expiry_time = cache_results.get(
            "expiry_time", datetime.datetime(1990, 1, 1))

        # Translation cache not set
        is_translation_none = translation is None
        # Translation expired
        is_translation_expired = expiry_time <= now_time
        if not is_translation_none and not is_translation_expired:
            # If not expired and not None translation will be returned
            # without calling backend
            return translation

        ############################################
        # Else... get translation from the backend #
        translation = None
        if self._microservice is not None:
            translation = self.translate__microservice(
                sentence=sentence, tag=tag, plural=plural, language=language,
                user_type=user_type)
        else:
            # Notify user if translation was atenpted, object was not
            # initializated.
            msg = (
                "PumpwoodI8n object not initializated, returning sentence "
                "without treatment.")
            warnings.warn(msg)
            return sentence

        # And save it as cache
        expiry_time = now_time + datetime.timedelta(hours=self._cache_expiry)
        self._translation_cache[cache_key] = {
            "translation": translation, "expiry_time": expiry_time}
        return translation

    def translate__microservice(self, sentence: str, tag: str = "",
                                plural: bool = False, language: str = "",
                                user_type: str = "") -> str:
        """Backend function for translation using _microservice."""
        try:
            # Force login using microservice
            self._microservice.login()
            action_result = self._microservice.execute_action(
                model_class="PumpwoodI8nTranslation", action="translate",
                parameters={
                    "sentence": sentence, "tag": tag, "plural": plural,
                    "language": language, "user_type": user_type,
                })
            return action_result["result"]

        # IF not possible to translate sentence, return same value
        except Exception as e:
            msg = (
                "Translation request to API did not work, check "
                "errors bellow.\n{error}").format(error=str(e))
            warnings.warn(msg)
            return sentence
