import textwrap
import warnings
from typing import Any, Dict, Iterable, Optional, Tuple, Union, cast

try:
    import itertools
    from mimetypes import guess_type
    from pathlib import PurePath

    from litestar import Litestar
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.connection import Request
    from litestar.datastructures import Cookie
    from litestar.enums import MediaType
    from litestar.exceptions import ImproperlyConfiguredException, LitestarException
    from litestar.response.base import ASGIResponse
    from litestar.utils.deprecation import warn_deprecation

    try:
        # litestar>=2.13.0
        from litestar.plugins.htmx import (
            EventAfterType,
            HTMXTemplate,
            PushUrlType,
            ReSwapMethod,
        )
    except ImportError:
        # litestar<2.13.0
        from litestar.contrib.htmx.response import HTMXTemplate
        from litestar.contrib.htmx.types import (
            EventAfterType,
            PushUrlType,
            ReSwapMethod,
        )

except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install litestar[jinja] before using jinja_fragments.litestar"
    ) from e

from . import render_block, render_blocks


class BlockNotFoundError(LitestarException):
    def __init__(
        self, block_name: str, template_name: str, message: Optional[str] = None
    ):
        self.block_name = block_name
        self.template_name = template_name
        super().__init__(
            message
            or f"Block {self.block_name!r} not found in template {self.template_name!r}"
        )


class HTMXBlockTemplate(HTMXTemplate):
    """
    A class for rendering specific template blocks with support for HTMX.

    This class facilitates the rendering of individual template blocks or a set of
    blocks, particularly for HTMX responses. It provides methods for block-specific
    rendering and conversion of the result into an ASGI-compatible response.

    Attributes:
        block_name: The name of the single block to be rendered. Optional if
            `block_names` is provided.
        block_names: A list of block names to be rendered. Optional if `block_name`
            is provided.
    """

    def __init__(
        self,
        *args,
        push_url: Optional[PushUrlType] = None,
        re_swap: Optional[ReSwapMethod] = None,
        re_target: Optional[str] = None,
        trigger_event: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        after: Optional[EventAfterType] = None,
        block_name: Optional[str] = None,
        block_names: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        """
        Initialize the HTMXBlockTemplate instance.

        The constructor sets up the initial configuration for block rendering.
        You can specify either a single block (`block_name`) or multiple blocks
        (`block_names`), but not both at the same time.

        Args:
            template_name: The name of the template to render (when used as first
            positional arg).
            block_name: The name of a single template block to render.
            block_names: A list of template block names to render. Only one of
                `block_name` and `block_names` can be set.

        Raises:
            ValueError: If both `block_name` and `block_names` are set.
        """

        # Handle positional arguments for backward compatibility and new signature
        if len(args) > 1:
            # Multiple positional arguments - old signature, issue deprecation warning
            arg_names = [
                "push_url",
                "re_swap",
                "re_target",
                "trigger_event",
                "params",
                "after",
                "block_name",
                "block_names",
            ]
            warning_message = textwrap.dedent(
                f"""
Passing multiple positional arguments to HTMXBlockTemplate is deprecated.
In a future version, only template_name will be accepted as a positional argument,
with all other parameters as keyword arguments.
Please use:
HTMXBlockTemplate(template_name, push_url={args[0] if len(args) > 0 else None}, ...)
"""
            ).strip()

            warnings.warn(
                warning_message,
                DeprecationWarning,
                stacklevel=2,
            )

            # Map positional args to their parameter names
            for i, arg in enumerate(args):
                if i < len(arg_names):
                    if arg_names[i] == "push_url" and push_url is None:
                        push_url = arg
                    elif arg_names[i] == "re_swap" and re_swap is None:
                        re_swap = arg
                    elif arg_names[i] == "re_target" and re_target is None:
                        re_target = arg
                    elif arg_names[i] == "trigger_event" and trigger_event is None:
                        trigger_event = arg
                    elif arg_names[i] == "params" and params is None:
                        params = arg
                    elif arg_names[i] == "after" and after is None:
                        after = arg
                    elif arg_names[i] == "block_name" and block_name is None:
                        block_name = arg
                    elif arg_names[i] == "block_names" and block_names is None:
                        block_names = arg

        elif len(args) == 1:
            # Single positional argument - assume it's template_name (new behavior)
            template_name_arg = args[0]
            if "template_name" not in kwargs:
                kwargs["template_name"] = template_name_arg

        # No positional arguments - all kwargs, nothing to do

        super().__init__(
            push_url, re_swap, re_target, trigger_event, params, after, **kwargs
        )
        if block_name and block_names:
            raise ValueError(
                "Set only the block_name or the block_names input argument, but not "
                "both."
            )
        self.block_name = block_name
        self.block_names = block_names

    def to_asgi_response(
        self,
        app: Optional[Litestar],
        request: Request,
        *,
        background: Union[BackgroundTask, BackgroundTasks, None] = None,
        cookies: Optional[Iterable[Cookie]] = None,
        encoded_headers: Optional[Iterable[Tuple[bytes, bytes]]] = None,
        headers: Optional[Dict[str, str]] = None,
        is_head_response: bool = False,
        media_type: Union[MediaType, str, None] = None,
        status_code: Optional[int] = None,
        type_encoders=None,
    ) -> ASGIResponse:
        if app is not None:
            warn_deprecation(
                version="2.1",
                deprecated_name="app",
                kind="parameter",
                removal_in="3.0.0",
                alternative="request.app",
            )
        if not (template_engine := request.app.template_engine):
            raise ImproperlyConfiguredException("Template engine is not configured")

        headers = {**headers, **self.headers} if headers is not None else self.headers
        cookies = (
            self.cookies if cookies is None else itertools.chain(self.cookies, cookies)
        )

        media_type = self.media_type or media_type
        if not media_type:
            if self.template_name:
                suffixes = PurePath(self.template_name).suffixes
                for suffix in suffixes:
                    if _type := guess_type(f"name{suffix}")[0]:
                        media_type = _type
                        break
                else:
                    media_type = MediaType.TEXT
            else:
                media_type = MediaType.HTML

        context = self.create_template_context(request)

        if self.template_str is not None:
            body = template_engine.render_string(self.template_str, context)
        else:
            # cast to str b/c we know that either template_name cannot be None
            # if template_str is None
            template = template_engine.get_template(cast("str", self.template_name))

            if self.block_name:
                try:
                    _ = template.blocks[self.block_name]
                except KeyError as exc:
                    raise BlockNotFoundError(
                        self.block_name, self.template_name
                    ) from exc
                body = render_block(
                    template_engine.engine, template, self.block_name, context
                )
            elif self.block_names:
                for block_name in self.block_names:
                    try:
                        _ = template.blocks[block_name]
                    except KeyError as exc:
                        raise BlockNotFoundError(
                            block_name, self.template_name
                        ) from exc
                body = render_blocks(
                    template_engine.engine, template, self.block_names, context
                )
            else:
                body = template.render(**context).encode(self.encoding)

        return ASGIResponse(
            background=self.background or background,
            body=body,
            content_length=None,
            cookies=cookies,
            encoded_headers=encoded_headers,
            encoding=self.encoding,
            headers=headers,
            is_head_response=is_head_response,
            media_type=media_type,
            status_code=self.status_code or status_code,
        )
