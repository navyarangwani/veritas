from typing import List, Dict, Any

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = None


class NativeRecursiveTextSplitter:
    """Zero-dependency recursive text splitter for high performance and reliability."""
    def __init__(self, chunk_size: int = 3000, chunk_overlap: int = 300, separators: list = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " "]

    def split_text(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            if end < len(text):
                # Try to find a separator to split cleanly
                split_at = -1
                for sep in self.separators:
                    pos = text.rfind(sep, start + self.chunk_overlap, end)
                    if pos != -1:
                        split_at = pos + len(sep)
                        break
                
                if split_at != -1:
                    end = split_at

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            start = max(start + 1, end - self.chunk_overlap)

        return chunks


def chunk_pages(pages: list) -> list:
    """
    Splits cleaned pages into overlapping chunks for LLM context optimization.
    """
    if RecursiveCharacterTextSplitter:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " "]
        )
    else:
        splitter = NativeRecursiveTextSplitter(
            chunk_size=3000,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " "]
        )

    chunks = []
    for p in pages:
        page_chunks = splitter.split_text(p["text"])
        for chunk in page_chunks:
            if chunk.strip():
                chunks.append({
                    "page": p["page"],
                    "text": chunk.strip()
                })

    print(f"[Brain 2 — Chunker] Created {len(chunks)} chunks from {len(pages)} pages")
    return chunks
