from __future__ import annotations

import pathlib

import fastapi
import flask
import litestar
import pytest
import quart
import sanic
import sanic_ext
from jinja2 import Environment, FileSystemLoader, select_autoescape
from litestar.testing import TestClient as LitestarTestClient
from starlette.responses import HTMLResponse
from starlette.testclient import TestClient

from jinja2_fragments.fastapi import Jinja2Blocks
from jinja2_fragments.flask import render_block as flask_render_block
from jinja2_fragments.flask import render_blocks as flask_render_blocks
from jinja2_fragments.quart import render_block as quart_render_block
from jinja2_fragments.quart import render_blocks as quart_render_blocks
from jinja2_fragments.sanic import render as sanic_render

# fmt: off
# Needed for type hints because we are using `from __future__ import annotations`
# to support Python <3.10. See
# https://stackoverflow.com/questions/66734640/any-downsides-to-using-from-future-import-annotations-everywhere
# for shortcomings of using the annotations import,
from litestar.contrib.htmx.request import HTMXRequest  # noqa isort: skip
from litestar.response import Template  # noqa isort: skip
# fmt: on

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

    @app.get("/multiple_blocks")
    def multiple_blocks():
        return flask_render_blocks(
            "multiple_blocks.html.jinja2",
            ["content", "additional_content"],
            name=NAME,
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

    @app.get("/multiple_blocks")
    def multiple_blocks():
        return quart_render_blocks(
            "multiple_blocks.html.jinja2",
            ["content", "additional_content"],
            name=NAME,
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

    @_app.get("/nested_inner_html_response_class", response_class=HTMLResponse)
    async def nested_inner_html_response_class(request: fastapi.requests.Request):
        """Decorator wraps around route method with
        `response_class=HTMLResponse` and includes `block_name`
        plus parameters `name` and `lucky_number` which are passed
        to the template. As a result, `inner` will be rendered.
        """
        page_to_render = "nested_blocks_and_variables.html.jinja2"
        return templates.TemplateResponse(
            page_to_render,
            {"request": request, "lucky_number": LUCKY_NUMBER},
            block_name="inner",
        )

    @_app.get("/multiple_blocks")
    async def multiple_blocks(
        request: fastapi.requests.Request,
    ):
        """Decorator wraps around route method and includes `block_names`
        parameter, so it will render content within all given blocks.
        """
        page_to_render = "multiple_blocks.html.jinja2"
        return templates.TemplateResponse(
            page_to_render,
            {"request": request, "name": NAME, "lucky_number": LUCKY_NUMBER},
            block_names=["content", "additional_content"],
        )

    @_app.get("/invalid_block")
    async def invalid_block(request: fastapi.requests.Request):
        """Decorator wraps around route method and includes an unexisting block name."""
        return templates.TemplateResponse(
            "simple_page.html.jinja2", {"request": request}, block_name="invalid_block"
        )

    @_app.get("/invalid_block_list")
    async def invalid_block_list(request: fastapi.requests.Request):
        """Decorator wraps around route method and includes an unexisting block name
        passed as a list argument."""
        return templates.TemplateResponse(
            "simple_page.html.jinja2",
            {"request": request},
            block_names=["invalid_block"],
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

    @app.get("/multiple_blocks")
    async def multiple_blocks(request: sanic.Request):
        return await sanic_render(
            "multiple_blocks.html.jinja2",
            blocks=["content", "additional_content"],
            context={"name": NAME, "lucky_number": LUCKY_NUMBER},
        )

    yield app


@pytest.fixture(scope="session")
def sanic_client(sanic_app: sanic.Sanic):
    return sanic_app.test_client


@pytest.fixture(scope="session")
def litestar_app():
    from pathlib import Path

    from litestar.contrib.htmx.request import HTMXRequest  # noqa
    from litestar.contrib.jinja import JinjaTemplateEngine
    from litestar.response import Response, Template  # noqa
    from litestar.template.config import TemplateConfig

    from jinja2_fragments.litestar import BlockNotFoundError, HTMXBlockTemplate

    jinja_env = Environment(
        loader=FileSystemLoader("tests/templates"),
        autoescape=select_autoescape(("html", "jinja2")),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template_config = TemplateConfig(
        directory=Path("tests/templates"),
        engine=JinjaTemplateEngine.from_environment(jinja_env),
    )

    def notfound_handler(
        request: HTMXRequest, exception: BlockNotFoundError
    ) -> Response:
        return Response(
            {
                "detail": f"Validation failed for {request.method}",
                "extra": exception.detail,
            },
            status_code=401,
        )

    @litestar.get(path="/", sync_to_thread=False)
    def get_form(request: HTMXRequest) -> Template:
        context = {"magic_number": 45, "name": "Bob"}
        htmx = request.htmx
        if htmx:
            context = {"magic_number": 42, "name": "Bob"}
            print(htmx.current_url)
            print("we are here")
            return HTMXBlockTemplate(
                template_name="simple_page.html.jinja2",
                context=context,
                block_name="content",
            )
        else:
            return HTMXBlockTemplate(
                template_name="simple_page.html.jinja2", context=context
            )

    @litestar.get(path="/simple_page", sync_to_thread=False)
    def simple_page(request: HTMXRequest) -> Template:
        template = "simple_page.html.jinja2"
        if (
            request.query_params.get("only_content")
            and request.query_params["only_content"].lower() != "false"
        ):
            return HTMXBlockTemplate(template_name=template, block_name="content")
        else:
            return HTMXBlockTemplate(
                template_name=template,
                context={"name": NAME, "lucky_number": LUCKY_NUMBER},
            )

    @litestar.get(path="/nested_content", sync_to_thread=False)
    def nested_content(request: HTMXRequest) -> Template:
        return HTMXBlockTemplate(
            template_name="nested_blocks_and_variables.html.jinja2",
            context={"name": NAME, "lucky_number": LUCKY_NUMBER},
            block_name="content",
        )

    @litestar.get(path="/nested_inner", sync_to_thread=False)
    def nested_inner(request: HTMXRequest) -> Template:
        return HTMXBlockTemplate(
            template_name="nested_blocks_and_variables.html.jinja2",
            context={"lucky_number": LUCKY_NUMBER},
            block_name="inner",
        )

    @litestar.get(path="/invalid_block", sync_to_thread=False)
    def invalid_block(request: HTMXRequest) -> Template:
        return HTMXBlockTemplate(
            template_name="simple_page.html.jinja2",
            context={"name": NAME, "lucky_number": LUCKY_NUMBER},
            block_name="invalid_block",
        )

    app = litestar.Litestar(
        route_handlers=[
            get_form,
            simple_page,
            nested_content,
            nested_inner,
            invalid_block,
        ],
        debug=True,
        request_class=HTMXRequest,
        template_config=template_config,
        exception_handlers={BlockNotFoundError: notfound_handler},
    )

    yield app


@pytest.fixture(scope="session")
def litestar_client(litestar_app):
    client = LitestarTestClient(app=litestar_app)
    return client
