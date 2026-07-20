#!/usr/bin/env python3
"""
generate_corpus.py — harvest H2 target-corpus generation.

Generates target-model output for every battery brief, one output per API call
with FRESH CONTEXT (a single messages.create, no carried history) — the H2 rule.
Varies ONLY sampling across the N samples of a brief: same system prompt, same
brief, same substrate. Saves prose-only to the documented convention

    <out>/outputs/<model>/<arm>/<prompt-id>.<NN>.md      (e.g. AN04.01.md)

read by `run_judge.py prepare`.

Two arms (HARVEST.md H2):
  A — control:    NO system prompt (brief + its own substrate only). Raw signature.
  B — gates-only: S0 core (S0_natural_prose_standards.md) as the system prompt,
                  with the BACKSTOP region left empty — its committed state. No
                  F0, no backstop, no voice profile.

Provenance: writes <out>/generation-provenance.json recording model IDs, arm
system-prompt hashes, battery hash, samples/brief, and a per-output row (model,
arm, brief, sample, resolved model id, sha256, word count, stop_reason). This is
a deliverable — the report cites it.

WHY the API and not subagents: one messages.create per output makes fresh
context structural (not a promise), pins the exact target model id, and lets
arm A carry literally no system prompt. A subagent harness cannot strip its own
ambient disposition and cannot pin the target model — both fatal to a clean arm
separation. Cost is not the constraint here (scientist-whose-work-ships).

Idempotent: skips an output that already exists unless --overwrite. Re-running
after an interruption resumes where it stopped.

    generate_corpus.py --out reports/<id> --models claude-opus-4-8 claude-sonnet-5 \\
        --arms A B --samples 3
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BATTERY = REPO / "harvest" / "battery" / "core.jsonl"
S0_CORE = REPO / "modules" / "S0_natural_prose_standards.md"

# max_tokens headroom per register. The longest briefs (~500w analytic/reasoning,
# ~400w narrative) sit well under 2000 tokens of prose; 4096 leaves room without
# inviting the model to overrun a length cap on its own.
MAX_TOKENS = 4096


def _load_env_local() -> None:
    for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        cand = parent / ".env.local"
        if cand.is_file():
            for raw in cand.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
            return


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_text(p.read_text(encoding="utf-8"))


def word_count(t: str) -> int:
    return len(re.findall(r"\S+", t))


def load_battery() -> list[dict]:
    return [json.loads(l) for l in BATTERY.read_text(encoding="utf-8").splitlines() if l.strip()]


def arm_system_prompt(arm: str) -> str | None:
    """The system prompt for an arm.

    A: None — no guardrails at all.
    B: the shipped S0 core, body only (frontmatter stripped), backstop region
       already empty in the committed file. This is what a consuming library
       loads as its prose floor before any backstop is spliced in.
    """
    if arm == "A":
        return None
    if arm == "B":
        body = S0_CORE.read_text(encoding="utf-8")
        # Strip the YAML frontmatter (build metadata, not part of the prompt a
        # library loads). Everything after the first closing '---' is the module.
        m = re.match(r"^---\n.*?\n---\n(.*)$", body, re.DOTALL)
        return (m.group(1) if m else body).strip()
    raise ValueError(f"unknown arm {arm!r}")


def user_message(brief: dict) -> str:
    """The brief as the model sees it: the prompt, plus its substrate when the
    register carries one. Mirrors how the exemplar generator received each brief
    (prompt + substrate, prose only)."""
    prompt = brief["prompt"].strip()
    substrate = (brief.get("substrate") or "").strip()
    if substrate:
        return f"{prompt}\n\n---\n\n{substrate}"
    return prompt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True, help="report dir")
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--arms", nargs="+", default=["A", "B"], choices=["A", "B"])
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--only-brief", default=None,
                    help="generate just this brief id (a smoke check)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be generated; make no API calls")
    args = ap.parse_args()

    _load_env_local()
    battery = load_battery()
    if args.only_brief:
        battery = [b for b in battery if b["id"] == args.only_brief]
        if not battery:
            print(f"no brief {args.only_brief}", file=sys.stderr)
            return 2

    arm_prompts = {a: arm_system_prompt(a) for a in args.arms}
    arm_hashes = {a: (sha256_text(p) if p else None) for a, p in arm_prompts.items()}
    battery_hash = sha256_file(BATTERY)

    total = len(args.models) * len(args.arms) * len(battery) * args.samples
    print(f"plan: {len(args.models)} models x {len(args.arms)} arms x "
          f"{len(battery)} briefs x {args.samples} samples = {total} outputs")
    print(f"  models: {', '.join(args.models)}")
    print(f"  arms:   {', '.join(args.arms)}  (A=no-guardrails, B=S0-core)")
    for a in args.arms:
        h = arm_hashes[a]
        print(f"    arm {a} system prompt: {'(none)' if h is None else h[:16]}")
    print(f"  battery: {BATTERY.name} sha256 {battery_hash[:16]}")

    if args.dry_run:
        for m in args.models:
            for a in args.arms:
                for b in battery:
                    for n in range(1, args.samples + 1):
                        print(f"  would generate {m}/{a}/{b['id']}.{n:02d}.md")
        return 0

    from anthropic import Anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("no ANTHROPIC_API_KEY (see .env.local)", file=sys.stderr)
        return 2
    client = Anthropic()

    prov_path = args.out / "generation-provenance.json"
    prov = {
        "script_version": "0.1.0",
        "battery": str(BATTERY.relative_to(REPO)),
        "battery_sha256": battery_hash,
        "s0_core": str(S0_CORE.relative_to(REPO)),
        "s0_core_sha256": sha256_file(S0_CORE),
        "models": args.models,
        "arms": args.arms,
        "arm_system_prompt_sha256": arm_hashes,
        "samples_per_brief": args.samples,
        "max_tokens": MAX_TOKENS,
        "note": "fresh context per output (one messages.create, no history). "
                "Arm A: no system prompt. Arm B: S0 core body, backstop empty. "
                "Sampling is the only thing varied across a brief's samples.",
        "outputs": [],
    }
    if prov_path.exists():  # resume: keep prior rows, append new
        try:
            prov["outputs"] = json.loads(prov_path.read_text())["outputs"]
        except Exception:
            pass
    seen = {(r["model"], r["arm"], r["pid"]) for r in prov["outputs"]}

    done = skipped = failed = 0
    for m in args.models:
        for a in args.arms:
            system = arm_prompts[a]
            out_dir = args.out / "outputs" / m / a
            out_dir.mkdir(parents=True, exist_ok=True)
            for b in battery:
                msg = user_message(b)
                for n in range(1, args.samples + 1):
                    pid = f"{b['id']}.{n:02d}"
                    outfile = out_dir / f"{pid}.md"
                    if outfile.exists() and not args.overwrite:
                        skipped += 1
                        continue
                    kwargs = dict(model=m, max_tokens=MAX_TOKENS,
                                  messages=[{"role": "user", "content": msg}])
                    if system:
                        kwargs["system"] = system
                    try:
                        resp = client.messages.create(**kwargs)
                    except Exception as e:  # transient API error: log, keep going
                        print(f"  FAIL {m}/{a}/{pid}: {e}", file=sys.stderr)
                        failed += 1
                        time.sleep(2)
                        continue
                    text = "".join(bl.text for bl in resp.content
                                   if getattr(bl, "type", None) == "text").strip()
                    outfile.write_text(text + "\n", encoding="utf-8")
                    row = {
                        "model": m, "arm": a, "brief": b["id"], "sample": n,
                        "pid": pid, "register": b["register"],
                        "substrate_kind": b["substrate_kind"],
                        "resolved_model": resp.model,
                        "sha256": sha256_text(text),
                        "word_count": word_count(text),
                        "stop_reason": resp.stop_reason,
                    }
                    # de-dupe on resume/overwrite
                    prov["outputs"] = [r for r in prov["outputs"]
                                       if (r["model"], r["arm"], r["pid"]) != (m, a, pid)]
                    prov["outputs"].append(row)
                    done += 1
                    if done % 10 == 0:
                        prov_path.write_text(json.dumps(prov, ensure_ascii=False, indent=2))
                    flag = "" if resp.stop_reason == "end_turn" else f"  [{resp.stop_reason}]"
                    print(f"  {m}/{a}/{pid}  {row['word_count']}w{flag}")

    prov_path.write_text(json.dumps(prov, ensure_ascii=False, indent=2))
    print(f"\ngenerated {done}, skipped {skipped} (existing), failed {failed}")
    print(f"provenance: {prov_path}")
    if failed:
        print("re-run the same command to retry failed outputs (idempotent).")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
