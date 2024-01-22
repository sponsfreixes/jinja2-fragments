import pytest


class TestLitestarRenderBlock:
    def test_app(self, litestar_client):
        response = litestar_client.get("/")
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "only_content, html_name",
        [
            (False, "simple_page.html"),
            (True, "simple_page_content.html"),
        ],
    )
    def test_simple_page(self, litestar_client, get_html, only_content, html_name):
        response = litestar_client.get(
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
    def test_nested_page(self, litestar_client, get_html, route, html_name):
        response = litestar_client.get(route)

        html = get_html(html_name)
        assert html == response.text

    def test_exception(self, litestar_client):
        response = litestar_client.get("/invalid_block")
        msg = (response.content).decode("utf-8")

        assert response.status_code == 401
        assert (
            msg
            == '{"detail":"Validation failed for GET","extra":\
"Block \'invalid_block\' not found in template \'simple_page.html.jinja2\'"}'
        )
