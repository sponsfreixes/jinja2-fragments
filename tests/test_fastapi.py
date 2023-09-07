import re

import pytest

from jinja2_fragments import BlockNotFoundError


class TestFastAPIRenderBlock:
    """Tests each of the methods to make sure the html generated is
    as expected. Removed whitespace and newline characters from html compare
    to make it easier to compare output. I believe either encoding
    or OS makes for odd variances otherwise.
    """

    def test_simple_page(
        self,
        fastapi_client,
        get_html,
    ):
        response = fastapi_client.get("/simple_page")
        html = get_html("simple_page.html")
        assert html == response.text

    def test_simple_page_content(
        self,
        fastapi_client,
        get_html,
    ):
        response = fastapi_client.get("/simple_page_content")
        response_text = response.text.replace('"', "").strip("\n")
        html = get_html("simple_page_content.html").strip("\n")
        assert html == response_text

    def test_nested_content(
        self,
        fastapi_client,
        get_html,
    ):
        response = fastapi_client.get("/nested_content")
        response_text = re.sub(r"[\s\"]*", "", response.text).replace("\\n", "")
        html = get_html("nested_blocks_and_variables_content.html")
        html = re.sub(r"[\s\"]*", "", html)
        assert html == response_text

    def test_nested_inner(
        self,
        fastapi_client,
        get_html,
    ):
        response = fastapi_client.get("/nested_inner")
        response_text = re.sub(r"[\s\"]*", "", response.text).replace("\\n", "")
        html = get_html("nested_blocks_and_variables_inner.html")
        html = re.sub(r"[\s\"]*", "", html)
        assert html == response_text

    def test_nested_inner_html_response_class(
        self,
        fastapi_client,
        get_html,
    ):
        """using `response_class=HTMLResponse` should still work"""
        response = fastapi_client.get("/nested_inner_html_response_class")
        response_text = re.sub(r"[\s\"]*", "", response.text).replace("\\n", "")
        html = get_html("nested_blocks_and_variables_inner.html")
        html = re.sub(r"[\s\"]*", "", html)
        assert html == response_text

    def test_exception(self, fastapi_client):
        with pytest.raises(BlockNotFoundError) as exc:
            fastapi_client.get("/invalid_block")

        assert exc.value.block_name == "invalid_block"
        assert exc.value.template_name == "simple_page.html.jinja2"
