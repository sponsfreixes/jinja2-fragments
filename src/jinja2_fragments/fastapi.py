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
        """
        Generate an HTTP response with a rendered template.

        This method renders a specified template with the given context and produces
        an HTTP response that includes the rendered content, as well as an appropriate
        status code.

        Args:
            template_name: The name of the template file to be rendered.
            context: A dictionary of variables to be made available in the template.
            status_code: The HTTP status code for the response. Defaults to 200 (OK).

        Returns:
            A FastAPI-compatible HTTP `Response` object containing the rendered
            template.

        Raises:
            InvalidContextError: If the provided context is invalid or malformed.
            TemplateNotFound: If the specified template cannot be located.
        """

        (
            request,
            name,
            context,
            status_code,
            headers,
            media_type,
            background,
        ) = self._parse_template_response_args(*args, **kwargs)

        if not isinstance(context, dict):
            raise TypeError("context must be a dict")
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
        typing.Mapping[str, str] | None,
        str | None,
        BackgroundTask | None,
    ]:
        """Parse arguments for the `TemplateResponse` method.

        Since the order of positional arguments has changed in starlette 0.29.0,
        parsing the argument list has become more complex. To remain backwards
        compatible, the scheme (< 0.29 or >= 0.29) must be detected.
        """

        if args and isinstance(args[0], Request) or "request" in kwargs:
            return self._parse_new_style_response_args(*args, **kwargs)

        warnings.warn(
            "The `name` is not the first parameter anymore. "
            "The first parameter should be the `Request` instance.\n"
            'Replace `TemplateResponse(name, {"request": request})` by '
            "`TemplateResponse(request, name)`.",
            DeprecationWarning,
            stacklevel=3,
        )
        return self._parse_old_style_response_args(*args, **kwargs)

    @staticmethod
    def _parse_old_style_response_args(
        name: str,
        context: dict[str, typing.Any],
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        **extra_kwargs: typing.Any,
    ) -> tuple[
        Request,
        str,
        dict[str, typing.Any],
        int,
        typing.Mapping[str, str] | None,
        str | None,
        BackgroundTask | None,
    ]:
        if "request" not in context:
            raise ValueError('context must include a "request" key')
        request = context["request"]

        return request, name, context, status_code, headers, media_type, background

    @staticmethod
    def _parse_new_style_response_args(
        request: Request,
        name: str,
        context: dict[str, typing.Any] = {},
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        **extra_kwargs: typing.Any,
    ) -> tuple[
        Request,
        str,
        dict[str, typing.Any],
        int,
        typing.Mapping[str, str] | None,
        str | None,
        BackgroundTask | None,
    ]:
        return request, name, context, status_code, headers, media_type, background
