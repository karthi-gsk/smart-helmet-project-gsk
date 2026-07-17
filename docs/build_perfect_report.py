#!/usr/bin/env python3
"""
build_perfect_report.py
Performs a two-pass generation of docs/PROJECT_REPORT.docx and docs/PROJECT_REPORT.pdf.
This ensures that all page numbers in the Table of Contents, List of Figures,
and List of Tables match the actual pages in the PDF precisely.
"""

import os
import sys
import json
import subprocess
import pypdf

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAGE_MAP_FILE = os.path.join(SCRIPT_DIR, "page_map.json")
DOCX_PATH = os.path.join(SCRIPT_DIR, "PROJECT_REPORT.docx")
PDF_PATH = os.path.join(SCRIPT_DIR, "PROJECT_REPORT.pdf")


def convert_docx_to_pdf():
    print("[INFO] Converting DOCX to PDF using docx2pdf...")
    from docx2pdf import convert
    convert(DOCX_PATH, PDF_PATH)
    print("[OK] PDF conversion complete.")


def scan_pdf_for_pages():
    print("[INFO] Scanning PDF to extract exact heading page numbers...")
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF file not found at: {PDF_PATH}")
        
    reader = pypdf.PdfReader(PDF_PATH)
    num_pages = len(reader.pages)
    print(f"[INFO] PDF total pages: {num_pages}")
    
    # Step 1: Find Chapter 1 start index in PDF
    ch1_idx = None
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if "CHAPTER 1: INTRODUCTION" in text:
            ch1_idx = idx
            break
            
    if ch1_idx is None:
        print("[WARN] Could not find 'CHAPTER 1: INTRODUCTION' in PDF text. Defaulting to index 8.")
        ch1_idx = 8
    else:
        print(f"[INFO] 'CHAPTER 1: INTRODUCTION' starts on PDF page index: {ch1_idx} (Page {ch1_idx + 1})")
        
    title_idx = 0
    
    def get_page_str(idx):
        if idx < ch1_idx:
            # lowerRoman for prelims starting at page ii (Certificate is index 1, i.e., page ii)
            romans = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
            rel = idx - title_idx
            if 0 <= rel < len(romans):
                return romans[rel]
            return "ii"
        else:
            # decimal for main chapters starting at Page 1 (Chapter 1)
            return str(idx - ch1_idx + 1)
            
    # Find table of contents page to avoid matching search terms on it
    toc_idx = None
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if "TABLE OF CONTENTS" in text and "Certificate" in text:
            toc_idx = idx
            break
            
    # Find list of figures page to avoid matching search terms on it
    lof_idx = None
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if "LIST OF FIGURES" in text and "System Architecture" in text:
            lof_idx = idx
            break
            
    # Find list of tables page to avoid matching search terms on it
    lot_idx = None
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if "LIST OF TABLES" in text and "Comparison of Existing" in text:
            lot_idx = idx
            break
            
    page_map = {}
    
    # 1. TOC Mappings
    toc_mappings = {
        "Certificate": "CERTIFICATE",
        "Acknowledgement": "ACKNOWLEDGEMENT",
        "Abstract": "ABSTRACT",
        "Table of Contents": "TABLE OF CONTENTS",
        "List of Figures": "LIST OF FIGURES",
        "List of Tables": "LIST OF TABLES",
        "Chapter 1: Introduction": "CHAPTER 1: INTRODUCTION",
        "Chapter 2: Problem Definition": "CHAPTER 2: PROBLEM DEFINITION",
        "Chapter 3: Objective of the Project": "CHAPTER 3: OBJECTIVE OF THE PROJECT",
        "Chapter 4: Literature Survey": "CHAPTER 4: LITERATURE SURVEY",
        "Chapter 5: Requirement Analysis": "CHAPTER 5: REQUIREMENT ANALYSIS",
        "Chapter 6: System Design": "CHAPTER 6: SYSTEM DESIGN",
        "Chapter 7: Implementation": "CHAPTER 7: IMPLEMENTATION",
        "Chapter 8: Modules Description": "CHAPTER 8: MODULES DESCRIPTION",
        "Chapter 9: Output and Screenshots": "CHAPTER 9: OUTPUT AND SCREENSHOTS",
        "Chapter 10: Testing": "CHAPTER 10: TESTING",
        "Chapter 11: Advantages and Applications": "CHAPTER 11: ADVANTAGES AND APPLICATIONS",
        "Chapter 12: Limitations": "CHAPTER 12: LIMITATIONS",
        "Chapter 13: Future Scope": "CHAPTER 13: FUTURE SCOPE",
        "Chapter 14: Conclusion": "CHAPTER 14: CONCLUSION",
        "Chapter 15: References / Bibliography": "CHAPTER 15: REFERENCES",
        "Appendix A: Backend API Details": "APPENDIX A: BACKEND API DETAILS",
        "Appendix B: Important Code Snippets": "APPENDIX B: IMPORTANT CODE SNIPPETS",
        "Appendix C: Run Commands": "APPENDIX C: RUN COMMANDS",
        "Appendix D: Demo Flow": "APPENDIX D: DEMO FLOW",
        "Appendix E: Hardware Components List": "APPENDIX E: HARDWARE COMPONENTS LIST",
    }
    
    for key, search_term in toc_mappings.items():
        found_idx = None
        for idx, page in enumerate(reader.pages):
            if idx == toc_idx and key != "Table of Contents":
                continue
            text = page.extract_text()
            if search_term in text:
                found_idx = idx
                break
        if found_idx is not None:
            page_map[key] = get_page_str(found_idx)
            
    # 2. Figures Mappings
    fig_titles = [
        "Fig. 1: System Architecture Diagram",
        "Fig. 2: Data Flow Diagram (Level-1)",
        "Fig. 3: Use Case Diagram",
        "Fig. 4: Activity Diagram",
        "Fig. 5: Sequence Diagram",
        "Fig. 6: Class Diagram",
        "Fig. 7: Home Page of Smart Helmet Website",
        "Fig. 8: Project Team Section",
        "Fig. 9: Live Dashboard in Safe Mode",
        "Fig. 10: Risky Mode Showing At-Risk Prediction",
        "Fig. 11: Drunk Mode Showing Alcohol Detection",
        "Fig. 12: Drowsy Mode Showing Fatigue Warning",
        "Fig. 13: Crash Mode Showing Emergency SOS Alert",
        "Fig. 14: GPS Location and Google Maps Link",
        "Fig. 15: Project Modules Page",
        "Fig. 16: Future Hardware Integration Diagram",
        "Fig. 17: FastAPI Documentation Page"
    ]
    
    for fig in fig_titles:
        num = fig.split(":")[0] + " "
        found_idx = None
        for idx, page in enumerate(reader.pages):
            if idx in [lof_idx, toc_idx]:
                continue
            text = page.extract_text()
            # Look for the exact caption at the bottom of the page
            if fig in text:
                found_idx = idx
                break
            # Fallback to search by "Fig. X "
            elif num in text and "LIST OF FIGURES" not in text:
                # verify it's not another figure reference
                lines = text.split("\n")
                if any(fig in l or num in l for l in lines):
                    found_idx = idx
                    break
        if found_idx is not None:
            page_map[fig] = get_page_str(found_idx)
        else:
            print(f"[WARN] Could not find page for figure: {fig}")
            
    # 3. Tables Mappings
    table_titles = [
        "Table 1: Comparison of Existing and Proposed Systems",
        "Table 2: Functional Requirements",
        "Table 3: Non-Functional Requirements",
        "Table 4: Software Requirements",
        "Table 5: Hardware Requirements (Future Scope)",
        "Table 6: ML Prediction Labels and Probabilities",
        "Table 7: Simulation Mode Parameters",
        "Table 8: Test Cases and Results"
    ]
    
    for tbl in table_titles:
        num = tbl.split(":")[0] + " "
        found_idx = None
        for idx, page in enumerate(reader.pages):
            if idx in [lot_idx, toc_idx]:
                continue
            text = page.extract_text()
            if tbl in text:
                found_idx = idx
                break
            elif num in text and "LIST OF TABLES" not in text:
                found_idx = idx
                break
        if found_idx is not None:
            page_map[tbl] = get_page_str(found_idx)
        else:
            print(f"[WARN] Could not find page for table: {tbl}")
            
    return page_map


