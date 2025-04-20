
Basic Usage
===========

Jinja2 Fragments follows the principle of `Locality of Behavior <https://htmx.org/essays/locality-of-behaviour/>`_ by allowing you to maintain a single template file for both full page and partial rendering. This eliminates the need to create separate template files for each block you want to render independently.

Core Concepts
=============

With traditional Jinja2, if you want to render a block by itself and as part of another page, you would typically:

1. Put that block in a separate file
2. Use the `include tag <https://jinja.palletsprojects.com/en/3.1.x/templates/#include>`_ or `Jinja Partials <https://github.com/mikeckennedy/jinja_partials>`_ on the wrapping template

With Jinja2 Fragments, you can:

1. Define all blocks in a single template file
2. Render the full template when needed
3. Render specific blocks from that template when needed

This approach is especially useful when working with htmx or similar libraries that fetch partial HTML content.

Simple Block Rendering
======================

Let's start with a basic example using vanilla Jinja2. Consider the following template ``page.html.jinja2``:

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

If you want to render only the ``content`` block, you can use ``render_block`` like this:

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

This will only render:

.. code-block:: html

    <p>This is the magic number: 42.</p>

.. note::
   The ``render_block`` function takes the same arguments as Jinja2's ``render_template`` function, 
   plus an additional argument for the block name to render.

Multiple Blocks Rendering
=========================

Jinja2 Fragments also allows you to render multiple blocks at once with the ``render_blocks`` function (notice the plural):

.. code-block:: python

    from jinja2 import Environment, FileSystemLoader, select_autoescape
    from jinja2_fragments import render_blocks

    environment = Environment(
        loader=FileSystemLoader("my_templates"),
        autoescape=select_autoescape(("html", "jinja2"))
    )
    rendered_html = render_blocks(
        environment, "page.html.jinja2", ["header", "content"], magic_number=42
    )

.. note::
   Rendering multiple blocks is particularly useful for implementing `out-of-band updates <https://htmx.org/attributes/hx-swap-oob/>`_ 
   when using htmx, allowing you to update multiple parts of a page in a single request.
