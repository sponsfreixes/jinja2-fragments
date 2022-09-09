import pathlib

import flask
import pytest
import quart
from jinja2 import Environment, FileSystemLoader, select_autoescape

from jinja2_fragments.flask import render_block as flask_render_block
from jinja2_fragments.quart import render_block as quart_render_block

NAME = "Guido"
LUCKY_NUMBER = "42"


@pytest.fixture(scope="session")
def environment():
    return Environment(
        loader=FileSystemLoader("tests/templates"),
        autoescape=select_autoescape(("html", "jinja2")),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture(scope="session")
def async_environment():
    return Environment(
        loader=FileSystemLoader("tests/templates"),
        autoescape=select_autoescape(("html", "jinja2")),
        trim_blocks=True,
        lstrip_blocks=True,
        enable_async=True,
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


@pytest.fixture(scope="session")
def flask_app():
    app = flask.Flask(__name__)
    app.config.update(
        {
            "TESTING": True,
        }
    )
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True

    @app.get("/simple_page")
    def simple_page():
        template = "simple_page.html.jinja2"
        if (
            flask.request.args.get("only_content")
            and flask.request.args["only_content"].lower() != "false"
        ):
            return flask_render_block(template, "content")
        else:
            return flask.render_template(template)

    @app.get("/nested_content")
    def nested_content():
        return flask_render_block(
            "nested_blocks_and_variables.html.jinja2",
            "content",
            name=NAME,
            lucky_number=LUCKY_NUMBER,
        )

    @app.get("/nested_inner")
    def nested_inner():
        return flask_render_block(
            "nested_blocks_and_variables.html.jinja2",
            "inner",
            lucky_number=LUCKY_NUMBER,
        )

    yield app


@pytest.fixture(scope="session")
def flask_client(flask_app):
    return flask_app.test_client()


@pytest.fixture(scope="session")
def quart_app():
    app = quart.Quart(__name__)
    app.config.from_mapping(
        {
            "TESTING": True,
        }
    )
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True

    @app.get("/simple_page")
    async def simple_page():
        template = "simple_page.html.jinja2"
        if (
            quart.request.args.get("only_content")
            and quart.request.args["only_content"].lower() != "false"
        ):
            return await quart_render_block(template, "content")
        else:
            return await quart.render_template(template)

    @app.get("/nested_content")
    async def nested_content():
        return await quart_render_block(
            "nested_blocks_and_variables.html.jinja2",
            "content",
            name=NAME,
            lucky_number=LUCKY_NUMBER,
        )

    @app.get("/nested_inner")
    async def nested_inner():
        return await quart_render_block(
            "nested_blocks_and_variables.html.jinja2",
            "inner",
            lucky_number=LUCKY_NUMBER,
        )

    yield app


@pytest.fixture(scope="session")
def quart_client(quart_app):
    return quart_app.test_client()
