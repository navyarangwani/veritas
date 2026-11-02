import os
import re
from typing import List, Dict, Any, Optional

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None


ESG_TABLE_KEYWORDS = [
    "scope 1", "scope 2", "scope 3", "ghg", "emissions", "carbon", "energy",
    "renewable", "mwh", "tco2", "tco2e", "water", "waste", "diversity",
    "workforce", "gender", "turnover", "brsr", "gri", "esrs", "intensity"
]


def is_esg_relevant_table(table_data: List[List[Any]]) -> bool:
    """Check if an extracted table contains ESG-relevant disclosures."""
    if not table_data or len(table_data) < 2:
        return False
    
    flat_text = " ".join([
        str(cell).lower() 
        for row in table_data if row
        for cell in row if cell is not None
    ])
    
    match_count = sum(1 for kw in ESG_TABLE_KEYWORDS if kw in flat_text)
    return match_count >= 2


def extract_tables_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Layout-aware extraction of structured tables with bounding boxes and metadata.
    Enables forensic table auditing and arithmetic verification.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")
    
    extracted_tables = []
    
    if pdfplumber is None:
        print("[Table Parser] pdfplumber not installed; falling back to text parsing.")
        return extracted_tables

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_num = page_idx + 1
                try:
                    tables = page.find_tables()
                    for t_idx, table_obj in enumerate(tables):
                        raw_table = table_obj.extract()
                        if not raw_table or len(raw_table) < 2:
                            continue
                        
                        if is_esg_relevant_table(raw_table):
                            bbox = list(table_obj.bbox)  # [x0, top, x1, bottom]
                            
                            # Clean headers and rows
                            headers = [str(c).strip() if c is not None else "" for c in raw_table[0]]
                            rows = []
                            for row in raw_table[1:]:
                                cleaned_row = [str(c).strip() if c is not None else "" for c in row]
                                if any(cleaned_row):
                                    rows.append(cleaned_row)
                            
                            # Extract page footnotes if any
                            footnotes = extract_page_footnotes(page, bbox)
                            
                            table_id = f"TBL-P{page_num}-{t_idx+1}"
                            extracted_tables.append({
                                "table_id": table_id,
                                "page": page_num,
                                "bbox": bbox,
                                "headers": headers,
                                "rows": rows,
                                "raw_data": raw_table,
                                "footnotes": footnotes,
                                "category": categorize_table(headers, rows)
                            })
                except Exception as page_err:
                    print(f"[Table Parser] Error parsing page {page_num}: {page_err}")
                    continue
    except Exception as e:
        print(f"[Table Parser] Failed to extract tables: {e}")

    print(f"[Brain 1 — Table Parser] Extracted {len(extracted_tables)} ESG-relevant tables.")
    return extracted_tables


def extract_page_footnotes(page, table_bbox: List[float]) -> List[str]:
    """Extract footnote text located underneath the table."""
    try:
        # Table bbox: [x0, top, x1, bottom]
        bottom_y = table_bbox[3]
        page_height = page.height
        
        if bottom_y < page_height - 10:
            # Crop region below table up to 60 points or page bottom
            footnote_box = (0, bottom_y, page.width, min(bottom_y + 80, page_height))
            cropped = page.crop(footnote_box)
            text = cropped.extract_text()
            if text:
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                # filter lines that look like footnotes (*, 1, 2, †, Note:)
                return [l for l in lines if re.match(r"^(\*|\d|†|‡|Note:|#)", l, re.IGNORECASE)]
    except Exception:
        pass
    return []


def categorize_table(headers: List[str], rows: List[List[str]]) -> str:
    """Classifies table into ESG functional domain."""
    combined = (" ".join(headers) + " " + " ".join([" ".join(r) for r in rows[:4]])).lower()
    
    if any(k in combined for k in ["scope 1", "scope 2", "scope 3", "ghg", "carbon", "tco2e"]):
        return "GHG_Emissions"
    elif any(k in combined for k in ["mwh", "gigajoule", "solar", "renewable energy", "fuel"]):
        return "Energy_Consumption"
    elif any(k in combined for k in ["water withdrawal", "water recycled", "effluent", "megaliter"]):
        return "Water_Stewardship"
    elif any(k in combined for k in ["hazardous waste", "landfill", "recycled waste", "plastic"]):
        return "Waste_Circularity"
    elif any(k in combined for k in ["diversity", "female", "workforce", "turnover", "gender"]):
        return "Workforce_Diversity"
    elif any(k in combined for k in ["brsr", "gri", "esrs", "kpi"]):
        return "General_ESG_Metrics"
    return "Other_ESG"
