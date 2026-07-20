#!/usr/bin/env python3
"""Promote staged battery exemplars into harvest/baseline/exemplars/<ID>/.

The exemplar is the QUALITY BAR each target-model output is judged against
(see memory harvest-battery-purpose). One Fable-authored exemplar per brief in
harvest/battery/core.jsonl, generated guardrail-free after studying the sources/
craft corpus. This script is the promotion step: it copies each reviewed staging
file to the layout run_judge.py expects (baseline/exemplars/<ID>/exemplar.md) and
writes a per-exemplar provenance.json so every locked exemplar is auditable.

Provenance is a deliverable, not an afterthought: run_judge.py's `tally` hashes
each exemplar into the sealed key, so what gets promoted here is what future
harvests compare against. Record enough to reconstruct how it was made.

Usage:
    python harvest/scripts/promote_exemplars.py --staging <dir> [--force]

--staging   dir of <ID>.md files (the reviewed outputs)
--force     overwrite existing baseline/exemplars/<ID>/ (default: refuse if present)
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def repo_root() -> Path:
    # walk up until we find harvest/battery/core.jsonl
    for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (parent / "harvest" / "battery" / "core.jsonl").exists():
            return parent
    sys.exit("could not locate repo root (harvest/battery/core.jsonl not found)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True, type=Path)
    ap.add_argument("--force", action="store_true")
    ap.add_argument(
        "--generator", default="claude-fable-5",
        help="model that authored the exemplars (recorded in provenance)")
    ap.add_argument(
        "--generated", default="2026-07",
        help="generation period (recorded in provenance)")
    ap.add_argument(
        "--method", default="v2-learn-decisions",
        help="generation-instruction version (recorded in provenance). "
             "v2-learn-decisions = 'learn the decisions behind the writing' framing, "
             "which reaches sub-tone mechanics the v1 'write like this' framing missed "
             "(see memory harvest-exemplar-learning-instruction)")
    args = ap.parse_args()

    root = repo_root()
    core = [json.loads(l) for l in (root / "harvest/battery/core.jsonl").open()]
    dest_root = root / "harvest/baseline/exemplars"

    # provenance inputs common to every exemplar
    corpus_manifest = root / "sources" / "MANIFEST.json"
    common = {
        "generator_model": args.generator,
        "generator_context": "sources/ craft corpus only; NO S0/F0/backstop/tic-list",
        "generation_method": args.method,
        "generated": args.generated,
        "core_jsonl_sha256": sha256_file(root / "harvest/battery/core.jsonl"),
        "corpus_manifest_sha256": (
            sha256_file(corpus_manifest) if corpus_manifest.exists() else None),
    }

    promoted, skipped = [], []
    for r in core:
        pid = r["id"]
        src = args.staging / f"{pid}.md"
        if not src.exists():
            sys.exit(f"missing staged exemplar for {pid}: {src}")
        dest_dir = dest_root / pid
        dest_md = dest_dir / "exemplar.md"
        if dest_md.exists() and not args.force:
            skipped.append(pid)
            continue
        dest_dir.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        dest_md.write_text(text, encoding="utf-8")
        prov = {
            "id": pid,
            "register": r["register"],
            "substrate_kind": r["substrate_kind"],
            "brief_prompt": r["prompt"],
            "battery_version": r.get("added"),
            "exemplar_sha256": sha256_file(dest_md),
            "word_count": len(text.split()),
            **common,
        }
        (dest_dir / "provenance.json").write_text(
            json.dumps(prov, indent=2) + "\n", encoding="utf-8")
        promoted.append(pid)

    print(f"promoted: {len(promoted)}")
    if skipped:
        print(f"skipped (exist, no --force): {len(skipped)} -> {skipped}")
    print(f"dest: {dest_root}")


if __name__ == "__main__":
    main()
