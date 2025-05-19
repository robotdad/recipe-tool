from document_generator.ui.editor import build_editor


def test_build_editor_returns_blocks():
    blocks = build_editor()
    assert hasattr(blocks, "launch")
