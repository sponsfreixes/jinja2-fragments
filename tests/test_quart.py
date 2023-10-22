import sys

import pytest

from jinja2_fragments import BlockNotFoundError
from jinja2_fragments.quart import render_block


class TestQuartRenderBlock:
    @pytest.mark.parametrize(
        "only_content, html_name",
        [
            (False, "simple_page.html"),
            (True, "simple_page_content.html"),
        ],
    )
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.version_info < (3, 8), reason="Quart requires Python 3.8.0 or higher"
    )
    async def test_simple_page(self, quart_client, get_html, only_content, html_name):
        response = await quart_client.get(
            "/simple_page", query_string={"only_content": only_content}
        )
        response_text = await response.get_data(True)

        html = get_html(html_name)
        assert html == response_text

    @pytest.mark.parametrize(
        "route, html_name",
        [
            ("/nested_content", "nested_blocks_and_variables_content.html"),
            ("/nested_inner", "nested_blocks_and_variables_inner.html"),
        ],
    )
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.version_info < (3, 8), reason="Quart requires Python 3.8.0 or higher"
    )
    async def test_nested_page(self, quart_client, get_html, route, html_name):
        response = await quart_client.get(route)
        response_text = await response.get_data(True)

        html = get_html(html_name)
        assert html == response_text

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.version_info < (3, 8), reason="Quart requires Python 3.8.0 or higher"
    )
    async def test_exception(self, quart_app):
        with pytest.raises(BlockNotFoundError) as exc:
            async with quart_app.app_context():
                await render_block("simple_page.html.jinja2", "invalid_block")

        assert exc.value.block_name == "invalid_block"
        assert exc.value.template_name == "simple_page.html.jinja2"
