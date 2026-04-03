import pytest
from conftest import LUCKY_NUMBER, NAME

from jinja2_fragments import (
    BlockNotFoundError,
    render_block,
    render_block_async,
    render_blocks,
    render_blocks_async,
    setup_globals,
)


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


class TestTemplateGlobals:
    """Test render_block / render_blocks called from within
    templates via setup_globals.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, environment):
        setup_globals(environment)
        yield
        # Clean up globals so other tests are unaffected
        environment.globals.pop("render_block", None)
        environment.globals.pop("render_blocks", None)

    def test_render_block_global(self, environment, get_html):
        """Test single-block rendering via template global with explicit kwargs."""
        template = environment.get_template("include_block.html.jinja2")
        rendered = template.render(lucky_number=LUCKY_NUMBER)
        assert rendered == get_html("include_block.html")

    def test_render_blocks_global(self, environment, get_html):
        """Test multi-block rendering via template global."""
        template = environment.get_template("include_blocks.html.jinja2")
        rendered = template.render(name=NAME, lucky_number=LUCKY_NUMBER)
        assert rendered == get_html("include_blocks.html")

    def test_auto_context_forwarding(self, environment, get_html):
        """Test that the parent template context is automatically forwarded."""
        template = environment.get_template("include_block_auto_context.html.jinja2")
        rendered = template.render(lucky_number=LUCKY_NUMBER)
        assert rendered == get_html("include_block_auto_context.html")

    def test_kwargs_override_context(self, environment, get_html):
        """Test that kwargs passed in the template override the parent context."""
        template = environment.get_template("include_block_override.html.jinja2")
        # Parent context has lucky_number="42", but template overrides with "99"
        rendered = template.render(lucky_number=LUCKY_NUMBER)
        assert rendered == get_html("include_block_override.html")


class TestAsyncTemplateGlobals:
    """Async variants of TestTemplateGlobals."""

    @pytest.fixture(autouse=True)
    def _setup(self, async_environment):
        setup_globals(async_environment)
        yield
        async_environment.globals.pop("render_block", None)
        async_environment.globals.pop("render_blocks", None)

    @pytest.mark.asyncio
    async def test_async_render_block_global(self, async_environment, get_html):
        """Test single-block rendering via async template global."""
        template = async_environment.get_template("include_block.html.jinja2")
        rendered = await template.render_async(lucky_number=LUCKY_NUMBER)
        assert rendered == get_html("include_block.html")

    @pytest.mark.asyncio
    async def test_async_render_blocks_global(self, async_environment, get_html):
        """Test multi-block rendering via async template global."""
        template = async_environment.get_template("include_blocks.html.jinja2")
        rendered = await template.render_async(name=NAME, lucky_number=LUCKY_NUMBER)
        assert rendered == get_html("include_blocks.html")

    @pytest.mark.asyncio
    async def test_async_auto_context_forwarding(self, async_environment, get_html):
        """Test that parent context is forwarded in async mode."""
        template = async_environment.get_template(
            "include_block_auto_context.html.jinja2"
        )
        rendered = await template.render_async(lucky_number=LUCKY_NUMBER)
        assert rendered == get_html("include_block_auto_context.html")

    @pytest.mark.asyncio
    async def test_async_kwargs_override_context(self, async_environment, get_html):
        """Test that kwargs override parent context in async mode."""
        template = async_environment.get_template(
            "include_block_override.html.jinja2"
        )
        rendered = await template.render_async(lucky_number=LUCKY_NUMBER)
        assert rendered == get_html("include_block_override.html")


class TestBlockNotFoundError:
    def test_exception_message(self):
        """
        This tests the optional message kwarg in the BlockNotFoundError exception.
        """

        block, template = "the_block", "the_template"
        message = f"{block} not found in {template}, please verify the values"

        a = BlockNotFoundError(block, template)
        assert "please" not in str(a)

        b = BlockNotFoundError(block, template, message)
        assert str(b) == message


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
    def test_render_block(
        self, environment, get_html, template_name, html_name, block, params
    ):
        """Test that the render_block function works."""
        rendered = (
            render_block(environment, template_name, block, params)
            if params
            else render_block(environment, template_name, block)
        )

        html = get_html(html_name)
        assert html == rendered

    @pytest.mark.parametrize(
        "template_name, html_name, blocks, params",
        [
            ("simple_page.html.jinja2", "simple_page_content.html", ["content"], None),
            (
                "multiple_blocks.html.jinja2",
                "multiple_blocks_single_block.html",
                ["content"],
                {"name": NAME},
            ),
            (
                "multiple_blocks.html.jinja2",
                "multiple_blocks_all_blocks.html",
                ["content", "additional_content"],
                {"name": NAME, "lucky_number": LUCKY_NUMBER},
            ),
        ],
    )
    def test_render_blocks(
        self, environment, get_html, template_name, html_name, blocks, params
    ):
        """Test that the render_blocks function works."""
        rendered = (
            render_blocks(environment, template_name, blocks, params)
            if params
            else render_blocks(environment, template_name, blocks)
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
        Test that the render_block function raises the right exception when passed an
        invalid block name.
        """
        with pytest.raises(BlockNotFoundError) as exc:
            (
                render_block(environment, template_name, block, params)
                if params
                else render_block(environment, template_name, block)
            )

        assert exc.value.block_name == block
        assert exc.value.template_name == template_name


class TestAsyncRenderBlock:
    @pytest.mark.asyncio
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
    async def test_async_render_block(
        self,
        async_environment,
        get_html,
        template_name,
        html_name,
        block,
        params,
    ):
        """Test that the render_block_async function works."""
        rendered = (
            await render_block_async(async_environment, template_name, block, params)
            if params
            else await render_block_async(async_environment, template_name, block)
        )

        html = get_html(html_name)
        assert html == rendered

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "template_name, html_name, blocks, params",
        [
            ("simple_page.html.jinja2", "simple_page_content.html", ["content"], None),
            (
                "multiple_blocks.html.jinja2",
                "multiple_blocks_single_block.html",
                ["content"],
                {"name": NAME},
            ),
            (
                "multiple_blocks.html.jinja2",
                "multiple_blocks_all_blocks.html",
                ["content", "additional_content"],
                {"name": NAME, "lucky_number": LUCKY_NUMBER},
            ),
        ],
    )
    async def test_async_blocks_render(
        self,
        async_environment,
        get_html,
        template_name,
        html_name,
        blocks,
        params,
    ):
        """Test that the render_blocks_async function works."""
        rendered = (
            await render_blocks_async(async_environment, template_name, blocks, params)
            if params
            else await render_blocks_async(async_environment, template_name, blocks)
        )

        html = get_html(html_name)
        assert html == rendered
