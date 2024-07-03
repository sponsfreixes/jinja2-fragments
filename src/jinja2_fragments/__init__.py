import typing

from jinja2 import Environment
from jinja2.runtime import Macro


class BlockNotFoundError(Exception):
    def __init__(
        self, block_name: str, template_name: str, message: typing.Optional[str] = None
    ):
        self.block_name = block_name
        self.template_name = template_name
        super().__init__(
            message
            or f"Block {self.block_name!r} not found in template {self.template_name!r}"
        )


async def render_block_async(
    environment: Environment,
    template_name: str,
    block_name: str,
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    """
    This works similar to :func:`render_block` but returns a coroutine that when
    awaited returns the entire rendered template block string. This requires the
    environment async feature to be enabled.
    """
    if not environment.is_async:
        raise RuntimeError("The environment was not created with async mode enabled.")

    template = environment.get_template(template_name)
    try:
        block_render_func = template.blocks[block_name]
    except KeyError:
        raise BlockNotFoundError(block_name, template_name)

    template_module = await template.make_module_async(vars=dict(*args, **kwargs))
    macros = {
        m: getattr(template_module, m)
        for m in dir(template_module)
        if isinstance(getattr(template_module, m), Macro)
    }
    ctx = template.new_context(vars=dict(*args, **kwargs), locals=macros)
    try:
        return environment.concat(  # type: ignore
            [n async for n in block_render_func(ctx)]  # type: ignore
        )
    except Exception:
        return environment.handle_exception()


def render_block(
    environment: Environment,
    template_name: str,
    block_name: str,
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    """This returns the rendered template block as a string."""
    if environment.is_async:
        import asyncio

        close = False

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            close = True

        try:
            return loop.run_until_complete(
                render_block_async(
                    environment, template_name, block_name, *args, **kwargs
                )
            )
        finally:
            if close:
                loop.close()

    template = environment.get_template(template_name)
    try:
        block_render_func = template.blocks[block_name]
    except KeyError:
        raise BlockNotFoundError(block_name, template_name)

    template_module = template.make_module(vars=dict(*args, **kwargs))
    macros = {
        m: getattr(template_module, m)
        for m in dir(template_module)
        if isinstance(getattr(template_module, m), Macro)
    }
    ctx = template.new_context(vars=dict(*args, **kwargs), locals=macros)
    try:
        return environment.concat(block_render_func(ctx))  # type: ignore
    except Exception:
        environment.handle_exception()
