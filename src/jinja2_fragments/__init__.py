from __future__ import annotations

import typing
from asyncio import AbstractEventLoop

from jinja2 import Environment


class BlockNotFoundError(Exception):
    def __init__(self, block_name: str, template_name: str, message: str | None = None):
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

    ctx = template.new_context(dict(*args, **kwargs))
    try:
        return environment.concat(  # type: ignore
            [n async for n in block_render_func(ctx)]  # type: ignore
        )
    except Exception:
        return environment.handle_exception()


async def render_blocks_async(
    environment: Environment,
    template_name: str,
    block_names: list[str],
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    """
    This works similar to :func:`render_blocks` but returns a coroutine that when
    awaited returns every rendered template block as a single string. This requires
    the environment async feature to be enabled.
    """
    if not environment.is_async:
        raise RuntimeError("The environment was not created with async mode enabled.")

    return await _render_template_blocks_async(
        environment, template_name, block_names, *args, **kwargs
    )


def render_block(
    environment: Environment,
    template_name: str,
    block_name: str,
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    """This returns the rendered template block as a string."""
    if environment.is_async:
        loop, close = _get_loop()

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

    ctx = template.new_context(dict(*args, **kwargs))
    try:
        return environment.concat(block_render_func(ctx))  # type: ignore
    except Exception:
        environment.handle_exception()


def render_blocks(
    environment: Environment,
    template_name: str,
    block_names: list[str],
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    """This returns one or more rendered template blocks as a string."""
    if environment.is_async:
        loop, close = _get_loop()

        try:
            return loop.run_until_complete(
                render_blocks_async(
                    environment, template_name, block_names, *args, **kwargs
                )
            )
        finally:
            if close:
                loop.close()

    return _render_template_blocks(
        environment, template_name, block_names, *args, **kwargs
    )


def _render_template_blocks(
    environment: Environment,
    template_name: str,
    block_names: list[str],
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    contents: list[str] = []
    template = environment.get_template(template_name)

    for block_name in block_names:
        try:
            block_render_func = template.blocks[block_name]
        except KeyError:
            raise BlockNotFoundError(block_name, template_name)

        ctx = template.new_context(dict(*args, **kwargs))
        try:
            contents.append(environment.concat(block_render_func(ctx)))  # type: ignore
        except Exception:
            environment.handle_exception()
    return "".join(contents)


async def _render_template_blocks_async(
    environment: Environment,
    template_name: str,
    block_names: list[str],
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    if not environment.is_async:
        raise RuntimeError("The environment was not created with async mode enabled.")

    contents: list[str] = []
    template = environment.get_template(template_name)

    for block_name in block_names:
        try:
            block_render_func = template.blocks[block_name]
        except KeyError:
            raise BlockNotFoundError(block_name, template_name)

        ctx = template.new_context(dict(*args, **kwargs))
        try:
            contents.append(
                environment.concat(  # type: ignore
                    [n async for n in block_render_func(ctx)]  # type: ignore
                )
            )
        except Exception:
            environment.handle_exception()
    return "".join(contents)


def _get_loop() -> tuple[AbstractEventLoop, bool]:
    import asyncio

    close = False

    try:
        return (asyncio.get_running_loop(), close)
    except RuntimeError:
        close = True
        return (asyncio.new_event_loop(), close)
