import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route
from starlette.testclient import TestClient

from jinja2_fragments import BlockNotFoundError
from jinja2_fragments.starlette import Jinja2Blocks


class TestStarletteRenderBlock:
    """Tests for native Starlette integration.

    This ensures that the Starlette module works with pure Starlette applications,
    not just FastAPI applications. The tests follow the same patterns as the FastAPI
    tests but use native Starlette constructs.
    """

    @pytest.fixture(scope="session")
    def starlette_app(self, environment):
        """Create a Starlette app for testing."""
        templates = Jinja2Blocks(env=environment)

        # Define route handlers
        async def simple_page(request: Request):
            """Basic template rendering without blocks."""
            return templates.TemplateResponse(request, "simple_page.html.jinja2")

        async def simple_page_content(request: Request):
            """Render only the content block."""
            return templates.TemplateResponse(
                request, "simple_page.html.jinja2", block_name="content"
            )

        async def nested_content(request: Request):
            """Render nested content block with context variables."""
            return templates.TemplateResponse(
                request,
                "nested_blocks_and_variables.html.jinja2",
                {"name": "Guido", "lucky_number": "42"},
                block_name="content",
            )

        async def nested_inner(request: Request):
            """Render nested inner block with context variables."""
            return templates.TemplateResponse(
                request,
                "nested_blocks_and_variables.html.jinja2",
                {"lucky_number": "42"},
                block_name="inner",
            )

        async def multiple_blocks(request: Request):
            """Render multiple blocks at once."""
            return templates.TemplateResponse(
                request,
                "multiple_blocks.html.jinja2",
                {"name": "Guido", "lucky_number": "42"},
                block_names=["content", "additional_content"],
            )

        async def invalid_block(request: Request):
            """Attempt to render a non-existent block."""
            return templates.TemplateResponse(
                request,
                "simple_page.html.jinja2",
                block_name="invalid_block",
            )

        async def invalid_block_list(request: Request):
            """Attempt to render non-existent blocks from a list."""
            return templates.TemplateResponse(
                request,
                "simple_page.html.jinja2",
                block_names=["invalid_block"],
            )

        async def deprecated_style(request: Request):
            """Test the deprecated API style with name first."""
            # This mimics the old style where name was passed first
            return templates.TemplateResponse(
                "simple_page.html.jinja2", {"request": request}
            )

        # Create routes
        routes = [
            Route("/simple_page", simple_page),
            Route("/simple_page_content", simple_page_content),
            Route("/nested_content", nested_content),
            Route("/nested_inner", nested_inner),
            Route("/multiple_blocks", multiple_blocks),
            Route("/invalid_block", invalid_block),
            Route("/invalid_block_list", invalid_block_list),
            Route("/deprecated_style", deprecated_style),
        ]

        app = Starlette(routes=routes)
        return app

    @pytest.fixture(scope="session")
    def starlette_client(self, starlette_app):
        """Create a test client for the Starlette app."""
        return TestClient(starlette_app)

    def test_simple_page(self, starlette_client, get_html):
        """Test rendering a complete page without any block restrictions."""
        response = starlette_client.get("/simple_page")
        html = get_html("simple_page.html")
        assert html == response.text

    def test_simple_page_content(self, starlette_client, get_html):
        """Test rendering only the content block."""
        response = starlette_client.get("/simple_page_content")
        html = get_html("simple_page_content.html")
        assert html == response.text

    def test_nested_content(self, starlette_client, get_html):
        """Test rendering nested content block with variables."""
        response = starlette_client.get("/nested_content")
        html = get_html("nested_blocks_and_variables_content.html")
        assert html == response.text

    def test_nested_inner(self, starlette_client, get_html):
        """Test rendering nested inner block with variables."""
        response = starlette_client.get("/nested_inner")
        html = get_html("nested_blocks_and_variables_inner.html")
        assert html == response.text

    def test_multiple_blocks(self, starlette_client, get_html):
        """Test rendering multiple blocks at once."""
        response = starlette_client.get("/multiple_blocks")
        html = get_html("multiple_blocks_all_blocks.html")
        assert html == response.text

    def test_exception_single_block(self, starlette_client):
        """Test that attempting to render a non-existent block raises an error."""
        with pytest.raises(BlockNotFoundError) as exc:
            starlette_client.get("/invalid_block")

        assert exc.value.block_name == "invalid_block"
        assert exc.value.template_name == "simple_page.html.jinja2"

    def test_exception_block_list(self, starlette_client):
        """
        Test that attempting to render non-existent blocks from a list raises an error.
        """
        with pytest.raises(BlockNotFoundError) as exc:
            starlette_client.get("/invalid_block_list")

        assert exc.value.block_name == "invalid_block"
        assert exc.value.template_name == "simple_page.html.jinja2"

    def test_deprecation_warning_old_style(self, starlette_client, get_html):
        """Test that the old-style API (name first) still works but issues a warning."""
        with pytest.warns(DeprecationWarning) as record:
            response = starlette_client.get("/deprecated_style")

        assert len(record) == 1
        warning_message = str(record[0].message)
        assert "first parameter should be the `Request` instance" in warning_message

        html = get_html("simple_page.html")
        assert html == response.text

    def test_response_status_codes(self, starlette_client):
        """Test that responses have correct status codes."""
        # Successful responses
        assert starlette_client.get("/simple_page").status_code == 200
        assert starlette_client.get("/simple_page_content").status_code == 200
        assert starlette_client.get("/nested_content").status_code == 200
        assert starlette_client.get("/nested_inner").status_code == 200
        assert starlette_client.get("/multiple_blocks").status_code == 200

    def test_response_content_type(self, starlette_client):
        """Test that responses have the correct content type."""
        response = starlette_client.get("/simple_page")
        assert response.headers["content-type"] == "text/html; charset=utf-8"

        response = starlette_client.get("/simple_page_content")
        assert response.headers["content-type"] == "text/html; charset=utf-8"


class TestStarletteCompatibility:
    """Tests to ensure compatibility with the Starlette ecosystem."""

    @pytest.fixture
    def templates(self, environment):
        """Create a Jinja2Blocks instance for testing."""
        return Jinja2Blocks(env=environment)

    def test_inherits_from_jinja2_templates(self, templates):
        """Test that Jinja2Blocks properly inherits from Starlette's Jinja2Templates."""
        from starlette.templating import Jinja2Templates

        assert isinstance(templates, Jinja2Templates)

    def test_has_standard_template_methods(self, templates):
        """Test that standard Jinja2Templates methods are available."""
        assert hasattr(templates, "get_template")
        assert hasattr(templates, "TemplateResponse")
        assert hasattr(templates, "env")

    def test_env_property_access(self, templates):
        """Test that the Jinja2 environment is accessible."""
        assert templates.env is not None
        assert hasattr(templates.env, "get_template")

    def test_template_retrieval(self, templates):
        """Test that templates can be retrieved using the standard method."""
        template = templates.get_template("simple_page.html.jinja2")
        assert template is not None
        assert template.name == "simple_page.html.jinja2"
