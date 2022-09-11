import typing
from functools import wraps

try:
    from fastapi.templating import Jinja2Templates
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install FastAPI before using jinja2_fragments.fastapi"
    ) from e

import jinja2_fragments


class InvalidContextError(Exception):
    pass


def render_block(
    jinja2templates: Jinja2Templates,
    *,
    block_name: typing.Optional[str] = None,
    **context: typing.Any,
):
    """Renders the template's block from the template directory defined in
    `jinja2templates` object, with the given context.

    :param jinja2templates: the FastAPI `Jinja2Templates` object that mounts the
    app template directory
    :param block_name: the name of the block to be rendered
    :param context: the variables that should be available in the context of the block
    """

    def inner(func):
        env = jinja2templates.env  # Refers to Jinja's `Environment.get` object

        @wraps(func)
        async def response_method(*args, **kwargs):

            # extract variables from FastAPI TemplateResponse
            func_response = await func(*args, **kwargs)
            func_context = func_response.context
            template_name = func_response.template.name

            # Combine context of TemplateResponse and method kwargs
            context.update(func_context)

            # Return FastAPI TemplateResponse if no block_name given
            if not block_name:
                return jinja2templates.TemplateResponse(template_name, context)

            if isinstance(context, dict):
                return jinja2_fragments.render_block(
                    env, template_name, block_name, context
                )
            else:
                raise InvalidContextError(
                    f"Context of type {type(context)} is not valid. Expected dict."
                )

        return response_method

    return inner
