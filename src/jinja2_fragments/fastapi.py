from __future__ import annotations

import typing

try:
    from starlette.background import BackgroundTask
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
    def __init__(self, directory, **env_options):
        super().__init__(directory, **env_options)

    @typing.overload  # type: ignore
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
        ...

    def TemplateResponse(
        self,
        name: str,
        context: dict[str, typing.Any],
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        **kwargs: typing.Any,
    ) -> Response:
        if "request" not in context:
            raise ValueError('context must include a "request" key')
        template = self.get_template(name)

        block_name = kwargs.get("block_name", None)
        block_names = kwargs.get("block_names", [])

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
