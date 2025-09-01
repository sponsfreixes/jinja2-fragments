
Framework Integrations
======================

Jinja2 Fragments provides seamless integration with popular Python web frameworks. Each framework integration is designed to align with that framework's specific patterns and idioms for template rendering.

The installation of Jinja2 Fragments for all them is the same:

.. code-block:: bash

   pip install jinja2-fragments


.. contents::
   :local:
   :depth: 2

Flask Integration
=================

Jinja2 Fragments provides a Flask-specific ``render_block`` function that works as a drop-in replacement for Flask's built-in ``render_template``.

To use Jinja2 Fragments with Flask, import ``render_block`` from the ``jinja2_fragments.flask`` module:

.. code-block:: python

   from flask import Flask, render_template
   from jinja2_fragments.flask import render_block

   app = Flask(__name__)

   @app.get("/full_page")
   def full_page():
       return render_template("page.html.jinja2", magic_number=42)


   @app.get("/only_content")
   def only_content():
       return render_block("page.html.jinja2", "content", magic_number=42)

The ``render_block`` function has the same signature as Flask's ``render_template``, with an additional parameter for the block name:

.. code-block:: python

   render_block(template_name_or_list, block_name, **context)


You can also use the ``render_blocks`` function (plural) to render multiple blocks at once:

.. code-block:: python

   from jinja2_fragments.flask import render_blocks

   @app.get("/multiple_blocks")
   def multiple_blocks():
       return render_blocks("page.html.jinja2", ["header", "content"], magic_number=42)

This is useful for htmx out-of-band updates where you need to update multiple elements in a single request.

Quart Integration
=================

The Jinja2 Fragments integration with Quart is very similar to Flask but designed for async usage.

To use Jinja2 Fragments with Quart, import ``render_block`` from the ``jinja2_fragments.quart`` module:

.. code-block:: python

   from quart import Quart, render_template
   from jinja2_fragments.quart import render_block

   app = Quart(__name__)

   @app.get("/full_page")
   async def full_page():
       return await render_template("page.html.jinja2", magic_number=42)


   @app.get("/only_content")
   async def only_content():
       return await render_block("page.html.jinja2", "content", magic_number=42)

.. note::
   Note that both functions are asynchronous and need to be awaited, following Quart's async-first design philosophy.

The ``render_block`` function has the same signature as Quart's ``render_template``, with an additional parameter for the block name:

.. code-block:: python

   await render_block(template_name_or_list, block_name, **context)

Multiple blocks can be rendered with the ``render_blocks`` function, similar to the Flask integration.

FastAPI Integration
===================

Jinja2 Fragments provides a ``Jinja2Blocks`` class that extends FastAPI's ``Jinja2Templates``.

To use Jinja2 Fragments with FastAPI, import ``Jinja2Blocks`` from the ``jinja2_fragments.fastapi`` module:

.. code-block:: python

   from fastapi import FastAPI
   from fastapi.requests import Request
   from jinja2_fragments.fastapi import Jinja2Blocks

   app = FastAPI()

   templates = Jinja2Blocks(directory="path/to/templates")

   @app.get("/full_page")
   async def full_page(request: Request):
       return templates.TemplateResponse(
           request,
           "page.html.jinja2",
           {"magic_number": 42}
       )

   @app.get("/only_content")
   async def only_content(request: Request):
       return templates.TemplateResponse(
           request,
           "page.html.jinja2",
           {"magic_number": 42},
           block_name="content"
       )

The ``Jinja2Blocks`` class works exactly like FastAPI's ``Jinja2Templates``, but allows you to include an optional ``block_name`` parameter to the ``TemplateResponse`` method.

.. important::
   Remember that FastAPI's template system requires a ``request`` object in the context, as shown in the examples above.

Sanic Integration
=================

Jinja2 Fragments provides a replacement for Sanic's template rendering function.

To use Jinja2 Fragments with Sanic, import ``render`` from the ``jinja2_fragments.sanic`` module:

.. code-block:: python

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

The ``render`` function is a drop-in replacement for Sanic's template extension's ``render()``. Your request context and environment configuration will work the same as before.

.. note::
   By default, the full page is rendered (``block=None``) unless you provide a ``block`` keyword argument.

Litestar Integration
====================

Jinja2 Fragments provides integration with Litestar through the ``HTMXBlockTemplate`` class.

To use Jinja2 Fragments with Litestar, import ``HTMXBlockTemplate`` from the ``jinja2_fragments.litestar`` module:

.. important::
   ``HTMXBlockTemplate`` can be used as a drop-in replacement for Litestar's ``Template`` class. 
   However, passing multiple positional arguments to ``HTMXBlockTemplate`` is deprecated and will be 
   removed in a future version. Use ``template_name`` as the only positional argument and pass all 
   other parameters as keyword arguments.
   
   **Recommended usage**: ``HTMXBlockTemplate("template.html", block_name="content", push_url="/url")``
   
   **Deprecated usage**: ``HTMXBlockTemplate("/url", "innerHTML", "#target", template_name="template.html")``

.. code-block:: python

   try:
       # litestar>=2.13.0
       from litestar.plugins.htmx import HTMXRequest
   except ImportError:
       # litestar<2.13.0
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

.. note::
    By default, the full page is rendered unless you provide a ``block_name`` keyword argument.
