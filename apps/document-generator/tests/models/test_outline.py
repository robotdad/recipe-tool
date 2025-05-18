
from document_generator.models.outline import Resource, Section, Outline

def test_outline_dataclass():
    o = Outline(title="T", general_instruction="GI")
    assert o.title == "T"
    assert o.general_instruction == "GI"
    assert isinstance(o.resources, list)
    assert isinstance(o.sections, list)

def test_resource_dataclass():
    r = Resource(key="k", path="/p", description="d", merge_mode="concat")
    assert r.key == "k"

def test_section_dataclass():
    s = Section(title="S")
    assert s.title == "S"
    assert s.prompt is None