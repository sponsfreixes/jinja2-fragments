import pytest

from jinja2_fragments import BlockNotFoundError
from jinja2_fragments.flask import render_block


class TestFlaskRenderBlock:
    @pytest.mark.parametrize(
        "only_content, html_name",
        [
            (False, "simple_page.html"),
            (True, "simple_page_content.html"),
        ],
    )
    def test_simple_page(self, flask_client, get_html, only_content, html_name):
        response = flask_client.get(
            "/simple_page", query_string={"only_content": only_content}
        )

        html = get_html(html_name)
        assert html == response.text

    @pytest.mark.parametrize(
        "route, html_name",
        [
            ("/nested_content", "nested_blocks_and_variables_content.html"),
            ("/nested_inner", "nested_blocks_and_variables_inner.html"),
        ],
    )
    def test_nested_page(self, flask_client, get_html, route, html_name):
        response = flask_client.get(route)

        html = get_html(html_name)
        assert html == response.text

    def test_exception(self, flask_app):
        with pytest.raises(BlockNotFoundError) as exc:
            with flask_app.app_context():
                render_block("simple_page.html.jinja2", "invalid_block")
            assert "invalid_block" in exc.value
            assert "simple_page.html.jinja2" in exc.value
