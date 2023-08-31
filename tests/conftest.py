import pathlib
import sys

import fastapi
import flask
import pytest
import quart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.testclient import TestClient

from jinja2_fragments.fastapi import Jinja2Blocks
from jinja2_fragments.flask import render_block as flask_render_block
from jinja2_fragments.quart import render_block as quart_render_block

if sys.version_info >= (3, 8):
    import sanic
    import sanic_ext

    from jinja2_fragments.sanic import render as sanic_render

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
    app.config["TESTING"] = True
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
    app.config["TESTING"] = True
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


@pytest.fixture(scope="session")
def fastapi_app():
    from fastapi.templating import Jinja2Templates

    _app = fastapi.FastAPI()

    templates: Jinja2Templates = Jinja2Blocks(
        "tests/templates",
        autoescape=select_autoescape(("html", "jinja2")),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    @_app.get("/")
    async def home():
        return {"msg": "Hello World"}

    @_app.get("/simple_page")
    async def simple_page(
        request: fastapi.requests.Request,
    ):
        """Decorator wraps around route method, but does not define a
        `block_name` paramater, so the template renders normally.
        """
        page_to_render = "simple_page.html.jinja2"
        return templates.TemplateResponse(page_to_render, {"request": request})

    @_app.get("/simple_page_content")
    async def simple_page_content(
        request: fastapi.requests.Request,
    ):
        """Decorator wraps around route method and includes `block_name`
        parameter, so will only render content within that block.
        """
        page_to_render = "simple_page.html.jinja2"
        return templates.TemplateResponse(
            page_to_render, {"request": request}, block_name="content"
        )

    @_app.get("/nested_content")
    async def nested_content(request: fastapi.requests.Request):
        """Decorator wraps around route method and includes `block_name`
        plus parameters `name` and `lucky_number` which are passed
        to the template. As a result, `content` will be rendered.
        """
        page_to_render = "nested_blocks_and_variables.html.jinja2"
        return templates.TemplateResponse(
            page_to_render,
            {"request": request, "name": NAME, "lucky_number": LUCKY_NUMBER},
            block_name="content",
        )

    @_app.get("/nested_inner")
    async def nested_inner(request: fastapi.requests.Request):
        """Decorator wraps around route method and includes `block_name`
        plus parameters `name` and `lucky_number` which are passed
        to the template. As a result, `inner` will be rendered.
        """
        page_to_render = "nested_blocks_and_variables.html.jinja2"
        return templates.TemplateResponse(
            page_to_render,
            {"request": request, "lucky_number": LUCKY_NUMBER},
            block_name="inner",
        )

    @_app.get("/invalid_block")
    async def invalid_block(request: fastapi.requests.Request):
        """Decorator wraps around route method and includes an unexisting block name."""
        return templates.TemplateResponse(
            "simple_page.html.jinja2", {"request": request}, block_name="invalid_block"
        )

    return _app


@pytest.fixture(scope="session")
def fastapi_client(fastapi_app):
    _client = TestClient(fastapi_app)
    return _client


@pytest.fixture(scope="session")
def sanic_app():
    app = sanic.Sanic(__name__)
    app.extend(config=sanic_ext.Config(templating_path_to_templates="tests/templates"))
    app.ext.environment.lstrip_blocks = True
    app.ext.environment.trim_blocks = True

    @app.get("/simple_page")
    async def simple_page(request: sanic.Request):
        template = "simple_page.html.jinja2"
        block = (
            "content" if request.args.get("only_content").lower() == "true" else None
        )
        return await sanic_render(template, block=block)

    @app.get("/nested_content")
    async def nested_content(request: sanic.Request):
        return await sanic_render(
            "nested_blocks_and_variables.html.jinja2",
            block="content",
            context={"name": NAME, "lucky_number": LUCKY_NUMBER},
        )

    @app.get("/nested_inner")
    async def nested_inner(request: sanic.Request):
        return await sanic_render(
            "nested_blocks_and_variables.html.jinja2",
            block="inner",
            context={"lucky_number": LUCKY_NUMBER},
        )

    yield app


@pytest.fixture(scope="session")
def sanic_client(sanic_app: sanic.Sanic):
    return sanic_app.test_client
