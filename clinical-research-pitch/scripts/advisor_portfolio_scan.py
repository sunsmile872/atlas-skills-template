#!/usr/bin/env python3
"""Scan PubMed, OpenAlex, and ClinicalTrials.gov for an advisor's portfolio and topic gaps."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def fetch_json(url: str, headers: dict[str, str] | None = None, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "clinical-research-pitch/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def scan_pubmed(query: str, max_hits: int, fetch_abstracts: bool) -> list[dict]:
    enc = urllib.parse.quote(query)
    esearch = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={enc}&retmax={max_hits}&sort=date&retmode=json"
    )
    res = fetch_json(esearch).get("esearchresult", {})
    pmids = res.get("idlist", [])
    if not pmids:
        return []

    records: list[dict] = []
    if fetch_abstracts:
        efetch = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=pubmed&id={','.join(pmids)}&retmode=xml"
        )
        req = urllib.request.Request(efetch, headers={"User-Agent": "clinical-research-pitch/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            root = ET.fromstring(r.read())
        for art in root.findall(".//PubmedArticle"):
            pmid = art.findtext(".//MedlineCitation/PMID", "")
            year = art.findtext(".//JournalIssue/PubDate/Year") or art.findtext(".//JournalIssue/PubDate/MedlineDate", "")[:4]
            journal = art.findtext(".//Journal/ISOAbbreviation") or art.findtext(".//Journal/Title", "")
            title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
            abst = " ".join("".join(el.itertext()) for el in art.findall(".//Abstract/AbstractText"))
            records.append({"pmid": pmid, "year": year, "journal": journal, "title": title, "abstract": abst})
    else:
        esum = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            f"?db=pubmed&id={','.join(pmids)}&retmode=json"
        )
        summary = fetch_json(esum).get("result", {})
        for p in pmids:
            it = summary.get(p, {})
            records.append({
                "pmid": p,
                "year": it.get("pubdate", "")[:4],
                "journal": it.get("source", ""),
                "title": it.get("title", ""),
            })
    return records


def scan_openalex(author_name: str) -> list[dict]:
    url = f"https://api.openalex.org/authors?search={urllib.parse.quote(author_name)}"
    data = fetch_json(url, headers={"User-Agent": "mailto:clinical-research-pitch@example.com"})
    out = []
    for a in data.get("results", [])[:3]:
        out.append({
            "name": a.get("display_name"),
            "works_count": a.get("works_count"),
            "cited_by_count": a.get("cited_by_count"),
            "summary_stats": a.get("summary_stats"),
            "top_topics": [f"{t.get('display_name')} ({t.get('count')})" for t in a.get("topics", [])[:10]],
        })
    return out


def scan_openalex_works(query: str, max_hits: int) -> list[dict]:
    url = (
        f"https://api.openalex.org/works?search={urllib.parse.quote(query)}"
        f"&sort=publication_year:desc&per-page={min(max_hits, 25)}"
    )
    data = fetch_json(url, headers={"User-Agent": "mailto:clinical-research-pitch@example.com"})
    out = []
    for w in data.get("results", []):
        src = (w.get("primary_location") or {}).get("source") or {}
        ids = w.get("ids") or {}
        out.append({
            "year": w.get("publication_year"),
            "pmid": ids.get("pmid", ""),
            "doi": ids.get("doi", ""),
            "journal": src.get("display_name", ""),
            "title": w.get("title", ""),
        })
    return out


def scan_europepmc(query: str, max_hits: int) -> list[dict]:
    url = (
        f"https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        f"?query={urllib.parse.quote(query)}&format=json&pageSize={min(max_hits, 25)}"
    )
    data = fetch_json(url, timeout=25)
    out = []
    for r in data.get("resultList", {}).get("result", []):
        out.append({
            "pmid": r.get("pmid", ""),
            "year": r.get("pubYear", ""),
            "journal": r.get("journalTitle", ""),
            "title": r.get("title", ""),
        })
    return out


def scan_clinical_trials(term: str, max_hits: int) -> list[dict]:
    url = f"https://clinicaltrials.gov/api/v2/studies?query.term={urllib.parse.quote(term)}&pageSize={max_hits}"
    data = fetch_json(url)
    out = []
    for s in data.get("studies", []):
        ps = s.get("protocolSection", {})
        idm = ps.get("identificationModule", {})
        stm = ps.get("statusModule", {})
        out.append({
            "nct_id": idm.get("nctId"),
            "status": stm.get("overallStatus"),
            "title": idm.get("briefTitle"),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Scout advisor portfolio across PubMed, OpenAlex, and ClinicalTrials.gov.")
    ap.add_argument("--pubmed-author", help="PubMed author query, e.g. 'Manimmanakorn N[Author]'")
    ap.add_argument("--pubmed-query", help="Custom PubMed query string")
    ap.add_argument("--pubmed-meta", help="Topic keywords to pull Systematic Reviews & Meta-Analyses on PubMed")
    ap.add_argument("--openalex-author", help="Full author name for OpenAlex profile lookup")
    ap.add_argument("--openalex-works", help="Topic keywords for OpenAlex works lookup (catches regional/non-PubMed journals)")
    ap.add_argument("--epmc-query", help="Europe PMC query string")
    ap.add_argument("--ct-term", help="ClinicalTrials.gov search term")
    ap.add_argument("--max", type=int, default=20, help="Max results per source (default 20)")
    ap.add_argument("--abstracts", action="store_true", help="Fetch full PubMed abstracts via efetch")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args()

    result: dict = {}
    if args.pubmed_author or args.pubmed_query:
        q = args.pubmed_query or args.pubmed_author
        try:
            result["pubmed"] = scan_pubmed(q, args.max, args.abstracts)
        except Exception as e:
            result["pubmed_error"] = str(e)

    if args.pubmed_meta:
        meta_q = f'({args.pubmed_meta}) AND ("systematic review"[Publication Type] OR "meta-analysis"[Publication Type] OR "meta-analysis"[Title])'
        try:
            result["pubmed_meta_analyses"] = scan_pubmed(meta_q, min(args.max, 15), True)
        except Exception as e:
            result["pubmed_meta_error"] = str(e)

    if args.openalex_author:
        try:
            result["openalex_author"] = scan_openalex(args.openalex_author)
        except Exception as e:
            result["openalex_error"] = str(e)

    if args.openalex_works:
        try:
            result["openalex_works"] = scan_openalex_works(args.openalex_works, args.max)
        except Exception as e:
            result["openalex_works_error"] = str(e)

    if args.epmc_query:
        try:
            result["europe_pmc"] = scan_europepmc(args.epmc_query, args.max)
        except Exception as e:
            result["europe_pmc_error"] = str(e)

    if args.ct_term:
        try:
            result["clinical_trials"] = scan_clinical_trials(args.ct_term, min(args.max, 20))
        except Exception as e:
            result["clinical_trials_error"] = str(e)

    if not result:
        ap.print_help()
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    for section, val in result.items():
        print(f"=== {section.upper()} ===")
        if isinstance(val, list):
            for row in val:
                print(" ", row)
        else:
            print(" ", val)
    return 0


if __name__ == "__main__":
    sys.exit(main())
