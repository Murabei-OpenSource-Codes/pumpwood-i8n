# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-07-13

### Added
- No adds.

### Changed
- Align ``pyproject.toml`` dependency declarations with Poetry build
  template.

### Removed
- No removes.

## [1.0.3] - 2026-07-13

### Added
- Local translation backend via ``i8n_model`` parameter or
  ``PUMPWOOD_I8N__I8N_MODEL`` environment variable.
- ``PumpwoodI8nTranslationCache`` dataclass for cache key generation.
- ``config`` module for environment variable helpers.
- ``aux`` module for lazy import of the local i18n model.
- ``translate_local`` backend method.
- ``load_i8n_model`` to validate and lazy-load the local model.
- ``app_ready_check`` callback to defer local translation until the
  host application is ready.
- ``pyproject_template.toml`` and Poetry build through ``build.sh``.

### Changed
- Rename ``translate__microservice`` to ``translate_microservice``.
- Read cache expiration from ``PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION``
  (seconds, default ``300``).
- ``t`` returns ``None`` when ``sentence`` is ``None`` without calling
  the backend.
- Replace ``warnings`` with ``loguru`` logger for backend failures.

### Removed
- ``cache_expire`` constructor argument and ``PUMPWOOD_I8N__CACHE_EXPIRE``
  environment variable.
- ``setup.py`` and ``setup_template.py`` build templates.

## [1.0.2] - 2025-09-09

### Added
- Set cache expire time using environment variable
  ``PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION``. Default is ``300`` seconds.

### Changed
- Refactor codes.

### Removed
- No removes.

## [1.0.1] - 2025-09-09

### Added
- Add disk cache for translation using pumpwood cache.

### Changed
- Refactor codes.

### Removed
- No removes.
