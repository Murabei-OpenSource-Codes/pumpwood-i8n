# PumpWood I8n

This package provides internationalization for Pumpwood systems. It can
translate sentences through a remote microservice backend or a local model
class that implements a ``translate`` method.

<p align="center" width="60%">
  <img src="doc/sitelogo-horizontal.png" /> <br>

  <a href="https://en.wikipedia.org/wiki/Cecropia">
    Pumpwood is a native Brazilian tree
  </a> which has a symbiotic relation with ants (Murabei)
</p>

## Quick start

The main class in the package is ``PumpwoodI8n``. It translates sentences
through the ``t`` method.

### Remote backend (microservice)

```python
from pumpwood_i8n.translate import PumpwoodI8n
from pumpwood_communication.microservices import PumpWoodMicroService


# Instantiate a microservice object to call the backend for translation.
microservice = PumpWoodMicroService(
    server_url='http://localhost/',
    username="pumpwood", password="is a nice system")

pumpwood_i8n = PumpwoodI8n(microservice=microservice)
translated_str = pumpwood_i8n.t(
    sentence="Translate this sequence please?",
    # Tags differentiate the same sentence in different contexts.
    tag="login",
    # Flag to indicate whether the translation is plural.
    plural=False,
    # Reference language for the translation.
    language="",
    # Optional user context for differentiated translations.
    user_type="")
```

It is also possible to instantiate an empty object and configure it later.

```python
from pumpwood_i8n.translate import PumpwoodI8n
from pumpwood_communication.microservices import PumpWoodMicroService


microservice = PumpWoodMicroService(
    server_url='http://localhost/',
    username="pumpwood", password="is a nice system")

pumpwood_i8n = PumpwoodI8n()
pumpwood_i8n.init(microservice=microservice)
```

### Local backend (Django model)

When running inside a Django application, configure a local model instead
of a microservice. Only one backend may be active at a time.

```python
from pumpwood_i8n.translate import PumpwoodI8n


def django_apps_ready():
    try:
        from django.apps import apps
        return apps.ready
    except Exception:
        return False


pumpwood_i8n = PumpwoodI8n(
    i8n_model='pumpwood_djangoauth.i8n.models.PumpwoodI8nTranslation',
    app_ready_check=django_apps_ready)
translated_str = pumpwood_i8n.t(
    sentence="Translate this sequence please?", tag="login")
```

The model path can also be set through the ``PUMPWOOD_I8N__I8N_MODEL``
environment variable. Pass ``app_ready_check`` when using a Django model
so translation is skipped until ``django.apps.apps.ready`` is ``True``.

### Singleton

Use the shared instance from ``singletons`` and initialize it at startup.

```python
from pumpwood_i8n.singletons import pumpwood_i8n
from pumpwood_communication.microservices import PumpWoodMicroService


microservice = PumpWoodMicroService(
    server_url='http://localhost/',
    username="pumpwood", password="is a nice system")

pumpwood_i8n.init(microservice=microservice)
```

## Cache

Pumpwood I8n can cache translations locally to avoid too many calls to
the backend. Cache entries expire after
``PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION`` seconds.

## Environment parameters

**PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION [int]:** Expiry time in seconds for
locally cached translations. After this period the sentence is translated
again and the local cache is renewed. Default is ``300``.

**PUMPWOOD_I8N__I8N_MODEL [str]:** Dotted path to the model class used for
local translation (lazy load). Example:
``pumpwood_djangoauth.i8n.models.PumpwoodI8nTranslation``.
