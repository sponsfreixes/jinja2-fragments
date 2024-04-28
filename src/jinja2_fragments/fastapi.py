import typing

try:
    from starlette.background import BackgroundTask
    from starlette.responses import HTMLResponse, Response
    from starlette.templating import Jinja2Templates, _TemplateResponse
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install Starlette to use jinja2_fragments.fastapi"
    ) from e

from . import render_block


class InvalidContextError(Exception):
    pass


class Jinja2Blocks(Jinja2Templates):
    def __init__(self, directory, **env_options):
        super().__init__(directory, **env_options)

    def TemplateResponse(
        self,
        name: str,
        context: typing.Dict[str, typing.Any],
        status_code: int = 200,
        headers: typing.Optional[typing.Mapping[str, str]] = None,
        media_type: typing.Optional[str] = None,
        background: typing.Optional[BackgroundTask] = None,
        *,
        block_name: typing.Optional[str] = None,
    ) -> Response:
        if "request" not in context:
            raise ValueError('context must include a "request" key')
        template = self.get_template(name)

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
        return _TemplateResponse(
            template,
            context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )
