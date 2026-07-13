"""Internationalization for Pumpwood.

PumpwoodI8n provides translation through a remote microservice backend
or a local model class with a callable ``translate`` method.

Usage::

    from pumpwood_i8n.translate import PumpwoodI8n
    from pumpwood_communication.microservices import PumpWoodMicroService

    microservice = PumpWoodMicroService(
        server_url='http://localhost/',
        username='user', password='pass')
    i8n = PumpwoodI8n(microservice=microservice)
    text = i8n.t(sentence='Hello', tag='login')

Local backend::

    def django_apps_ready():
        try:
            from django.apps import apps
            return apps.ready
        except Exception:
            return False

    i8n = PumpwoodI8n(
        i8n_model='myapp.models.TranslationModel',
        app_ready_check=django_apps_ready)
    text = i8n.t(sentence='Hello')
"""
from typing import Callable
from loguru import logger
from dataclasses import dataclass
from pumpwood_communication.type import PumpwoodDataclassMixin
from pumpwood_i8n.exceptions import PumpwoodI8nException
from pumpwood_i8n.aux import _import_function_by_string
from pumpwood_i8n.config import (
    PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION, PUMPWOOD_I8N__I8N_MODEL)


@dataclass
class PumpwoodI8nTranslationCache(PumpwoodDataclassMixin):
    """Cache key fields for a translation request."""

    sentence: str
    """Sentence to be translated."""
    tag: str
    """Tag to identify context of a sentence."""
    plural: bool
    """Whether the sentence should be translated as plural."""
    language: str
    """Language the sentence should be translated to."""
    user_type: str
    """Using user_type it is possible to return
    different names for the same object according to end-user
    knowledge. This might be helpful on Pumpwood since the
    Modeling Unit might be a product or a customer or other
    unit. Using user_type it is possible to translate
    DescriptionModelingUnit differently for each user."""

    context: str = "pumpwood_i8n__translation"
    """Context for the cache key."""


