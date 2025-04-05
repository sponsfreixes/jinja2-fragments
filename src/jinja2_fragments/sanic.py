from typing import Any, Dict, Optional

from jinja2 import Environment

try:
    from sanic import Request, Sanic, SanicException
    from sanic_ext.exceptions import ExtensionNotFound
    from sanic_ext.extensions.templating import render as sanic_render
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install sanic, sanic_ext before using jinja2_fragments.sanic"
    ) from e

from . import render_block, render_block_async, render_blocks, render_blocks_async


async def render(
    template_name: str = "",
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "text/html; charset=utf-8",
    app: Optional[Sanic] = None,
    environment: Optional[Environment] = None,
    context: Optional[Dict[str, Any]] = None,
    *,
    block: Optional[str] = None,
    blocks: Optional[list[str]] = None,
) -> sanic_render.TemplateResponse:
    """
    Render a template or specific blocks within a template using Sanic.

    This function renders a complete template or specific block(s) from a given
    template. It supports both synchronous and asynchronous rendering based on
    the application's configuration. If neither `block` nor `blocks` is provided,
    the entire template is rendered.

    Args:
        template_name: The name of the template to be rendered.
        status: The HTTP status code to be returned with the response.
        headers: A dictionary of HTTP headers to include in the response.
        content_type: The content type of the HTTP response.
        app: The Sanic application instance. If omitted, attempts to locate the
            current app automatically.
        environment: The Jinja2 environment used for templating.
        context: A dictionary containing variables to be passed to the template
            or blocks for rendering.
        block: The name of the single block to render within the template.
        blocks: A list of block names to render within the template. Only one of
            `block` or `blocks` can be set.

    Returns:
        A Sanic `TemplateResponse` containing the rendered content.

    Raises:
        ValueError: If both `block` and `blocks` are set.
        SanicException: If the Sanic application cannot be determined automatically.
        ExtensionNotFound: If the templating extension is not enabled or Jinja2 is
            not installed.
    """
    if not block and not blocks:
        return await sanic_render.render(
            template_name=template_name,
            status=status,
            headers=headers,
            content_type=content_type,
            app=app,
            environment=environment,
            context=context,
        )
    if block and blocks:
        raise ValueError(
            "Set only the block or the blocks input argument, but not both."
        )

    if app is None:
        try:
            app = Sanic.get_app()
        except SanicException as e:
            raise SanicException(
                "Cannot render template because locating the Sanic application "
                "was ambiguous. Please return  render(..., app=some_app)."
            ) from e

    if environment is None:
        try:
            environment = app.ext.environment
        except AttributeError:
            raise ExtensionNotFound(
                "The Templating extension does not appear to be enabled. "
                "Perhaps jinja2 is not installed."
            )

    kwargs = context if context else {}
    kwargs["request"] = Request.get_current()

    if template_name:
        if app.config.TEMPLATING_ENABLE_ASYNC:
            if block:
                content = await render_block_async(
                    environment=environment,
                    template_name=template_name,
                    block_name=block,
                    **kwargs,
                )
            else:
                content = await render_blocks_async(
                    environment=environment,
                    template_name=template_name,
                    block_names=blocks,
                    **kwargs,
                )
        else:
            if block:
                content = render_block(
                    environment=environment,
                    template_name=template_name,
                    block_name=block,
                    **kwargs,
                )
            else:
                content = render_blocks(
                    environment=environment,
                    template_name=template_name,
                    block_names=blocks,
                    **kwargs,
                )

        return sanic_render.TemplateResponse(  # type: ignore
            content, status=status, headers=headers, content_type=content_type
        )
    else:
        return sanic_render.LazyResponse(
            kwargs, status=status, headers=headers, content_type=content_type
        )
