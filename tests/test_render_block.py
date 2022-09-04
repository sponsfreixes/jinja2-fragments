import pytest
from conftest import LUCKY_NUMBER, NAME

from jinja2_fragments import BlockNotFoundError, render_block


class TestFullpage:
    @pytest.mark.parametrize(
        "template_name, html_name, params",
        [
            ("simple_page.html.jinja2", "simple_page.html", None),
            (
                "nested_blocks_and_variables.html.jinja2",
                "nested_blocks_and_variables_full_page.html",
                {
                    "title": "This is a title",
                    "name": NAME,
                    "lucky_number": LUCKY_NUMBER,
                },
            ),
        ],
    )
    def test_full_page(self, get_template, get_html, template_name, html_name, params):
        """
        This test is just a sanity check to confirm that full pages are rendering
        normally with jinja2.
        """
        template = get_template(template_name)

        rendered = template.render(params) if params else template.render()

        html = get_html(html_name)
        assert html == rendered


class TestRenderBlock:
    @pytest.mark.parametrize(
        "template_name, html_name, block, params",
        [
            ("simple_page.html.jinja2", "simple_page_content.html", "content", None),
            (
                "nested_blocks_and_variables.html.jinja2",
                "nested_blocks_and_variables_content.html",
                "content",
                {"name": NAME, "lucky_number": LUCKY_NUMBER},
            ),
            (
                "nested_blocks_and_variables.html.jinja2",
                "nested_blocks_and_variables_inner.html",
                "inner",
                {"lucky_number": LUCKY_NUMBER},
            ),
        ],
    )
    def test_block_render(
        self, environment, get_html, template_name, html_name, block, params
    ):
        """Test that the block_render function works."""
        rendered = (
            render_block(environment, template_name, block, params)
            if params
            else render_block(environment, template_name, block)
        )

        html = get_html(html_name)
        assert html == rendered

    @pytest.mark.parametrize(
        "template_name, html_name, block, params",
        [
            ("simple_page.html.jinja2", "simple_page_content.html", "foo", None),
            (
                "nested_blocks_and_variables.html.jinja2",
                "nested_blocks_and_variables_content.html",
                "bar",
                {"name": NAME, "lucky_number": LUCKY_NUMBER},
            ),
        ],
    )
    def test_invalid_block(
        self, environment, get_html, template_name, html_name, block, params
    ):
        """
        Test that the block_render function raises the right exception when passed an
        invalid block name.
        """
        with pytest.raises(BlockNotFoundError) as exc:
            render_block(
                environment, template_name, block, params
            ) if params else render_block(environment, template_name, block)
            assert block in exc.value
            assert template_name in exc.value
