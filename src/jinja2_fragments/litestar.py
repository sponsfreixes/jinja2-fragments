from typing import Any, Dict, Iterable, Optional, Tuple, Union, cast

try:
    import itertools
    from mimetypes import guess_type
    from pathlib import PurePath

    from litestar import Litestar
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.connection import Request
    from litestar.contrib.htmx.response import HTMXTemplate
    from litestar.contrib.htmx.types import EventAfterType, PushUrlType, ReSwapMethod
    from litestar.datastructures import Cookie
    from litestar.enums import MediaType
    from litestar.exceptions import ImproperlyConfiguredException, LitestarException
    from litestar.response.base import ASGIResponse
    from litestar.utils.deprecation import warn_deprecation
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install litestar[jinja] before using jinja_fragments.litestar"
    ) from e

from . import render_block


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
    def __init__(
        self,
        push_url: Optional[PushUrlType] = None,
        re_swap: Optional[ReSwapMethod] = None,
        re_target: Optional[str] = None,
        trigger_event: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        after: Optional[EventAfterType] = None,
        block_name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            push_url, re_swap, re_target, trigger_event, params, after, **kwargs
        )
        self.block_name = block_name

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
