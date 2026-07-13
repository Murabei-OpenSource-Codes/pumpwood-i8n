"""Configuration helpers for PumpwoodI8n.

Reads environment variables used to configure translation cache expiration
and the default local i8n model.
"""
import os


PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION = int(
    os.getenv('PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION', '300'))
"""Seconds before cached translations expire.

Retrieved from ``PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION`` (default 300
seconds).
"""

PUMPWOOD_I8N__I8N_MODEL = os.getenv('PUMPWOOD_I8N__I8N_MODEL', None)
"""Dotted path to the local i8n model class.

Retrieved from ``PUMPWOOD_I8N__I8N_MODEL`` when not set explicitly on
``PumpwoodI8n`` initialization.
"""
