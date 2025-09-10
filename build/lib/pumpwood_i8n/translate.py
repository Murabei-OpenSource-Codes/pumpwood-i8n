"""Internationalization for Pumpwood."""
import os
import warnings
from loguru import logger
from pumpwood_i8n.exceptions import PumpwoodI8nException


class PumpwoodI8n:
    """Class for internationalization of Pumpwood.

    Constant:
        CACHE_KEY_TEMPLATE (str): Template to create key for store
            translation  cash.
    """
    # Django model for internationalization
    # pumpwood_djangoauth.i8n.models.PumpwoodI8nTranslation
    _i8n_model: object = None

    # Pumpwood _microservice to ask translation using API calls
    _microservice: object = None

    def __init__(self, microservice: object = None, tag: str = None,
                 pumpwood_cache: object = None, cache_expire: int = None):
        """__init__.

        Class can be loaded later using init method.

        Use PUMPOOD__I8N__CACHE_EXPIRY (hours [float] of expirity) enviroment
        variable to set expirity time for translation.

        Args:
            microservice (object):
                PumpwoodMicroservice object, PumpwoodI8n will use API to
                retrieve translation.
            tag (str):
                Set a default tag to translations.
            pumpwood_cache (object):
                A pumpwood cache object that can be used to store
                translation.
            cache_expire (int):
                Seconds to invalidate cache for transalation, if not set it
                will be retrieved from `PUMPWOOD_I8N__CACHE_EXPIRE` env
                variable (default 3600 seconds, 1h).
        """
        self._microservice = None
        """Microservice object to comunicate with backend."""
        self._pumpwood_cache = None
        """Pumpwood cache object."""
        self._tag = None
        """Default tag for translation."""
        self._cache_expire = int(
            os.getenv('PUMPWOOD_I8N__CACHE_EXPIRE', '3600'))
        """Store the time that will be considered to expire the cache."""
        self.init(
            microservice=microservice, tag=tag,
            pumpwood_cache=pumpwood_cache)

    def init(self, microservice: object = None, tag: str = None,
             pumpwood_cache: object = None):
        """Init model.

        Class can be loaded later using init method.

        Use PUMPOOD__I8N__CACHE_EXPIRY (hours [float] of expirity) enviroment
        variable to set expirity time for translation.

        Args:
            microservice (object):
                PumpwoodMicroservice object, PumpwoodI8n
                will use API to retrieve translation.
            tag (str):
                Set a default tag to translations.
            pumpwood_cache (object):
                A pumpwood cache object that can be used to store
                translation.
        """
        # Lazy load PumpwoodI8nTranslation
        self._microservice = microservice
        self._pumpwood_cache = pumpwood_cache

        # Set default tag
        self._tag = tag

        # Check if object was not initializated corretly
        is_none__i8n_model = self._i8n_model is None
        is_none__microservice = self._microservice is None
        if not is_none__i8n_model and not is_none__microservice:
            raise PumpwoodI8nException(
                "PumpwoodI8n initializate with both backends, please choose "
                "junt one")

    @classmethod
    def _build_hash_dict(cls, sentence: str, tag: str = "",
                         plural: bool = False, language: str = "",
                         user_type: str = ""):
        """Build cache dict."""
        return {
            'sentence': sentence, 'tag': tag,
            'plural': plural, 'language': language,
            'user_type': user_type}

    def t(self, sentence: str, tag: str = "",
          plural: bool = False, language: str = "",
          user_type: str = "") -> str:
        """Translate sentence using PumpwoodI8n backend.

        It will try to translate sentence, if not possible will return
        the same string as sentence and add a new entry for translation on
        backend.

        It is possible  to set other parameters for translation such as
        plural, language, user_type. The macth must be equal to present on
        I8n database.

        Args:
            sentence (str):
                Sentence to be translated.
            tag (str):
                A tag to indentify context of a sentence, it is
                possible that the same sentence should be translated
                differently according to context.
            plural (str):
                Set if the sentence should be translated as plural.
            language (str):
                Set the language that the sentence should be
                translated.
            user_type (str):
                Using user_type it is possible to return
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

        if self._microservice is None:
            msg = (
                "microservice object not initializated, returning sentence "
                "without treatment.")
            warnings.warn(msg)
            return sentence

        # Set a default tag
        tag = tag or self._tag

        # Get translation cache not to make too many calls on backend
        hash_dict = None
        if self._pumpwood_cache is not None:
            hash_dict = self._build_hash_dict(
                sentence=sentence, tag=tag, plural=plural, language=language,
                user_type=user_type)
            cache_results = self._pumpwood_cache.get(hash_dict=hash_dict)
            if cache_results is not None:
                logger.info("get translation cache")
                return cache_results

        translation = self.translate__microservice(
            sentence=sentence, tag=tag, plural=plural, language=language,
            user_type=user_type)

        # Set cache if avaliable
        if self._pumpwood_cache is not None:
            self._pumpwood_cache.set(
                hash_dict=hash_dict, value=translation,
                expire=self._cache_expire)
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
                    "language": language, "user_type": user_type})
            return action_result["result"]

        # IF not possible to translate sentence, return same value
        except Exception as e:
            msg = (
                "Translation request to API did not work, check "
                "errors bellow.\n{error}").format(error=str(e))
            warnings.warn(msg)
            return sentence
