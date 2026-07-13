"""Singleton instance for Pumpwood internationalization.

Import ``pumpwood_i8n`` and call ``init`` during application startup to
configure the translation backend once and reuse it across the codebase.

Usage::

    from pumpwood_i8n.singletons import pumpwood_i8n

    pumpwood_i8n.init(
        i8n_model='myapp.models.TranslationModel')
"""
from pumpwood_i8n.translate import PumpwoodI8n

# Instantiate an object to be initialized at application startup.
pumpwood_i8n = PumpwoodI8n()
"""I8n singleton instance."""
