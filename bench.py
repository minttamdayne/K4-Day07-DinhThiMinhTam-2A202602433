"""Shared retrieval benchmark for the UEH scholarship corpus.

Every team member keeps this file unchanged except for the single ``CHUNKER``
assignment below. This makes chunking strategy the only experimental variable.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src import (
    EMBEDDING_PROVIDER_ENV,
    GEMINI_EMBEDDING_MODEL,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    GeminiEmbedder,
    HeadingChunker,
    LocalEmbedder,
    MockEmbedder,
    OpenAIEmbedder,
    RecursiveChunker,
    SentenceChunker,
)


DATA_DIR = Path("data/hoc-bong")
TOP_K = 3

# MỖI THÀNH VIÊN CHỈ ĐỔI ĐÚNG DÒNG NÀY.
CHUNKER = HeadingChunker(chunk_size=500)

# Các lựa chọn tham khảo để thay vào dòng trên:
# FixedSizeChunker(chunk_size=500, overlap=50)
# SentenceChunker(max_sentences_per_chunk=3)
# RecursiveChunker(chunk_size=500)
# HeadingChunker(chunk_size=500)

BENCHMARKS = [
    {
        "query": "Có bao nhiêu sinh viên nhận học bổng bán phần trong chương trình học bổng tuyển sinh Khóa 46 năm 2020?",
        "metadata_filter": None,
    },
    {
        "query": "Để được xét và nhận học bổng khuyến khích học tập cần thực hiện như thế nào?",
        "metadata_filter": {"audience": "student"},
    },
    {
        "query": "Quy trình xét và chi trả học bổng khuyến khích học tập gồm những bước nào?",
        "metadata_filter": None,
    },
    {
        "query": "Hãy liệt kê ba mức học bổng tuyển sinh Khóa 46 năm 2020 và giá trị tương ứng.",
        "metadata_filter": None,
    },
    {
        "query": "Việc chi trả học bổng khuyến khích học tập học kỳ cuối năm 2020 cho sinh viên Khóa 43, 44 và 45 dự kiến được thông báo khi nào?",
        "metadata_filter": None,
    },
]


def parse_frontmatter(raw_text: str) -> tuple[dict[str, str], str]:
    """Return simple YAML frontmatter and Markdown body separately.

    The corpus uses one-line scalar values only, so a small parser avoids adding
    PyYAML as a required dependency. Colons inside values remain intact.
    """
    lines = raw_text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, raw_text.strip()

    try:
        closing_index = next(
            index for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration as exc:
        raise ValueError("Frontmatter mở bằng '---' nhưng thiếu dòng đóng") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:closing_index]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Dòng frontmatter không hợp lệ: {line!r}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        metadata[key] = value

    body = "\n".join(lines[closing_index + 1 :]).strip()
    return metadata, body


def build_chunk_documents(data_dir: Path, chunker: Any) -> list[Document]:
    """Chunk Markdown bodies outside the store and inherit all metadata."""
    documents: list[Document] = []
    paths = sorted(data_dir.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"Không tìm thấy file .md trong {data_dir}")

    for path in paths:
        frontmatter, content = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not content:
            print(f"Bỏ qua file không có nội dung: {path}")
            continue

        chunks = chunker.chunk(content)
        for index, chunk in enumerate(chunks):
            # doc_id always identifies the original file; Document.id identifies
            # this individual chunk. Every child receives a fresh metadata copy.
            metadata = {**frontmatter, "doc_id": path.stem}
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata=metadata,
                )
            )

        print(f"{path.name}: {len(chunks)} chunk")

    return documents


def select_embedder() -> Any:
    """Select one shared embedding backend; fall back safely to mock."""
    load_dotenv(override=False)
    # The shared benchmark defaults to the real multilingual local model.
    # Set EMBEDDING_PROVIDER=mock explicitly only when the model cannot run.
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "local").strip().lower()

    try:
        if provider == "local":
            return LocalEmbedder(
                model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL)
            )
        if provider == "openai":
            return OpenAIEmbedder(
                model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL)
            )
        if provider == "gemini":
            return GeminiEmbedder(
                model_name=os.getenv("GEMINI_EMBEDDING_MODEL", GEMINI_EMBEDDING_MODEL)
            )
        if provider != "mock":
            print(f"Embedding provider không nhận diện: {provider!r}; dùng mock.")
    except Exception as exc:
        print(f"Không khởi tạo được embedding provider {provider!r}: {exc}")
        print("Chuyển sang mock embedding.")

    return MockEmbedder()


def excerpt(text: str, limit: int = 180) -> str:
    """Create a compact one-line result preview."""
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else compact[: limit - 1] + "…"


def run_benchmark() -> int:
    chunk_documents = build_chunk_documents(DATA_DIR, CHUNKER)
    if not chunk_documents:
        print("Không tạo được chunk nào.")
        return 1

    embedder = select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    store = EmbeddingStore(collection_name="scholarship_benchmark", embedding_fn=embedder)

    # Chunking has already happened above; the store receives one Document per chunk.
    store.add_documents(chunk_documents)

    print("\n=== BENCHMARK CONFIG ===")
    print(f"Chunker: {CHUNKER.__class__.__name__}")
    print(f"Embedding: {backend}")
    print(f"Tổng số chunk đã nạp: {store.get_collection_size()}")

    for query_index, benchmark in enumerate(BENCHMARKS, start=1):
        query = benchmark["query"]
        metadata_filter = benchmark["metadata_filter"]
        results = store.search_with_filter(
            query,
            top_k=TOP_K,
            metadata_filter=metadata_filter,
        )

        print(f"\n=== QUERY {query_index}/5 ===")
        print(query)
        print(f"Filter: {metadata_filter or 'không'}")
        if not results:
            print("Không có kết quả phù hợp.")
            continue

        for rank, result in enumerate(results, start=1):
            doc_id = result["metadata"].get("doc_id", "unknown")
            print(
                f"{rank}. doc_id={doc_id} | chunk_id={result['id']} "
                f"| score={result['score']:.4f}"
            )
            print(f"   {excerpt(result['content'])}")

    if isinstance(embedder, MockEmbedder):
        print("\nLưu ý: mock embedding chỉ kiểm tra luồng chạy, không đo chất lượng ngữ nghĩa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_benchmark())
