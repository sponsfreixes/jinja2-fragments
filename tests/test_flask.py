import pytest

from jinja2_fragments import BlockNotFoundError
from jinja2_fragments.flask import (
    before_render_template_block,
    render_block,
    template_block_rendered,
)


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

        assert exc.value.block_name == "invalid_block"
        assert exc.value.template_name == "simple_page.html.jinja2"

    @pytest.mark.parametrize(
        "signal",
        [
            before_render_template_block,
            template_block_rendered,
        ],
    )
    def test_signals(app, flask_app, flask_client, signal):
        recorded = []

        def record(sender, template_name, block_name, context):
            context["testing"] = "yes please"
            recorded.append((sender, template_name, block_name, context))

        def call():
            flask_client.get("/simple_page", query_string={"only_content": "true"})

        # Test for absence of typo in signal name
        assert signal is globals().get(signal.name.replace("-", "_"))

        # No signal should be recorded
        call()
        assert len(recorded) == 0

        # Connect, record one signal
        signal.connect(record, flask_app)
        call()
        assert len(recorded) == 1

        # Disconnect, stop recording signals
        signal.disconnect(record, flask_app)
        call()
        assert len(recorded) == 1

        # Verify values sent in the signal
        sender, template_name, block_name, context = recorded[0]
        assert sender == flask_app
        assert template_name == "simple_page.html.jinja2"
        assert block_name == "content"
        assert context["testing"] == "yes please"
