import warnings

import pytest
from litestar.response import Template

from jinja2_fragments.litestar import HTMXBlockTemplate


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

    @pytest.mark.parametrize(
        "route, html_name",
        [
            ("/multiple_blocks", "multiple_blocks_all_blocks.html"),
        ],
    )
    def test_multiple_blocks(self, litestar_client, get_html, route, html_name):
        response = litestar_client.get(route)

        html = get_html(html_name)
        assert html == response.text


class TestHTMXTemplateCompatibility:
    """Tests for HTMXBlockTemplate compatibility with Template signature."""

    def test_drop_in_replacement(self):
        """
        Test that HTMXBlockTemplate can be used as drop-in replacement for Template.
        """
        # Both should work identically with single positional argument
        template = Template("test_template.html")
        htmx_template = HTMXBlockTemplate("test_template.html")
        assert template.template_name == htmx_template.template_name

    def test_backward_compatibility_kwargs(self):
        """Test backward compatibility with keyword arguments."""
        htmx_template = HTMXBlockTemplate(
            template_name="test_template.html", block_name="content"
        )
        assert htmx_template.template_name == "test_template.html"
        assert htmx_template.block_name == "content"

    def test_deprecation_warning_multiple_args(self):
        """
        Test that deprecation warning is issued for multiple positional arguments.
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            HTMXBlockTemplate(
                "/some/url",
                "innerHTML",
                "#target",
                "myEvent",
                {"key": "value"},
                "settle",
                template_name="old_template.html",
            )
            assert len(w) > 0
            assert issubclass(w[0].category, DeprecationWarning)
            assert "multiple positional arguments" in str(w[0].message)

    def test_template_name_parameter_handling(self):
        """Test various ways of specifying template_name."""
        # Single positional argument should be treated as template_name
        single_arg = HTMXBlockTemplate("my_template.html")
        assert single_arg.template_name == "my_template.html"

        # Mixed usage
        mixed = HTMXBlockTemplate(
            "my_template.html", block_name="header", push_url="/test"
        )
        assert mixed.template_name == "my_template.html"
        assert mixed.block_name == "header"

    def test_no_positional_args_kwargs_only(self):
        """Test that kwargs-only usage works properly."""
        kwargs_only = HTMXBlockTemplate(
            template_name="kwargs_template.html",
            block_name="footer",
            push_url="/footer-url",
        )
        assert kwargs_only.template_name == "kwargs_template.html"
        assert kwargs_only.block_name == "footer"
