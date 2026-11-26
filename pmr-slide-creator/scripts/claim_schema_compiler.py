#!/usr/bin/env python3
"""
Deterministic Claim-ID Compiler for Slide Creator v3 (Phase 3/4 Prototype)
Eliminates manual [[k]] guessing and phantom FOOTNOTE_MAP strings:
  - Authors embed verified {{CLAIM_ID}} or {{CLAIM_A,CLAIM_B}} tokens in Stage 1 JSON.
  - Every CLAIM_ID maps 1:1 in `claim_registry` to {book_id, page, quote}.
  - Compiler auto-resolves [[book_ids]] (or Unicode ¹²³⁴ for charts), enforces anti-digit-adjacency,
    auto-computes exact per-slide `footnote` (`Ref:`) strings from rendered claims only,
    and builds the trailing `references_slide` from actual deck usage.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CLAIM_TOKEN_RE = re.compile(r"\{\{([A-Za-z0-9_,\s-]+)\}\}")
UNICODE_SUP = {1: "\u00b9", 2: "\u00b2", 3: "\u00b3", 4: "\u2074", 5: "\u2075", 6: "\u2076", 7: "\u2077", 8: "\u2078", 9: "\u2079"}


def _format_pages(pages: list[str]) -> str:
    """Sorts, deduplicates, and merges page tokens cleanly (e.g. ['p. 577', 'p. 576–577'] -> 'pp. 576–577')."""
    ranges: list[tuple[int, int]] = []
    non_numeric: list[str] = []
    for p in pages:
        cleaned = re.sub(r"^(pp?\.\s*)", "", p.strip())
        if not cleaned:
            continue
        for part in [s.strip() for s in cleaned.split(",") if s.strip()]:
            m = re.match(r"^(\d+)(?:[–-](\d+))?$", part)
            if m:
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else start
                ranges.append((min(start, end), max(start, end)))
            elif part not in non_numeric:
                non_numeric.append(part)

    merged: list[tuple[int, int]] = []
    for s, e in sorted(ranges):
        if merged and s <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    tokens = [f"{s}–{e}" if e > s else str(s) for s, e in merged] + non_numeric
    joined = ", ".join(tokens)
    prefix = "pp." if (len(tokens) > 1 or any(ch in joined for ch in ("–", "-", ","))) else "p."
    return f"{prefix} {joined}"


def _resolve_string(
    text: str,
    registry: dict,
    used_claims: list[str],
    slide_num: int,
    is_chart_label: bool = False,
) -> str:
    def _repl(match: re.Match) -> str:
        prefix = text[: match.start()]
        if re.search(r"\d\.?$", prefix):
            raise ValueError(
                f"Slide {slide_num:02d}: Digit-adjacent claim token '{prefix[-12:]}{match.group(0)}' "
                f"(anchor citation onto a word instead)"
            )
        raw_ids = [cid.strip() for cid in match.group(1).split(",") if cid.strip()]
        book_ids: list[int] = []
        for cid in raw_ids:
            if cid not in registry:
                raise KeyError(f"Slide {slide_num:02d}: Unknown claim_id '{cid}' not found in claim_registry")
            if cid not in used_claims:
                used_claims.append(cid)
            bid = int(registry[cid]["book_id"])
            if bid not in book_ids:
                book_ids.append(bid)
        book_ids.sort()
        if is_chart_label:
            return "".join(UNICODE_SUP[b] for b in book_ids)
        return "[[" + ",".join(str(b) for b in book_ids) + "]]"

    return CLAIM_TOKEN_RE.sub(_repl, text)


def _walk_and_resolve(obj, registry: dict, used_claims: list[str], slide_num: int, key_name: str = ""):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("claims", "allowed_label_numbers", "references", "claim_ids", "footnote"):
                out[k] = copy.deepcopy(v)
                continue
            if k == "figure" and isinstance(v, dict) and v.get("claim_id"):
                fig = copy.deepcopy(v)
                cid = fig["claim_id"]
                if cid not in registry:
                    raise KeyError(f"Slide {slide_num:02d}: Unknown figure claim_id '{cid}'")
                if cid not in used_claims:
                    used_claims.append(cid)
                cobj = registry[cid]
                fig["source"] = f"[{cobj['book_id']}] {cobj['page']}"
                out[k] = fig
                continue
            out[k] = _walk_and_resolve(v, registry, used_claims, slide_num, key_name=k)
        return out
    if isinstance(obj, list):
        is_chart_cats = key_name == "categories"
        return [
            _walk_and_resolve(item, registry, used_claims, slide_num, key_name="chart_cat" if is_chart_cats else key_name)
            for item in obj
        ]
    if isinstance(obj, str):
        return _resolve_string(obj, registry, used_claims, slide_num, is_chart_label=(key_name == "chart_cat"))
    return obj


def compile_bundle(raw_bundle: dict) -> dict:
    """Compiles a v3_claim_id bundle into an auditable deck spec with auto-derived footnotes & references."""
    registry = raw_bundle.get("claim_registry")
    if not isinstance(registry, dict) or not registry:
        raise ValueError("Bundle must define non-empty 'claim_registry'")

    ref_catalog = {int(r["id"]): copy.deepcopy(r) for r in raw_bundle.get("references", [])}
    compiled_slides: list[dict] = []
    deck_books_used: dict[int, list[str]] = defaultdict(list)

    for s_obj in raw_bundle.get("slides", []):
        s_num = int(s_obj["slide_id"])
        arch = s_obj.get("archetype", "")
        if arch == "references_slide":
            continue

        used_claims: list[str] = []
        resolved = _walk_and_resolve(s_obj, registry, used_claims, s_num)
        resolved["claim_ids"] = used_claims

        per_book_pages: dict[int, list[str]] = defaultdict(list)
        for cid in used_claims:
            bid = int(registry[cid]["book_id"])
            pg = str(registry[cid]["page"]).strip()
            if pg not in per_book_pages[bid]:
                per_book_pages[bid].append(pg)
            if pg not in deck_books_used[bid]:
                deck_books_used[bid].append(pg)

        if s_num > 1 and per_book_pages:
            parts = [f"[{bid}] {_format_pages(per_book_pages[bid])}" for bid in sorted(per_book_pages.keys())]
            resolved["footnote"] = "  |  ".join(parts)
        else:
            resolved["footnote"] = ""

        # Collect allowed numbers from resolved text + slide pagination + reference IDs
        nums = set(re.findall(r"\d+(?:\.\d+)?", json.dumps(resolved, ensure_ascii=False)))
        nums.update(str(bid) for bid in per_book_pages.keys())
        nums.add(str(s_num))
        nums.add(f"{s_num:02d}")
        resolved["allowed_label_numbers"] = sorted(nums)
        compiled_slides.append(resolved)

    # Append dynamic References slide containing strictly books cited in deck
    total_slides = len(compiled_slides) + 1
    active_refs = []
    for bid in sorted(deck_books_used.keys()):
        if bid not in ref_catalog:
            raise KeyError(f"Cited book_id [{bid}] missing from top-level 'references' catalog")
        ref_entry = copy.deepcopy(ref_catalog[bid])
        if not ref_entry.get("chapters_pages"):
            ref_entry["chapters_pages"] = _format_pages(deck_books_used[bid])
        active_refs.append(ref_entry)

    ref_nums = set(re.findall(r"\d+(?:\.\d+)?", json.dumps(active_refs, ensure_ascii=False)))
    ref_nums.update({str(total_slides), "1", "2", "3", "4"})
    compiled_slides.append(
        {
            "slide_id": total_slides,
            "archetype": "references_slide",
            "eyebrow": "REFERENCES  |  PRIMARY TEXTBOOK SOURCES",
            "title": "Primary Textbook References",
            "subtitle": "All clinical figures, statistics, and diagnostic criteria verified verbatim from approved textbooks",
            "references": active_refs,
            "allowed_label_numbers": sorted(ref_nums),
            "footnote": "",
        }
    )

    for s in compiled_slides:
        s["allowed_label_numbers"] = sorted(set(s.get("allowed_label_numbers", []) + [str(total_slides)]))

    out = copy.deepcopy(raw_bundle)
    out["schema_version"] = "v3_claim_id_compiled"
    out["references"] = active_refs
    out["slides"] = compiled_slides
    return out


def main():
    parser = argparse.ArgumentParser(description="Compile Stage 1 v3_claim_id bundle into verified evidence_bundle.json")
    parser.add_argument("--in-json", required=True)
    parser.add_argument("--out-json", required=True)
    args = parser.parse_args()

    raw = json.loads(Path(args.in_json).read_text(encoding="utf-8"))
    compiled = compile_bundle(raw)
    Path(args.out_json).write_text(json.dumps(compiled, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"SUCCESS: Compiled {len(compiled['slides'])} slides ({len(compiled['references'])} active references) -> {args.out_json}"
    )


if __name__ == "__main__":
    main()
