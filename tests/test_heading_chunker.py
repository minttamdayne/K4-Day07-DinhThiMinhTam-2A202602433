import pytest

from src.chunking import HeadingChunker


def test_splits_immediately_before_each_heading():
    text = "# Quy định\nMở đầu.\n\n## Điều 1\nNội dung một.\n\n## Điều 2\nNội dung hai."

    chunks = HeadingChunker(chunk_size=200).chunk(text)

    assert chunks == [
        "# Quy định\nMở đầu.",
        "## Điều 1\nNội dung một.",
        "## Điều 2\nNội dung hai.",
    ]


def test_repeats_heading_on_every_child_of_long_section():
    heading = "## Điều kiện tham gia"
    text = f"{heading}\n" + " ".join(["điều kiện"] * 80)

    chunks = HeadingChunker(chunk_size=100).chunk(text)

    assert len(chunks) > 1
    assert all(chunk.startswith(heading + "\n") for chunk in chunks)
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_uses_recursive_splitting_for_headingless_text():
    chunks = HeadingChunker(chunk_size=20).chunk("một đoạn văn rất dài cần được chia nhỏ")

    assert len(chunks) > 1
    assert all(len(chunk) <= 20 for chunk in chunks)


def test_rejects_non_positive_chunk_size():
    with pytest.raises(ValueError):
        HeadingChunker(chunk_size=0)
