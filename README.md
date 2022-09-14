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
[Locality of Behavior](https://htmx.org/essays/locality-of-behaviour/) design principle
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

You can also use Jinja2 Fragments with FastAPI. FastAPI wraps Jinja `Environment` with the object `Jinja2Templates` and uses a `TemplateResponse` to create the HTML. Jinja2 Fragments uses the `Jinja2Templates` object to determine what response to send.

For FastAPI, you use a decorator that takes the `Jinja2Templates` object as a positional parameter, and then you can then define the `block_name` as a key/value pair.

Assuming the same template as the examples above:

```py
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="path/to/templates")

@app.get("/full_page")
@render_block(templates, magic_number=42)
async def full_page(request: Request):
    """No `block_name` given, so renders normally."""
    return templates.TemplateResponse(
        "page.html.jinja2",
        {"request": request}
    )

@app.get("/only_content")
@render_block(templates, block_name="content", magic_number=42)
async def only_content(request: Request):
    return templates.TemplateResponse(
        "page.html.jinja2",
        {"request": request}
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

From now one, every time you commit your files on this project, they will be automatically processed by the tools listed
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