class PumpwoodI8n:
    """Class for internationalization of Pumpwood.

    PumpwoodI8n supports two mutually exclusive backends: a
    ``PumpwoodMicroservice`` for remote API translation, or a local model
    class (or dotted import path) that implements ``translate``.

    Attributes:
        _i8n_model (str | type | None):
            Local model class or dotted path used for translation.
        _microservice (object):
            Pumpwood microservice object used for remote translation.
    """

    # Django model for internationalization
    # pumpwood_djangoauth.i8n.models.PumpwoodI8nTranslation
    _i8n_model: str | type | None = None

    # Pumpwood _microservice to ask translation using API calls
    _microservice: object = None

    def __init__(self, microservice: object = None, tag: str = None,
                 pumpwood_cache: object = None,
                 i8n_model: str | type | None = None,
                 app_ready_check: Callable[[], bool] | None = None):
        """Initialize PumpwoodI8n.

        The object can also be configured later using ``init``.

        Cache expiration is read from the
        ``PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION`` environment variable
        (seconds).

        Args:
            microservice (object):
                PumpwoodMicroservice object. PumpwoodI8n will use the API
                to retrieve translations.
            tag (str):
                Default tag for translations.
            pumpwood_cache (object):
                Pumpwood cache object used to store translations.
            i8n_model (str | type | None):
                Model class to use for local translation. When not set,
                ``PUMPWOOD_I8N__I8N_MODEL`` is used.
            app_ready_check (Callable[[], bool] | None):
                Optional callable that returns whether the host
                application is ready for local translation. When it
                returns ``False``, ``translate_local`` returns the
                original sentence without loading the model.
        """
        self._microservice = None
        """Microservice object to communicate with backend."""
        self._pumpwood_cache = None
        """Pumpwood cache object."""
        self._tag = None
        """Default tag for translation."""
        self._cache_expire = PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION
        """Seconds before cached translations expire."""
        self._is_local = None
        """Flag indicating local or remote translation backend."""
        self._app_ready_check = None
        """Callable that checks host application readiness."""
        self.init(
            microservice=microservice, tag=tag,
            pumpwood_cache=pumpwood_cache, i8n_model=i8n_model,
            app_ready_check=app_ready_check)

    def init(self, microservice: object = None, tag: str = None,
             pumpwood_cache: object = None,
             i8n_model: str | type | None = None,
             app_ready_check: Callable[[], bool] | None = None):
        """Configure PumpwoodI8n backends and defaults.

        Only one backend may be active: ``microservice`` or ``i8n_model``.
        Cache expiration is read from the
        ``PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION`` environment variable
        (seconds).

        Args:
            microservice (object):
                PumpwoodMicroservice object. PumpwoodI8n will use the API
                to retrieve translations.
            tag (str):
                Default tag for translations.
            pumpwood_cache (object):
                Pumpwood cache object used to store translations.
            i8n_model (str | type | None):
                Model class to use for local translation. When not set,
                ``PUMPWOOD_I8N__I8N_MODEL`` is used.
            app_ready_check (Callable[[], bool] | None):
                Optional callable that returns whether the host
                application is ready for local translation. When it
                returns ``False``, ``translate_local`` returns the
                original sentence without loading the model.

        Raises:
            PumpwoodI8nException:
                If both ``microservice`` and ``i8n_model`` are provided.
        """
        # Use the model passed as argument or fallback to environment variable
        i8n_model = i8n_model or PUMPWOOD_I8N__I8N_MODEL

        # Allow only one backend to be used at each time
        is_none_i8n_model = i8n_model is None
        is_none_microservice = microservice is None
        if not is_none_i8n_model and not is_none_microservice:
            raise PumpwoodI8nException(
                "PumpwoodI8n initializate with both backends, please choose "
                "junt one")

        self._microservice = microservice
        self._pumpwood_cache = pumpwood_cache
        self._tag = tag

        # i8n_model may be a string loaded later by load_i8n_model
        self._i8n_model = i8n_model
        self._is_local = not is_none_i8n_model
        if app_ready_check is not None:
            self._app_ready_check = app_ready_check

    def _is_app_ready(self) -> bool:
        """Return whether the host application is ready.

        When no ``app_ready_check`` callback is configured, local
        translation is always considered ready.

        Returns:
            bool:
                ``True`` when local translation may proceed.
        """
        if self._app_ready_check is None:
            return True
        return self._app_ready_check()

    def load_i8n_model(self) -> type:
        """Load and validate the local i8n model.

        When ``_i8n_model`` is a dotted import path, the class is imported
        lazily and cached on the instance.

        Returns:
            type:
                Model class that implements a callable ``translate`` method.

        Raises:
            PumpwoodI8nException:
                If the model is not configured or does not implement
                ``translate``.
        """
        if self._i8n_model is None:
            msg = (
                "I8n model not found, please check if it is "
                "correctly set in the environment variable "
                "PUMPWOOD_I8N__I8N_MODEL.")
            raise PumpwoodI8nException(msg)

        # Lazzy load the model for translation
        if type(self._i8n_model) is str:
            self._i8n_model = _import_function_by_string(self._i8n_model)

        if not callable(getattr(self._i8n_model, 'translate', None)):
            msg = (
                "I8n model [{model}] does not implement a callable "
                "'translate' method.").format(model=self._i8n_model)
            raise PumpwoodI8nException(msg)
        return self._i8n_model

    def t(self, sentence: str | None, tag: str = "",
          plural: bool = False, language: str = "",
          user_type: str = "") -> str | None:
        """Translate a sentence using the configured backend.

        When translation is not possible, the original sentence is returned
        and a new entry may be created on the backend. Parameters must match
        records stored in the i8n database.

        Args:
            sentence (str | None):
                Sentence to be translated. When ``None``, returns ``None``
                without calling the backend.
            tag (str):
                Tag to identify the context of a sentence. The same sentence
                may be translated differently according to context.
            plural (bool):
                Whether the sentence should be translated as plural.
            language (str):
                Target language for the translation.
            user_type (str):
                Using user_type it is possible to return different names for
                the same object according to end-user knowledge. This might
                be helpful on Pumpwood since the Modeling Unit might be a
                product or a customer or other unit. Using user_type it is
                possible to translate DescriptionModelingUnit differently for
                each user.

        Returns:
            str | None:
                Translated sentence, the original sentence when translation
                fails, or ``None`` when ``sentence`` is ``None``.
        """
        if sentence is None:
            return None

        if (self._i8n_model is None) and (self._microservice is None):
            msg = (
                "microservice object not initializated, returning sentence "
                "without treatment.")
            logger.warning(msg)
            return sentence

        # Set a default tag
        tag = tag or self._tag

        # Get translation cache not to make too many calls on backend
        hash_dict = PumpwoodI8nTranslationCache(
            sentence=sentence, tag=tag, plural=plural, language=language,
            user_type=user_type).to_dict()
        if self._pumpwood_cache is not None:
            cache_results = self._pumpwood_cache.get(hash_dict=hash_dict)
            if cache_results is not None:
                logger.info("get translation cache")
                return cache_results

        # Run translation according to backend configuration
        if self._is_local:
            translation = self.translate_local(
                sentence=sentence, tag=tag, plural=plural, language=language,
                user_type=user_type)
        else:
            translation = self.translate_microservice(
                sentence=sentence, tag=tag, plural=plural, language=language,
                user_type=user_type)

        # Set cache if avaliable
        if self._pumpwood_cache is not None:
            self._pumpwood_cache.set(
                hash_dict=hash_dict, value=translation,
                expire=self._cache_expire)
        return translation

    def translate_microservice(self, sentence: str, tag: str = "",
                               plural: bool = False, language: str = "",
                               user_type: str = "") -> str:
        """Translate a sentence using the microservice backend.

        Args:
            sentence (str):
                Sentence to be translated.
            tag (str):
                Tag to identify the context of a sentence.
            plural (bool):
                Whether the sentence should be translated as plural.
            language (str):
                Target language for the translation.
            user_type (str):
                User context used to differentiate translations.

        Returns:
            str:
                Translated sentence, or the original sentence when the API
                request fails.
        """
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
            logger.warning(msg)
            return sentence

    def translate_local(self, sentence: str, tag: str = "",
                        plural: bool = False, language: str = "",
                        user_type: str = "") -> str:
        """Translate a sentence using the local i8n model.

        Args:
            sentence (str):
                Sentence to be translated.
            tag (str):
                Tag to identify the context of a sentence.
            plural (bool):
                Whether the sentence should be translated as plural.
            language (str):
                Target language for the translation.
            user_type (str):
                User context used to differentiate translations.

        Returns:
            str:
                Translated sentence, the original sentence when the host
                application is not ready, or the original sentence when
                local translation fails.
        """
        if not self._is_app_ready():
            return sentence

        try:
            i8n_model = self.load_i8n_model()
            if i8n_model is None:
                raise PumpwoodI8nException(
                    "I8n model not found, please check if it is "
                    "correctly set.")

            translation = i8n_model.translate(
                sentence=sentence, tag=tag, plural=plural, language=language,
                user_type=user_type)
            return translation

        except Exception as e:
            msg = (
                "Local translation did not work, check errors "
                "bellow.\n{error}").format(error=str(e))
            logger.warning(msg)
            return sentence
