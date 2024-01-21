import pytest
from jinja2_fragments import BlockNotFoundError
from litestar.status_codes import HTTP_200_OK


class TestLitestarRenderBlock:

    def test_app(self, litestar_client):
        response = litestar_client.get("/")
        assert response.status_code == 200


    @pytest.mark.parametrize(
        "only_content, html_name",
        [
            (False, "simple_page.html"),
            (True, "simple_page_content.html"),
        ]
    )
    def test_simple_page(self, litestar_client, get_html, only_content, html_name):
        response = litestar_client.get(
            "/simple_page", params={"only_content": only_content}
        )
        print(response)

        html = get_html(html_name)
        response_text = response.text.replace('"', "").strip("\n")
        html = get_html("simple_page_content.html").strip("\n")
        assert html == response_text
        