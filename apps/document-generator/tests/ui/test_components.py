from document_generator_app.ui.components import resource_entry, section_entry


def test_resource_entry_returns_list():
    comps = resource_entry()
    assert isinstance(comps, list)


def test_section_entry_returns_list():
    comps = section_entry()
    assert isinstance(comps, list)
