===============================
Jinja2 Fragments Documentation
===============================


.. image:: https://img.shields.io/pypi/v/jinja2-fragments
   :alt: PyPI - Version

.. image:: https://img.shields.io/pypi/dm/jinja2-fragments
   :alt: PyPI - Downloads

.. image:: https://img.shields.io/github/license/sponsfreixes/jinja2-fragments
   :alt: License

Overview
========

**jinja2-fragments** is a Python library that enhances `Jinja2 templates <https://palletsprojects.com/p/jinja/>`_
by allowing you to render individual blocks from templates. This is particularly useful for modern web applications
using `htmx <https://htmx.org/>`_ or other JavaScript-based partial page update techniques, where you often need to
render just a section of a page rather than the entire page.

This library was created to enable the pattern of `Template Fragments <https://htmx.org/essays/template-fragments/>`_
with Jinja2, making it easier to maintain a single source template file for both full page and partial rendering.

Key Features
------------

* Render specific blocks from Jinja2 templates
* Support for rendering multiple blocks at once
* Support for both synchronous and asynchronous rendering
* Integrations with popular Python web frameworks:
  
  * Flask
  * FastAPI
  * Quart (async Flask)
  * Sanic
  * Litestar

* Natural syntax that follows each framework's conventions
* Perfect for use with htmx for dynamic UI updates

Quick Start
===========

Installation
------------

Install ``jinja2-fragments`` with pip:

.. code-block:: bash

   pip install jinja2-fragments

The above also works for framework-specific installations.

Basic Usage
-----------

Here's a simple example with vanilla Jinja2. Given the following template:

.. code-block:: html

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

You can render only the ``content`` block with:

.. code-block:: python

    from jinja2 import Environment, FileSystemLoader, select_autoescape
    from jinja2_fragments import render_block

    environment = Environment(
        loader=FileSystemLoader("my_templates"),
        autoescape=select_autoescape(("html", "jinja2"))
    )
    rendered_html = render_block(
        environment, "page.html.jinja2", "content", magic_number=42
    )

Which will render:


.. code-block:: html

    <p>This is the magic number: 42.</p>


Framework Examples
------------------

Each framework has its own integration patterns:

.. tabs::

   .. tab:: Flask

      .. code-block:: python

         from flask import Flask, render_template
         from jinja2_fragments.flask import render_block

         app = Flask(__name__)

         @app.route('/profile/<username>')
         def profile(username):
             return render_template('profile.html.jinja2', username=username)

         @app.route('/profile/<username>/details')
         def profile_details(username):
             return render_block('profile.html.jinja2', 'details', username=username)

   .. tab:: Quart

      .. code-block:: python

         from quart import Quart, render_template
         from jinja2_fragments.quart import render_block

         app = Quart(__name__)

         @app.route('/profile/<username>')
         async def profile(username):
             return await render_template('profile.html.jinja2', username=username)

         @app.route('/profile/<username>/details')
         async def profile_details(username):
             return await render_block('profile.html.jinja2', 'details', username=username)

   .. tab:: FastAPI

      .. code-block:: python

         from fastapi import FastAPI, Request
         from jinja2_fragments.fastapi import Jinja2Blocks

         app = FastAPI()
         templates = Jinja2Blocks(directory="templates")

         @app.get('/profile/{username}')
         def profile(request: Request, username: str):
             return templates.TemplateResponse(
                'profile.html.jinja2',
                {"request": request, "username": username}
                )

         @app.get('/profile/{username}/details')
         def profile_details(request: Request, username: str):
             return templates.TemplateResponse(
                 'profile.html.jinja2',
                 {"request": request, "username": username},
                 block_name="details"
             )

   .. tab:: Sanic

      .. code-block:: python

        from sanic import Sanic, Request
        import sanic_ext
        from jinja2_fragments.sanic import render

        app = Sanic(__name__)
        app.extend(config=sanic_ext.Config(templating_path_to_templates='path/to/templates'))

        @app.route('/profile/<username>')
        async def profile(request: Request, username: str):
            return await render('profile.html.jinja2', context={"username": username}
            )

        @app.route('/profile/<username>/details')
        async def profile_details(request: Request, username: str):
            return await render(
                'profile.html.jinja2', block='content', context={"username": username}
            )

   .. tab:: Litestar

      .. code-block:: python

        from litestar.contrib.htmx.request import HTMXRequest
        from litestar import get, Litestar
        from litestar.response import Template

        from litestar.contrib.jinja import JinjaTemplateEngine
        from litestar.template.config import TemplateConfig
        from jinja2_fragments.litestar import HTMXBlockTemplate


        @get('/profile/{username:str}')
        def profile(request: HTMXRequest, username: str) -> Template:
            return HTMXBlockTemplate(
                template_name='profile.html.jinja2',
                context={"username": username}
            )

        @get('/profile/{username:str}/details')
        def profile_details(request: HTMXRequest, username:str) -> Template:
            return HTMXBlockTemplate(
                template_name='profile.html.jinja2',
                block_name='details',
                context={"username": username}
            )

        app = Litestar(
            route_handlers=[profile, profile_details],
            request_class=HTMXRequest,
            template_config=TemplateConfig(
                directory="path/to/templates", engine=JinjaTemplateEngine,
            )
        )


.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   basic_usage
   framework_integrations

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api/core
   api/flask
   api/quart
   api/fastapi
   api/sanic
   api/litestar

.. toctree::
   :maxdepth: 1
   :caption: Development

   development
   changelog


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
