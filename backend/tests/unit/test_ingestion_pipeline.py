from backend.app.services.ingestion.ingestion_pipeline import (
    analyze_layout,
    route_parser,
    process_document,
)
from tempfile import NamedTemporaryFile


def test_layout_routing():
    layout = {"table_density": 0.1, "column_count": 1, "complex_layout_score": 0.2}
    assert route_parser(layout) == "docling"
    layout = {"table_density": 0.4, "column_count": 2, "complex_layout_score": 0.9}
    assert route_parser(layout) == "mineru"


def test_document_ingest_markdown_output():
    with NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        tf.write(b"Test PDF content")
        out = process_document(tf.name)
        assert "markdown_path" in out
        assert out["status"] == "EXTRACTED"
        assert out["parser_used"] in ("docling", "mineru")