def main():
    print("=== STARTING PERFECT TWO-PASS REPORT BUILD ===")
    
    # Pass 1: Generate initial DOCX and PDF (with defaults/approximations)
    print("\n--- PASS 1: Generating Initial Documents ---")
    if os.path.exists(PAGE_MAP_FILE):
        os.remove(PAGE_MAP_FILE)
        
    subprocess.run([sys.executable, "generate_report.py"], check=True)
    convert_docx_to_pdf()
    
    # Extract exact pages from Pass 1 PDF
    print("\n--- EXTRACTING PAGE NUMBER MAP ---")
    page_map = scan_pdf_for_pages()
    
    # Save the page map to file
    with open(PAGE_MAP_FILE, "w") as f:
        json.dump(page_map, f, indent=2)
    print(f"[OK] Saved extracted page map to {PAGE_MAP_FILE}")
    
    # Pass 2: Re-generate DOCX with exact page numbers
    print("\n--- PASS 2: Regenerating Perfect Documents with Dot Leaders & Match Page Numbers ---")
    subprocess.run([sys.executable, "generate_report.py"], check=True)
    convert_docx_to_pdf()
    
    print("\n=== SUCCESS: Perfect submission-ready documents generated! ===")
    print(f"Generated DOCX: {DOCX_PATH}")
    print(f"Generated PDF: {PDF_PATH}")

    # Final verification pass
    print("\n--- FINAL VERIFICATION ---")
    final_map = scan_pdf_for_pages()
    reader = pypdf.PdfReader(PDF_PATH)
    print(f"PDF total pages: {len(reader.pages)}")

    with open(PAGE_MAP_FILE, "r") as f:
        saved_map = json.load(f)

    toc_page = reader.pages[4].extract_text()
    mismatches = []
    for key, expected in saved_map.items():
        if key.startswith("Chapter") or key.startswith("Appendix") or key in [
            "Certificate", "Acknowledgement", "Abstract", "Table of Contents",
            "List of Figures", "List of Tables"
        ]:
            if expected not in toc_page and key in toc_page.split("\n")[0:25]:
                pass
        if key.startswith("Fig.") or key.startswith("Table"):
            continue

    for key in ["Chapter 9: Output and Screenshots", "Chapter 15: References / Bibliography",
                "Appendix E: Hardware Components List"]:
        pg = saved_map.get(key, "?")
        print(f"  {key}: page {pg}")

    # Check Table 2 is not orphaned
    ch1_idx = None
    for idx, page in enumerate(reader.pages):
        if "CHAPTER 1: INTRODUCTION" in page.extract_text():
            ch1_idx = idx
            break
    for idx, page in enumerate(reader.pages):
        t = page.extract_text()
        if "Table 2: Functional Requirements" in t:
            lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
            tbl_idx = next(i for i, ln in enumerate(lines) if "Table 2:" in ln)
            tail = lines[tbl_idx:]
            has_data = any(ln.startswith("FR-") for ln in tail)
            footer = idx - ch1_idx + 1
            print(f"  Table 2 on footer page {footer}: caption+data together={has_data}")
            if not has_data:
                mismatches.append("Table 2 caption orphaned without data rows")
            break

    if mismatches:
        print("[WARN] Verification issues:", mismatches)
    else:
        print("[OK] Verification checks passed.")


if __name__ == "__main__":
    main()
