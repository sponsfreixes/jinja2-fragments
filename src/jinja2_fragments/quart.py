import typing

try:
    from quart import current_app
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install quart before using jinja2_fragments.quart"
    ) from e

try:
    # Quart >= 0.19.0
    from quart.signals import Namespace

    CUSTOM_SIGNAL = False
except ImportError:
    # Quart < 0.19.0
    from quart.signals import AsyncNamespace as Namespace

    CUSTOM_SIGNAL = True


from . import render_block_async, render_blocks_async

jinja2_fragments_signals = Namespace()

before_render_template_block = jinja2_fragments_signals.signal(
    "before-render-template-block"
)
template_block_rendered = jinja2_fragments_signals.signal("template-block-rendered")

before_render_template_blocks = jinja2_fragments_signals.signal(
    "before-render-template-blocks"
)
template_blocks_rendered = jinja2_fragments_signals.signal("template-blocks-rendered")


async def render_block(
    template_name: str, block_name: str, **context: typing.Any
) -> str:
    """
    Render a single block from a specified template asynchronously.

    This function renders a specific block within a template located in the
    template folder, using the provided context variables. It leverages Quart's
    asynchronous functionality.

    Args:
        template_name: The name of the template containing the block to render.
        block_name: The name of the block to render.
        **context: Keyword arguments representing variables to be used as the
            context for the block.

    Returns:
        The rendered string of the specified block.
    """
    app = current_app  # type: ignore[attr-defined]
    await app.update_template_context(context)
    if CUSTOM_SIGNAL:
        await before_render_template_block.send(
            app, template_name=template_name, block_name=block_name, context=context
        )
    else:
        await before_render_template_block.send_async(
            app,
            _sync_wrapper=app.ensure_async,
            template_name=template_name,
            block_name=block_name,
            context=context,
        )
    rendered = await render_block_async(
        app.jinja_env, template_name, block_name, **context
    )
    if CUSTOM_SIGNAL:
        await template_block_rendered.send(
            app, template_name=template_name, block_name=block_name, context=context
        )
    else:
        await template_block_rendered.send_async(
            app,
            _sync_wrapper=app.ensure_async,
            template_name=template_name,
            block_name=block_name,
            context=context,
        )
    return rendered


async def render_blocks(
    template_name: str, block_names: list[str], **context: typing.Any
) -> str:
    """
    Render multiple blocks from a specified template asynchronously.

    This function renders multiple blocks within a template located in the
    template folder, using the provided context variables. It leverages Quart's
    asynchronous functionality.

    Args:
        template_name: The name of the template containing the blocks to render.
        block_names: A list of block names to render.
        **context: Keyword arguments representing variables to be used as the
            context for the blocks.

    Returns:
        The rendered string of the specified blocks.
    """
    app = current_app  # type: ignore[attr-defined]
    await app.update_template_context(context)
    if CUSTOM_SIGNAL:
        await before_render_template_blocks.send(
            app, template_name=template_name, block_names=block_names, context=context
        )
    else:
        await before_render_template_blocks.send_async(
            app,
            _sync_wrapper=app.ensure_async,
            template_name=template_name,
            block_names=block_names,
            context=context,
        )
    rendered = await render_blocks_async(
        app.jinja_env, template_name, block_names, **context
    )
    if CUSTOM_SIGNAL:
        await template_blocks_rendered.send(
            app, template_name=template_name, block_names=block_names, context=context
        )
    else:
        await template_blocks_rendered.send_async(
            app,
            _sync_wrapper=app.ensure_async,
            template_name=template_name,
            block_names=block_names,
            context=context,
        )
    return rendered
