import os
from typing import List, Dict, Any

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None


def extract_pages(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Enhanced PDF extractor that returns page text along with coordinate bounding boxes.
    Maintains backward compatibility while enabling precision document grounding.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    if fitz is None:
        raise ImportError("PyMuPDF / fitz is not installed.")

    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. Plain text extraction for backward compatibility
        text = page.get_text("text")
        
        # 2. Text blocks with bounding boxes for precision auditor citation
        blocks = []
        try:
            raw_blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)
            for b in raw_blocks:
                if len(b) >= 5 and b[4].strip():
                    blocks.append({
                        "bbox": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)],
                        "text": b[4].strip(),
                        "block_id": b[5] if len(b) > 5 else 0
                    })
        except Exception as e:
            print(f"[PDF Parser] Error getting block coordinates on page {page_num + 1}: {e}")

        if text.strip() or blocks:
            pages.append({
                "page": page_num + 1,
                "text": text,
                "blocks": blocks,
                "width": round(page.rect.width, 2),
                "height": round(page.rect.height, 2)
            })

    doc.close()
    print(f"[Brain 1 — PDF Parser] Extracted {len(pages)} pages with block coordinate grounding.")
    return pages
