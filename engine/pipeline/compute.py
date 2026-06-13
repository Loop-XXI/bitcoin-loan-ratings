#!/usr/bin/env python3
"""
Pipeline: evidence.yaml → compute scores → write scores.yaml

Usage:
    python -m engine.pipeline.compute data/providers/<slug>/

Reads evidence.yaml from the provider directory, runs the AnchorGrade engine,
writes scores.yaml, and prints a summary.
"""
import os, sys, yaml, argparse
from pathlib import Path

# Ensure project root is on sys.path
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.anchor import AnchorGrader, EvidenceTier


def load_evidence_yaml(path: Path) -> dict:
    """Load and validate an evidence.yaml file."""
    ev_path = path / "evidence.yaml"
    if not ev_path.exists():
        print(f"ERROR: {ev_path} not found")
        sys.exit(1)
    with open(ev_path) as f:
        data = yaml.safe_load(f)
    return data


def evidence_to_grader_input(evidence: dict) -> dict:
    """Convert evidence.yaml structure to AnchorGrader.compute_all() input.

    The evidence.yaml uses human-readable tier strings ('T1', 'T2', etc.).
    The grader expects EvidenceTier enum values.
    """
    tier_map = {
        "T1": EvidenceTier.T1,
        "T2": EvidenceTier.T2,
        "T3": EvidenceTier.T3,
        "T4": EvidenceTier.T4,
        "T0": EvidenceTier.T0,
    }

    grader_input = {}

    # Convert gates
    gates_data = evidence.get("gates", {})
    grader_input["gates"] = {}
    for gate_id, entry in gates_data.items():
        if isinstance(entry, dict):
            grader_input["gates"][gate_id] = entry.get("value", False)
        else:
            grader_input["gates"][gate_id] = bool(entry)

    # Convert pillars
    for pillar_id in ["pillar_1", "pillar_2", "pillar_3", "pillar_4", "pillar_5"]:
        pillar_data = evidence.get(pillar_id, {})
        grader_input[pillar_id] = {}
        for sub_id, entry in pillar_data.items():
            if not isinstance(entry, dict):
                continue
            raw_tier = entry.get("tier", "T0")
            grader_input[pillar_id][sub_id] = {
                "score": float(entry.get("score", 0)),
                "tier": tier_map.get(raw_tier, EvidenceTier.T0),
            }

    return grader_input


def write_scores_yaml(path: Path, result: dict):
    """Write computed scores to scores.yaml."""
    scores_path = path / "scores.yaml"

    output = {
        "last_computed": __import__("datetime").date.today().isoformat(),
        "engine_version": "1.0.0",
        "gates_triggered": result["gates"],
        "pillar_scores": {k: round(v, 2) for k, v in result["pillar_scores"].items()},
        "anchor_score": round(result["anchor_score"], 2),
        "grade_letter": result["grade_letter"],
    }

    with open(scores_path, "w") as f:
        yaml.dump(
            output,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
    print(f"  Wrote: {scores_path}")


def print_summary(slug: str, result: dict):
    """Print a concise summary."""
    gates = result["gates"]
    gate_status = f"GATED ({', '.join(gates)})" if gates else "None"
    print()
    print(f"{'='*50}")
    print(f"  {slug}")
    print(f"{'='*50}")
    print(f"  Gates triggered: {gate_status}")
    if not gates:
        print(f"  Pillar scores:")
        for pid in ["pillar_1", "pillar_2", "pillar_3", "pillar_4", "pillar_5"]:
            ps = result["pillar_scores"].get(pid, 0)
            name = {
                "pillar_1": "Key Control & Exit",
                "pillar_2": "Asset Fidelity",
                "pillar_3": "Verifiability",
                "pillar_4": "Operator Resilience",
                "pillar_5": "Borrower Exposure",
            }.get(pid, pid)
            print(f"    {name:25s}  {ps:6.2f}")
        print(f"  Anchor Score:     {result['anchor_score']:.2f}")
        print(f"  Grade:            {result['grade_letter']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Compute Anchor Grade from evidence.yaml")
    parser.add_argument("provider_dir", help="Path to provider directory (e.g., data/providers/unchained/)")
    args = parser.parse_args()

    provider_path = Path(args.provider_dir).resolve()
    slug = provider_path.name

    print(f"\n  Computing grade for: {slug}")
    print(f"  Reading: {provider_path / 'evidence.yaml'}")

    evidence = load_evidence_yaml(provider_path)
    grader_input = evidence_to_grader_input(evidence)

    grader = AnchorGrader()
    result = grader.compute_all(grader_input)

    write_scores_yaml(provider_path, result)
    print_summary(slug, result)

    if result["gates"]:
        print("  ⛔ Provider is GATED — not scored.")
    else:
        print("  ✅ Grade computed deterministically from evidence.")


if __name__ == "__main__":
    main()
