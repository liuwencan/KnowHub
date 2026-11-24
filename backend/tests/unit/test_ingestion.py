from konwhub.ingestion.splitters import split_excel_rows, split_length, split_markdown_parent_child, split_markdown_sibling, split_smart


def test_markdown_preserves_parent_and_order() -> None:
    parts = split_markdown_parent_child("# Intro\nfirst\n## Detail\nsecond", max_length=100)
    assert [part.order for part in parts] == [0, 1, 2, 3]
    assert parts[0].metadata["is_parent"] is True
    assert parts[1].metadata["parent_heading"] == "Intro"


def test_sibling_context_and_length() -> None:
    parts = split_markdown_sibling("# A\nalpha\n# B\nbeta\n# C\ngamma", max_length=20)
    assert "sibling_indices" in parts[1].metadata
    assert split_length("abcdef", max_length=3)[1].text == "def"


def test_excel_chunk_keeps_rows_with_headers() -> None:
    parts = split_excel_rows([["name", "value"], ["a", 1], ["b", 2]], max_rows=1)
    assert len(parts) == 2
    assert "name: a" in parts[0].text
    assert parts[1].metadata["row_count"] == 1


def test_smart_split_uses_paragraphs() -> None:
    parts = split_smart("one\n\ntwo\n\nthree", max_length=7)
    assert [part.text for part in parts] == ["one", "two", "three"]
