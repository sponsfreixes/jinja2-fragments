from __future__ import annotations

import typing
import warnings

try:
    from starlette.background import BackgroundTask
    from starlette.requests import Request
    from starlette.responses import HTMLResponse, Response
    from starlette.templating import Jinja2Templates, _TemplateResponse
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install Starlette to use jinja2_fragments.fastapi"
    ) from e

from . import render_block, render_blocks


class InvalidContextError(Exception):
    pass


class Jinja2Blocks(Jinja2Templates):
    @typing.overload
    def TemplateResponse(
        self,
        request: Request,
        name: str,
        context: dict[str, typing.Any] | None = None,
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        *,
        block_names: list[str] = [],
    ) -> Response: ...

    @typing.overload
    def TemplateResponse(
        self,
        request: Request,
        name: str,
        context: dict[str, typing.Any] | None = None,
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        *,
        block_name: str | None = None,
    ) -> Response: ...

    @typing.overload
    def TemplateResponse(
        self,
        name: str,
        context: dict[str, typing.Any],
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        *,
        block_names: list[str] = [],
    ) -> Response:
        # Deprecated, request should be given as first argument
        ...

    @typing.overload
    def TemplateResponse(
        self,
        name: str,
        context: dict[str, typing.Any],
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        *,
        block_name: str | None = None,
    ) -> Response:
        # Deprecated, request should be given as first argument
        ...

    def TemplateResponse(self, *args: typing.Any, **kwargs: typing.Any) -> Response:
        (
            request,
            name,
            context,
            status_code,
            headers,
            media_type,
            background,
        ) = self._parse_template_response_args(*args, **kwargs)

        context.setdefault("request", request)
        for context_processor in self.context_processors:
            context.update(context_processor(request))

        template = self.get_template(name)

        block_name: str | None = kwargs.get("block_name", None)
        block_names: list[str] = kwargs.get("block_names", [])

        if block_name:
            content = render_block(
                self.env,
                name,
                block_name,
                context,
            )
            return HTMLResponse(
                content=content,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
                background=background,
            )

        if block_names:
            content = render_blocks(
                self.env,
                name,
                block_names,
                context,
            )
            return HTMLResponse(
                content=content,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
                background=background,
            )

        return _TemplateResponse(
            template,
            context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

    def _parse_template_response_args(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> tuple[
        Request,
        str,
        dict[str, typing.Any],
        int,
        typing.Mapping[str, str],
        str,
        BackgroundTask,
    ]:
        if args:
            if isinstance(
                args[0], str
            ):  # the first argument is template name (old style)
                warnings.warn(
                    "The `name` is not the first parameter anymore. "
                    "The first parameter should be the `Request` instance.\n"
                    'Replace `TemplateResponse(name, {"request": request})` by '
                    "`TemplateResponse(request, name)`.",
                    DeprecationWarning,
                    stacklevel=2,
                )

                name = args[0]
                context = args[1] if len(args) > 1 else kwargs.get("context", {})
                status_code = (
                    args[2] if len(args) > 2 else kwargs.get("status_code", 200)
                )
                headers = args[2] if len(args) > 2 else kwargs.get("headers")
                media_type = args[3] if len(args) > 3 else kwargs.get("media_type")
                background = args[4] if len(args) > 4 else kwargs.get("background")

                if "request" not in context:
                    raise ValueError('context must include a "request" key')
                request = context["request"]
            else:  # the first argument is a request instance (new style)
                request = args[0]
                name = args[1] if len(args) > 1 else kwargs["name"]
                context = args[2] if len(args) > 2 else kwargs.get("context", {})
                status_code = (
                    args[3] if len(args) > 3 else kwargs.get("status_code", 200)
                )
                headers = args[4] if len(args) > 4 else kwargs.get("headers")
                media_type = args[5] if len(args) > 5 else kwargs.get("media_type")
                background = args[6] if len(args) > 6 else kwargs.get("background")
        else:  # all arguments are kwargs
            if "request" not in kwargs:
                warnings.warn(
                    "The `TemplateResponse` now requires the `request` argument.\n"
                    'Replace `TemplateResponse(name, {"request": request})` by '
                    "`TemplateResponse(request, name)`.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                if "request" not in kwargs.get("context", {}):
                    raise ValueError('context must include a "request" key')

            context = kwargs.get("context", {})
            request = kwargs.get("request", context.get("request"))
            name = typing.cast(str, kwargs["name"])
            status_code = kwargs.get("status_code", 200)
            headers = kwargs.get("headers")
            media_type = kwargs.get("media_type")
            background = kwargs.get("background")

        return request, name, context, status_code, headers, media_type, background
