import pytest
from sanic_testing.testing import SanicTestClient


class TestSanicRenderBlock:
    @pytest.mark.parametrize(
        "only_content, html_name",
        [
            (False, "simple_page.html"),
            (True, "simple_page_content.html"),
        ],
    )
    def test_simple_page(
        self, sanic_client: "SanicTestClient", get_html, only_content, html_name
    ):
        _, response = sanic_client.get(
            "/simple_page", params={"only_content": only_content}
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
    def test_nested_page(self, sanic_client, get_html, route, html_name):
        _, response = sanic_client.get(route)
        html = get_html(html_name)
        assert html == response.text
