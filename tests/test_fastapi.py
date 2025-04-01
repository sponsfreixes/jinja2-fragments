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
        html = get_html("simple_page_content.html")
        assert html == response.text

    def test_nested_content(
        self,
        fastapi_client,
        get_html,
    ):
        response = fastapi_client.get("/nested_content")
        html = get_html("nested_blocks_and_variables_content.html")
        assert html == response.text

    def test_nested_inner(
        self,
        fastapi_client,
        get_html,
    ):
        response = fastapi_client.get("/nested_inner")
        html = get_html("nested_blocks_and_variables_inner.html")
        assert html == response.text

    def test_multiple_blocks(
        self,
        fastapi_client,
        get_html,
    ):
        response = fastapi_client.get("/multiple_blocks")
        html = get_html("multiple_blocks_all_blocks.html")
        assert html == response.text

    def test_nested_inner_html_response_class(
        self,
        fastapi_client,
        get_html,
    ):
        """using `response_class=HTMLResponse` should still work"""
        response = fastapi_client.get("/nested_inner_html_response_class")
        html = get_html("nested_blocks_and_variables_inner.html")
        assert html == response.text

    def test_exception(self, fastapi_client):
        with pytest.raises(BlockNotFoundError) as exc:
            fastapi_client.get("/invalid_block")

        assert exc.value.block_name == "invalid_block"
        assert exc.value.template_name == "simple_page.html.jinja2"

    def test_exception_block_list(self, fastapi_client):
        with pytest.raises(BlockNotFoundError) as exc:
            fastapi_client.get("/invalid_block_list")

        assert exc.value.block_name == "invalid_block"
        assert exc.value.template_name == "simple_page.html.jinja2"

    def test_deprecation_warning_simple_page(self, fastapi_client, get_html):
        with pytest.warns(DeprecationWarning) as record:
            response = fastapi_client.get(
                "/simple_page", params={"pass_request_via_context": True}
            )

        assert len(record) == 1
        assert "conftest.py" in record[0].filename

        html = get_html("simple_page.html")
        assert html == response.text

    def test_deprecation_warning_simple_page_content(self, fastapi_client, get_html):
        with pytest.warns(DeprecationWarning) as record:
            response = fastapi_client.get(
                "/simple_page_content", params={"pass_request_via_context": True}
            )

        assert len(record) == 1
        assert "conftest.py" in record[0].filename

        html = get_html("simple_page_content.html")
        assert html == response.text
