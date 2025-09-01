# Changelog

## Version 1.10.0
Released YYYY-MM-DD
* **[Litestar]** Improves HTMXBlockTemplate compatibility with Template class - HTMXBlockTemplate can now be used as a drop-in replacement for Template with single positional argument for template_name.
* **[Litestar]** Adds backward compatibility support with deprecation warnings for multiple positional arguments in HTMXBlockTemplate constructor. The old signature will be removed in a future version.
* **[Litestar]** Fixes deprecated HTMXRequest import to support both litestar>=2.13.0 and litestar<2.13.0.
* Adds comprehensive test suite for HTMXBlockTemplate compatibility scenarios.

## Version 1.9.0
Released 2025-04-20
* Adds support for newer FastAPI `TemplateResponse` pattern ([PR #42](https://github.com/sponsfreixes/jinja2-fragments/pull/42)).
* Migrates project from `setup.py` to `pyproject.toml`.
* Replaces existing pre-commit hooks (black, isort, pyupgrade, flake8) with Ruff.
* Adds Sphinx documentation.

## Version 1.8.0
Released 2025-02-27
* Adds support for rendering multiple blocks on Flask, Quart, Sanic and Litestar (solves [Issue #40](https://github.com/sponsfreixes/jinja2-fragments/issues/40)).
* Fixes deprecated Litestar import ([PR #38](https://github.com/sponsfreixes/jinja2-fragments/pull/38)).

## Version 1.7.0
Released 2024-12-24
* Adds support for Litestar>=2.13.0 ([PR #37](https://github.com/sponsfreixes/jinja2-fragments/pull/37)).
* Drops support for Python 3.8.

## Version 1.6.0
Released 2024-08-21
* Adds support for rendering multiple blocks ([PR #34](https://github.com/sponsfreixes/jinja2-fragments/pull/34)).

## Version 1.5.0
Released 2024-07-06
* Removes support for Jinja macros. This feature introduced a bug that breaks some complex templates. See discussion on [Issue #21](https://github.com/sponsfreixes/jinja2-fragments/issues/21).

## Version 1.4.1
Released 2024-07-03
* Fixes regression: dictionary access ([PR #33](https://github.com/sponsfreixes/jinja2-fragments/pull/33)).

## Version 1.4.0
Released 2024-06-30
* Adds support for Jinja macros ([PR #30](https://github.com/sponsfreixes/jinja2-fragments/pull/30)).

## Version 1.3.0
Released 2024-01-29
* Adds support for Litestar ([PR #26](https://github.com/sponsfreixes/jinja2-fragments/pull/26)).
* Drops support for Python 3.7.

## Version 1.2.1
Released 2023-10-26
* Adds missing `py.typed` marker file to wheels.

## Version 1.2.0
Released 2023-10-22
* Adds support for Quart>=0.19.0 ([PR #22](https://github.com/sponsfreixes/jinja2-fragments/pull/22)).
* Adds `py.typed` marker file as per PEP 561.

## Version 1.1.0
Released 2023-09-30
* Fixes tests for Sanic on Python 3.7
* Improves FastAPI support by returning a Response object instead of string ([PR #16](https://github.com/sponsfreixes/jinja2-fragments/pull/16)).

## Version 1.0.0
Released 2023-08-30
* Adds support for Sanic ([PR #14](https://github.com/sponsfreixes/jinja2-fragments/pull/14)).
* Improves FastAPI documentation ([PR #4](https://github.com/sponsfreixes/jinja2-fragments/pull/4)).
* Fixes tests dependencies ([PR #9](https://github.com/sponsfreixes/jinja2-fragments/pull/9)).
* Fixes Flask/Quart signal name typo ([PR #10](https://github.com/sponsfreixes/jinja2-fragments/pull/10)).
* Fixes test for BlockNotFoundError ([PR #12](https://github.com/sponsfreixes/jinja2-fragments/pull/12)).
* Adds GitHub actions for pre-commits and tests ([PR #13](https://github.com/sponsfreixes/jinja2-fragments/pull/13)).

## Version 0.3.0
Released 2022-09-18
* Adds support for FastAPI ([PR #2](https://github.com/sponsfreixes/jinja2-fragments/pull/2)).

## Version 0.2.0
Released 2022-09-10
* Adds support for Quart ([PR #1](https://github.com/sponsfreixes/jinja2-fragments/pull/1)).

## Version 0.1.1
Released 2022-09-08
* Fixes bug with async support.

## Version 0.1.0
Released 2022-09-04
* First release of Jinja2 Fragments.
* Includes support for Flask.
