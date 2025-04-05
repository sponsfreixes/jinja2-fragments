import typing

try:
    from flask import current_app
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install flask before using jinja2_fragments.flask"
    ) from e

from . import render_block as _render_block
from . import render_blocks as _render_blocks

try:
    from blinker import Namespace
except ModuleNotFoundError:
    from flask.signals import Namespace


jinja2_fragments_signals = Namespace()

before_render_template_block = jinja2_fragments_signals.signal(
    "before-render-template-block"
)
template_block_rendered = jinja2_fragments_signals.signal("template-block-rendered")

before_render_template_blocks = jinja2_fragments_signals.signal(
    "before-render-template-blocks"
)
template_blocks_rendered = jinja2_fragments_signals.signal("template-blocks-rendered")


def render_block(template_name: str, block_name: str, **context: typing.Any) -> str:
    """
    Render a single block from a specified template.

    This function renders a specific block within a template located in the
    template folder, using the provided context variables.

    Args:
        template_name: The name of the template containing the block to render.
        block_name: The name of the block to render.
        **context: Keyword arguments representing variables to be used as the
            context for the block.

    Returns:
        The rendered string of the specified block.
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    app.update_template_context(context)
    before_render_template_block.send(
        app, template_name=template_name, block_name=block_name, context=context
    )
    rendered = _render_block(app.jinja_env, template_name, block_name, **context)
    template_block_rendered.send(
        app, template_name=template_name, block_name=block_name, context=context
    )
    return rendered


def render_blocks(
    template_name: str, block_names: list[str], **context: typing.Any
) -> str:
    """
    Render multiple blocks from a specified template.

    This function renders multiple blocks within a template located in the
    template folder, using the provided context variables.

    Args:
        template_name: The name of the template containing the blocks to render.
        block_names: A list of block names to render.
        **context: Keyword arguments representing variables to be used as the
            context for the blocks.

    Returns:
        The rendered string of the specified blocks.
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    app.update_template_context(context)
    before_render_template_blocks.send(
        app, template_name=template_name, block_names=block_names, context=context
    )
    rendered = _render_blocks(app.jinja_env, template_name, block_names, **context)
    template_blocks_rendered.send(
        app, template_name=template_name, block_names=block_names, context=context
    )
    return rendered
