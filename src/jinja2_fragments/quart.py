import typing

try:
    from quart import current_app
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install quart before using jinja2_fragments.quart"
    ) from e

from quart.signals import AsyncNamespace

import jinja2_fragments

jinja2_fragments_signals = AsyncNamespace()
before_render_template_block = jinja2_fragments_signals.signal(
    "before-render-template-block"
)
template_block_rendered = jinja2_fragments_signals.signal("template-bock-rendered")


async def render_block(
    template_name: str, block_name: str, **context: typing.Any
) -> str:
    """Renders a template's block from the template folder with the given context.

    :param template_name: the name of the template where to find the block to be
        rendered
    :param block_name: the name of the block to be rendered
    :param context: the variables that should be available in the context of the block
    """
    app = current_app  # type: ignore[attr-defined]
    await app.update_template_context(context)
    await before_render_template_block.send(
        app, template_name=template_name, block_name=block_name, context=context
    )
    rendered = await jinja2_fragments.render_block_async(
        app.jinja_env, template_name, block_name, **context
    )
    await template_block_rendered.send(
        app, template_name=template_name, block_name=block_name, context=context
    )
    return rendered
