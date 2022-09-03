import pathlib

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape


@pytest.fixture(scope="session")
def environment():
    return Environment(
        loader=FileSystemLoader("tests/templates"),
        autoescape=select_autoescape(("html", "jinja2")),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture(scope="function")
def get_html():
    def _get_html(page_name):
        return pathlib.Path(f"tests/rendered_templates/{page_name}").read_text()

    return _get_html


@pytest.fixture(scope="function")
def get_template(environment):
    def _get_template(template_name):
        return environment.get_template(template_name)

    return _get_template
