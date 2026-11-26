#!/usr/bin/env python3
"""
citation_engine.py
Two-pass non-destructive citation verification and reference resequencing for Markdown manuscripts.
Pass 1: Live PubMed E-utilities & CrossRef API check + title similarity (>= 0.50).
Pass 2: Claim-to-source grounding against PubMed abstracts and optional local PDFs.
"""

import argparse
import hashlib
import os
import re
import sys
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET

try:
    import requests
except ImportError:
    requests = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

HEADERS = {"User-Agent": "ClinicalAcademicEditor/1.0 (mailto:research@local.invalid)"}
REF_HEADER_RE = re.compile(r"^#{1,3}\s+(?:References|Bibliography|เอกสารอ้างอิง)\b", re.I | re.M)
REF_LINE_RE = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)\.)\s+(.+)$")
INLINE_BRACKET_RE = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")
PMID_RE = re.compile(r"\bPMID\s*:?\s*(\d{5,10})\b", re.I)
DOI_RE = re.compile(r"(?:doi\s*:?\s*|https?://(?:dx\.)?doi\.org/)(10\.\d{4,9}/[^\s\]\),;]+)", re.I)


def sha256_file(path: str) -> str:
    """Return hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def split_body_and_refs(text: str) -> Tuple[str, str, List[Tuple[int, str]]]:
    """Split Markdown into body, reference section header/raw, and parsed (num, text) list."""
    m = REF_HEADER_RE.search(text)
    if not m:
        return text, "", []
    body = text[: m.start()]
    ref_block = text[m.start() :]
    refs: List[Tuple[int, str]] = []
    for line in ref_block.splitlines():
        rm = REF_LINE_RE.match(line)
        if rm:
            num = int(rm.group(1) or rm.group(2))
            refs.append((num, rm.group(3).strip()))
    return body, ref_block, refs


def expand_citation_tokens(expr: str) -> List[int]:
    """Expand '1, 3-5' into [1, 3, 4, 5]."""
    nums: List[int] = []
    for part in expr.split(","):
        part = part.strip()
        if "-" in part:
            bounds = [x.strip() for x in part.split("-", 1)]
            if len(bounds) == 2 and bounds[0].isdigit() and bounds[1].isdigit():
                a, b = int(bounds[0]), int(bounds[1])
                if a <= b and (b - a) <= 50:
                    nums.extend(range(a, b + 1))
        elif part.isdigit():
            nums.append(int(part))
    return nums


def extract_inline_citations(body: str) -> List[Tuple[int, str]]:
    """Return list of (citation_number, sentence_context) from body text."""
    sentences = re.split(r"(?<=[.!?])\s+|\n+", body)
    hits: List[Tuple[int, str]] = []
    for sent in sentences:
        for m in INLINE_BRACKET_RE.finditer(sent):
            for num in expand_citation_tokens(m.group(1)):
                hits.append((num, sent.strip()))
    return hits


def normalize_text(s: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", s.lower()).strip()


def title_similarity(ref_text: str, api_title: str) -> float:
    """Best-effort similarity between API title and substring/reference text."""
    nt = normalize_text(api_title)
    nr = normalize_text(ref_text)
    if not nt or not nr:
        return 0.0
    if nt in nr:
        return 1.0
    # Compare against overlapping token windows or full string
    t_words = set(nt.split())
    r_words = set(nr.split())
    jaccard = len(t_words & r_words) / max(1, len(t_words))
    seq = SequenceMatcher(None, nt, nr[: max(len(nt) + 40, 120)]).ratio()
    return max(jaccard, seq)


def fetch_pubmed_meta(pmid: str) -> Optional[Dict[str, str]]:
    """Query NCBI esummary + efetch for a PMID."""
    if not requests:
        return None
    try:
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params={"db": "pubmed", "id": pmid, "retmode": "json"},
            headers=HEADERS,
            timeout=10,
        )
        data = r.json().get("result", {}).get(pmid)
        if not data or "error" in data:
            return None
        title = data.get("title", "")
        abstract = ""
        ef = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={"db": "pubmed", "id": pmid, "retmode": "xml"},
            headers=HEADERS,
            timeout=10,
        )
        if ef.ok:
            root = ET.fromstring(ef.text)
            abstract = " ".join(el.text or "" for el in root.findall(".//AbstractText"))
        return {"source": "PubMed", "id": f"PMID:{pmid}", "title": title, "abstract": abstract}
    except Exception:
        return None


def fetch_crossref_meta(doi: str) -> Optional[Dict[str, str]]:
    """Query CrossRef API for a DOI."""
    if not requests:
        return None
    doi_clean = doi.rstrip(".")
    try:
        r = requests.get(
            f"https://api.crossref.org/works/{doi_clean}",
            headers=HEADERS,
            timeout=10,
        )
        if not r.ok:
            return None
        msg = r.json().get("message", {})
        titles = msg.get("title") or []
        title = titles[0] if titles else ""
        abstract = re.sub(r"<[^>]+>", " ", msg.get("abstract", ""))
        return {"source": "CrossRef", "id": f"DOI:{doi_clean}", "title": title, "abstract": abstract}
    except Exception:
        return None


def search_pubmed_candidate(ref_text: str) -> Optional[str]:
    """Attempt candidate PMID lookup from cleaned reference text."""
    if not requests:
        return None
    clean = re.sub(r"PMID.*|DOI.*|https?://\S+", "", ref_text, flags=re.I)
    words = [w for w in re.findall(r"[A-Za-z0-9]{4,}", clean)][:10]
    if len(words) < 3:
        return None
    try:
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pubmed", "term": " ".join(words), "retmax": 1, "retmode": "json"},
            headers=HEADERS,
            timeout=10,
        )
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except Exception:
        return None


def index_local_pdfs(library_dir: Optional[str]) -> Dict[str, str]:
    """Extract lowercase text from PDFs in library_dir keyed by filename."""
    out: Dict[str, str] = {}
    if not library_dir or not os.path.isdir(library_dir) or not fitz:
        return out
    for root, _, files in os.walk(library_dir):
        for fn in files:
            if fn.lower().endswith(".pdf"):
                p = os.path.join(root, fn)
                try:
                    doc = fitz.open(p)
                    out[fn] = "\n".join(page.get_text("text") for page in doc)
                except Exception:
                    continue
    return out


def cmd_audit_2pass(args: argparse.Namespace) -> int:
    doc_path = os.path.abspath(args.doc)
    before_hash = sha256_file(doc_path)
    with open(doc_path, "r", encoding="utf-8") as f:
        text = f.read()

    body, _, refs = split_body_and_refs(text)
    inline_hits = extract_inline_citations(body)
    ref_map = {n: t for n, t in refs}
    pdf_texts = index_local_pdfs(args.library)

    lines = [
        "# Citation & Claim Grounding Audit Report",
        "",
        f"- **Target**: `{doc_path}`",
        f"- **SHA-256**: `{before_hash}`",
        f"- **References Parsed**: {len(refs)}",
        f"- **Inline Citation Mentions**: {len(inline_hits)}",
        f"- **Local PDFs Indexed**: {len(pdf_texts)}",
        "",
        "## Pass 1: Source Reality & Metadata Audit",
        "",
        "| # | Detected ID | API Source | Title Similarity | Status |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    meta_cache: Dict[int, Optional[Dict[str, str]]] = {}
    issues = 0

    for num, ref_text in refs:
        pm = PMID_RE.search(ref_text)
        dm = DOI_RE.search(ref_text)
        meta = None
        detected_id = "None"
        if pm:
            detected_id = f"PMID:{pm.group(1)}"
            meta = fetch_pubmed_meta(pm.group(1))
        elif dm:
            detected_id = f"DOI:{dm.group(1).rstrip('.')}"
            meta = fetch_crossref_meta(dm.group(1))

        if meta:
            sim = title_similarity(ref_text, meta["title"])
            status = "VERIFIED" if sim >= 0.50 else "TITLE_MISMATCH"
            if status != "VERIFIED":
                issues += 1
            lines.append(
                f"| {num} | `{detected_id}` | {meta['source']} | {sim:.0%} | **{status}** |"
            )
            meta_cache[num] = meta
        elif detected_id != "None":
            issues += 1
            lines.append(f"| {num} | `{detected_id}` | - | 0% | **NOT_FOUND** |")
        else:
            cand = None if args.offline else search_pubmed_candidate(ref_text)
            hint = f" (Candidate PMID:`{cand}`)" if cand else ""
            issues += 1
            lines.append(f"| {num} | None | - | - | **UNVERIFIED_NO_ID**{hint} |")

    # Check orphan inline or unused bibliography
    inline_nums = {n for n, _ in inline_hits}
    missing_in_bib = sorted(inline_nums - set(ref_map.keys()))
    unused_in_body = sorted(set(ref_map.keys()) - inline_nums)
    if missing_in_bib or unused_in_body:
        issues += len(missing_in_bib) + len(unused_in_body)
        lines.extend([
            "",
            "### Forward / Reverse Mapping Gaps",
            f"- **Cited in text but missing from References**: {missing_in_bib or 'None'}",
            f"- **Listed in References but never cited in text**: {unused_in_body or 'None'}",
        ])

    lines.extend(["", "## Pass 2: Claim Grounding & Numerical Spot-Check", ""])
    num_token_re = re.compile(r"\b(?:n\s*=\s*\d+|p\s*[<>=]\s*0?\.\d+|\d+(?:\.\d+)?%)", re.I)
    for num, sent in inline_hits:
        nums_found = num_token_re.findall(sent)
        if not nums_found:
            continue
        meta = meta_cache.get(num)
        abstract = (meta or {}).get("abstract", "")
        matched_tokens = [tok for tok in nums_found if re.sub(r"\s+", "", tok.lower()) in re.sub(r"\s+", "", abstract.lower())]
        pdf_match = [fn for fn, ptxt in pdf_texts.items() if any(t.lower() in ptxt.lower() for t in nums_found)]
        lines.append(
            f"- **[{num}]** Claim: _{sent[:160]}_ | Numbers: `{nums_found}` | "
            f"Abstract match: `{matched_tokens or 'Check full text'}` | Local PDF hit: `{pdf_match or 'None'}`"
        )

    out_path = args.out or os.path.join(os.path.dirname(doc_path), "citation_audit_report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    after_hash = sha256_file(doc_path)
    assert before_hash == after_hash, "Source file hash changed during read-only audit!"
    print(f"Report written: {out_path} (Issues flagged: {issues}, SHA-256 unchanged: {before_hash[:12]}...)")
    return 0


def cmd_resequence(args: argparse.Namespace) -> int:
    doc_path = os.path.abspath(args.doc)
    with open(doc_path, "r", encoding="utf-8") as f:
        text = f.read()

    body, ref_block, refs = split_body_and_refs(text)
    if not refs:
        print("No numbered references section found.")
        return 1

    order: List[int] = []
    for m in INLINE_BRACKET_RE.finditer(body):
        for n in expand_citation_tokens(m.group(1)):
            if n not in order:
                order.append(n)
    for n, _ in refs:
        if n not in order:
            order.append(n)

    mapping = {old: new for new, old in enumerate(order, start=1)}
    ref_lookup = {n: t for n, t in refs}

    def replace_bracket(match: re.Match) -> str:
        expanded = expand_citation_tokens(match.group(1))
        if not expanded:
            return match.group(0)
        remapped = sorted({mapping.get(n, n) for n in expanded})
        return "[" + ", ".join(str(x) for x in remapped) + "]"

    new_body = INLINE_BRACKET_RE.sub(replace_bracket, body)

    # Rebuild reference block preserving header line
    ref_lines = ref_block.splitlines()
    header = ref_lines[0] if ref_lines else "## References"
    new_ref_lines = [header, ""]
    for new_num in range(1, len(order) + 1):
        old_num = order[new_num - 1]
        if old_num in ref_lookup:
            new_ref_lines.append(f"[{new_num}] {ref_lookup[old_num]}")

    new_text = new_body.rstrip() + "\n\n" + "\n".join(new_ref_lines) + "\n"

    if args.in_place:
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"Resequenced {len(mapping)} citations in-place: {doc_path}")
    else:
        print("Resequence mapping (old -> new):", mapping)
        print("Pass -i to apply changes in-place.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="2-Pass Citation Engine & Resequencer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_aud = sub.add_parser("audit-2pass", help="Run read-only 2-pass citation & claim audit")
    p_aud.add_argument("doc", help="Markdown draft path")
    p_aud.add_argument("--library", help="Optional Literature_Library PDF directory")
    p_aud.add_argument("--out", help="Output report path")
    p_aud.add_argument("--offline", action="store_true", help="Skip fallback candidate search")
    p_aud.set_defaults(func=cmd_audit_2pass)

    p_seq = sub.add_parser("resequence", help="Resequence citations by order of appearance")
    p_seq.add_argument("doc", help="Markdown draft path")
    p_seq.add_argument("-i", "--in-place", action="store_true", help="Modify file in-place")
    p_seq.set_defaults(func=cmd_resequence)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
