import os
import json
import csv
import time
import requests
from pathlib import Path
from lxml import etree

# ========= CONFIG =========
# Start GROBID first:
#   docker pull lfoppiano/grobid:0.8.0
#   docker run --rm -it -p 8070:8070 lfoppiano/grobid:0.8.0
GROBID_URL = "http://localhost:8070/api/processFulltextDocument"

# Your PDFs folder:
PDF_DIR = Path(r"C:\Users\negin\Survey_Negin\References\References_V_3\PDFs_3")

# Outputs will be written next to this script / current working dir:
OUT_JSON = Path("grobid_references.json")     # per-paper dict of references
OUT_CSV  = Path("grobid_references.csv")      # flat table of all references

# ========= HELPERS =========
def text_or_none(node):
    if node is None:
        return None
    t = "".join(node.itertext()).strip()
    return t or None

def get_year_from_bibl(bibl):
    # Prefer <date when="YYYY-...">
    date = bibl.find(".//{*}date")
    if date is not None:
        when = date.get("when")
        if when and len(when) >= 4 and when[:4].isdigit():
            return when[:4]
        t = text_or_none(date)
        if t:
            parts = t.replace(",", " ").split()
            for token in parts:
                if token.isdigit() and len(token) == 4:
                    return token
    # Fallback: any 4-digit number in the reference text
    t = "".join(bibl.itertext())
    for token in t.split():
        if token.isdigit() and len(token) == 4:
            return token
    return None

def parse_bibl_struct(bibl):
    # Title (article-level), fallback to any title
    title = text_or_none(bibl.find(".//{*}title[@level='a']")) \
         or text_or_none(bibl.find(".//{*}title"))

    # Authors
    authors = []
    for pers in bibl.findall(".//{*}author/{*}persName"):
        given = text_or_none(pers.find(".//{*}forename"))
        family = text_or_none(pers.find(".//{*}surname"))
        if family and given:
            authors.append(f"{given} {family}")
        elif family:
            authors.append(family)
        elif given:
            authors.append(given)
    if not authors:
        # fallback to any text inside <author>
        for a in bibl.findall(".//{*}author"):
            t = text_or_none(a)
            if t:
                authors.append(t)

    # Venue (journal/book/series)
    venue = (
        text_or_none(bibl.find(".//{*}monogr/{*}title")) or
        text_or_none(bibl.find(".//{*}series/{*}title"))
    )

    # DOI
    doi = None
    for idno in bibl.findall(".//{*}idno"):
        id_type = (idno.get("type") or "").lower()
        txt = text_or_none(idno)
        if id_type == "doi" and txt:
            doi = txt
            break
        if txt and "10." in txt:  # heuristic
            doi = txt
            break

    # Year
    year = get_year_from_bibl(bibl)

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "venue": venue,
        "doi": doi
    }

def extract_references_from_tei(tei_xml_bytes):
    root = etree.fromstring(tei_xml_bytes)
    bibls = root.findall(".//{*}listBibl/{*}biblStruct")
    refs = [parse_bibl_struct(b) for b in bibls]
    # keep only refs with a title or authors
    refs = [r for r in refs if (r["title"] or r["authors"])]
    return refs

def grobid_process(pdf_path, retry=3, sleep=1.5):
    files = {"input": (pdf_path.name, open(pdf_path, "rb"), "application/pdf")}
    data = {
        "consolidateCitations": 1,
        "includeRawCitations": 1,
        "includeRawAffiliations": 0
    }
    for attempt in range(1, retry + 1):
        try:
            resp = requests.post(GROBID_URL, files=files, data=data, timeout=90)
            if resp.status_code == 200 and resp.content.strip():
                return resp.content
            time.sleep(sleep)
        except requests.RequestException:
            time.sleep(sleep)
    raise RuntimeError(f"GROBID failed for {pdf_path}")

# ========= RUN =========
def main():
    if not PDF_DIR.exists():
        raise FileNotFoundError(f"PDF directory not found: {PDF_DIR}")

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDFs in {PDF_DIR}")

    per_paper = {}    # {pdf_name: [refs]}
    flat_rows = []    # for CSV

    for i, pdf in enumerate(pdf_files, 1):
        try:
            tei = grobid_process(pdf)
            refs = extract_references_from_tei(tei)
            per_paper[pdf.name] = refs
            for r in refs:
                flat_rows.append({
                    "source_pdf": pdf.name,
                    "ref_title": r["title"],
                    "ref_authors": "; ".join(r["authors"]) if r["authors"] else None,
                    "ref_year": r["year"],
                    "ref_venue": r["venue"],
                    "ref_doi": r["doi"],
                })
            print(f"[{i}/{len(pdf_files)}] {pdf.name}: {len(refs)} references")
        except Exception as e:
            print(f"[{i}/{len(pdf_files)}] {pdf.name}: ERROR -> {e}")

    # Save JSON (per paper)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(per_paper, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved JSON: {OUT_JSON.resolve()}")

    # Save CSV (flat)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["source_pdf", "ref_title", "ref_authors", "ref_year", "ref_venue", "ref_doi"]
        )
        writer.writeheader()
        writer.writerows(flat_rows)
    print(f"✅ Saved CSV:  {OUT_CSV.resolve()}")

    total_refs = sum(len(v) for v in per_paper.values())
    print(f"\nSummary: PDFs={len(pdf_files)}, total references extracted={total_refs}")

if __name__ == "__main__":
    main()
