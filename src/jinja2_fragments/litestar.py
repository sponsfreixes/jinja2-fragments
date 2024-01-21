from typing import Optional, Any, Iterable, cast

try:
    from litestar.contrib.htmx.response import HTMXTemplate
    from litestar import Litestar
    from litestar.response.base import ASGIResponse
    import itertools
    from mimetypes import guess_type
    from pathlib import PurePath
    from litestar.utils.deprecation import warn_deprecation
    from litestar.contrib.htmx.types import PushUrlType, EventAfterType, ReSwapMethod
    from litestar.enums import MediaType
    from litestar.exceptions import ImproperlyConfiguredException
    from litestar.connection import Request
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.datastructures import Cookie
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
    "Install litestar[jinja] before using jinja_fragments.litestar"
) from e

from . import render_block


class LitestarHTMXTemplate(HTMXTemplate):
    def __init__(
        self,
        push_url: PushUrlType | None = None,
        re_swap: ReSwapMethod | None = None,
        re_target: str | None = None,
        trigger_event: str | None = None,
        params: dict[str, Any] | None = None,
        after: EventAfterType | None = None,
        block_name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            push_url,
            re_swap,
            re_target,
            trigger_event,
            params,
            after,
            **kwargs)
        self.block_name = block_name


    def to_asgi_response(
        self,
        app: Litestar | None,
        request: Request,
        *,
        background: BackgroundTask | BackgroundTasks | None = None,
        cookies: Iterable[Cookie] | None = None,
        encoded_headers: Iterable[tuple[bytes, bytes]] | None = None,
        headers: dict[str, str] | None = None,
        is_head_response: bool = False,
        media_type: MediaType | str | None = None,
        status_code: int | None = None,
        type_encoders = None,
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
        cookies = self.cookies if cookies is None else itertools.chain(self.cookies, cookies)

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
            # cast to str b/c we know that either template_name cannot be None if template_str is None
            template = template_engine.get_template(cast("str", self.template_name))
            if self.block_name:
                body = render_block(template_engine.engine, template, self.block_name, context)
                print(body)
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