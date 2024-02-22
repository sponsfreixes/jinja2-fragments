# Jinja2 fragments

Jinja2 Fragments allows rendering individual blocks from
[Jinja2 templates](https://palletsprojects.com/p/jinja/). This library was created
to enable the pattern of
[Template Fragments](https://htmx.org/essays/template-fragments/) with Jinja2. It's a
great pattern if you are using [HTMX](https://htmx.org/) or some other library that
leverages fetching partial HTML.

With jinja2, if you have a template block that you want to render by itself and
as part of another page, you are forced to put that block on a separate file and then
use the [include tag](https://jinja.palletsprojects.com/en/3.1.x/templates/#include)
(or [Jinja Partials](https://github.com/mikeckennedy/jinja_partials)) on the wrapping
template.

With Jinja2 Fragments, following the
[Locality of Behavior](https://htmx.org/essays/locality-of-behaviour/) design principle,
you have a single file for both cases. See below for examples.

## Install

It's just `pip install jinja2-fragments` and you're all set. It's a pure Python package
that only needs `jinja2` (for obvious reasons!).

## Usage

This is an example of how to use the library with vanilla Jinja2. Given the template `page.html.jinja2`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>This is the title</title>
</head>
<body>
    <h1>This is a header</h1>
    {% block content %}
    <p>This is the magic number: {{ magic_number }}.</p>
    {% endblock %}
</body>
</html>
```

If you want to render only the `content` block, do:

```python
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2_fragments import render_block

environment = Environment(
    loader=FileSystemLoader("my_templates"),
    autoescape=select_autoescape(("html", "jinja2"))
)
rendered_html = render_block(
    environment, "page.html.jinja2", "content", magic_number=42
)
```

And this will only render:
```html
<p>This is the magic number: 42.</p>
```

## Usage with Flask

If you want to use Jinja2 Fragments with Flask, assuming the same template as the
example above, do:

```python
from flask import Flask, render_template
from jinja2_fragments.flask import render_block

app = Flask(__name__)

@app.get("/full_page")
def full_page():
    return render_template("page.html.jinja2", magic_number=42)


@app.get("/only_content")
def only_content():
    return render_block("page.html.jinja2", "content", magic_number=42)
```

## Usage with Quart

If you want to use Jinja2 Fragments with Quart, assuming the same template as the
example above, do:

```python
from quart import Quart, render_template
from jinja2_fragments.quart import render_block

app = Quart(__name__)

@app.get("/full_page")
async def full_page():
    return await render_template("page.html.jinja2", magic_number=42)


@app.get("/only_content")
async def only_content():
    return await render_block("page.html.jinja2", "content", magic_number=42)
```
## Usage with FastAPI

You can also use Jinja2 Fragments with FastAPI. In this case, Jinja2 Fragments has a wrapper around the FastAPI `Jinja2Templates` object called `Jinja2Blocks`.

It functions exactly the same, but allows you to include an optional parameter to the `TemplateResponse` that includes the `block_name` you want to render.

Assuming the same template as the examples above:

```py
from fastapi import FastAPI
from fastapi.requests import Request
from jinja2_fragments.fastapi import Jinja2Blocks

app = FastAPI()

templates = Jinja2Blocks(directory="path/to/templates")

@app.get("/full_page")
async def full_page(request: Request):
    return templates.TemplateResponse(
        "page.html.jinja2",
        {"request": request, "magic_number": 42}
    )

@app.get("/only_content")
async def only_content(request: Request):
    return templates.TemplateResponse(
        "page.html.jinja2",
        {"request": request, "magic_number": 42},
        block_name="content"
    )
```

## Usage with Sanic
You can use jinja2-fragments's `render()` with Sanic as a drop-in replacement of the Sanic template extension's `render()`. Your request context and environment configuration will work the same as before. You must have `sanic_ext` and `Jinja2` installed.

By default, the full page is rendered (`block=None`) unless you provide a `block` keyword argument.

```py
from sanic import Sanic, Request
import sanic_ext
from jinja2_fragments.sanic import render

app = Sanic(__name__)
app.extend(config=sanic_ext.Config(templating_path_to_templates='path/to/templates'))

@app.get('/full_page')
async def full_page(request: Request):
    return await render(
        'page.html.jinja2', 
        context={"magic_number": 42}
    )

@app.get("/only_content")
async def only_content(request: Request):
    return await render(
        'page.html.jinja2',
        block='content',
        context={"magic_number": 42}
    )
```

## Usage with Litestar
You can use Jinja2 Fragments with Litestar by using the `LitestarHTMXTemplate` class. This gives you access to the `block_name` parameter when rendering the template.

By default, the full page is rendered unless you provide a `block_name` keyword argument.

```py
from litestar.contrib.htmx.request import HTMXRequest
from litestar import get, Litestar
from litestar.response import Template

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from jinja2_fragments.litestar import HTMXBlockTemplate


@get('/full_page')
def full_page(request: HTMXRequest) -> Template:
    return HTMXBlockTemplate(
        template_name='page.html.jinja2',
        context={"magic_number": 42}
    )

@get('/only_content')
def only_content(request: HTMXRequest) -> Template:
    return HTMXBlockTemplate(
        template_name='page.html.jinja2',
        block_name='content',
        context={"magic_number": 42}
    )

app = Litestar(
    route_handlers=[full_page, only_content],
    request_class=HTMXRequest,
    template_config=TemplateConfig(
        directory="path/to/templates",
        engine=JinjaTemplateEngine,
    )
)
```


## How to collaborate

This project uses pre-commit hooks to run black, isort, pyupgrade and flake8 on each commit. To have that running
automatically on your environment, install the project with:

```shell
pip install -e .[dev]
```

And then run once:

```shell
pre-commit install
```

From now on, every time you commit your files on this project, they will be automatically processed by the tools listed
above.

## How to run tests

You can install pytest and other required dependencies with:

```shell
pip install -e .[tests]
```

And then run the test suite with:

```shell
pytest
```

