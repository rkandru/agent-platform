#!/usr/bin/env python3
"""Collect Agent CRs from gitops/teams/<team>/agents/*.yaml into the `kubectl get -o json` shape
that render_agent_policies.py reads. Requires PyYAML (CI: pip install pyyaml)."""
import json
import sys
from pathlib import Path

import yaml


def main(teams_dir: str) -> None:
    items = []
    for f in sorted(Path(teams_dir).glob("*/agents/*.yaml")):
        team = f.parts[-3]
        if team.startswith("_"):
            continue
        for doc in yaml.safe_load_all(f.read_text()):
            if doc and doc.get("kind") == "Agent":
                doc["metadata"].setdefault("namespace", f"team-{team}")
                items.append(doc)
    json.dump({"items": items}, sys.stdout, indent=2)


if __name__ == "__main__":
    main(sys.argv[1])
