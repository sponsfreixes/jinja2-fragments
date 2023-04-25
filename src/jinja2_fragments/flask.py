import typing

try:
    from flask import current_app
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install flask before using jinja2_fragments.flask"
    ) from e

from . import render_block as _render_block

try:
    from blinker import Namespace
except ModuleNotFoundError:
    from flask.signals import Namespace


jinja2_fragments_signals = Namespace()
before_render_template_block = jinja2_fragments_signals.signal(
    "before-render-template-block"
)
template_block_rendered = jinja2_fragments_signals.signal("template-block-rendered")


def render_block(template_name: str, block_name: str, **context: typing.Any) -> str:
    """Renders a template's block from the template folder with the given context.

    :param template_name: the name of the template where to find the block to be
        rendered
    :param block_name: the name of the block to be rendered
    :param context: the variables that should be available in the context of the block
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
