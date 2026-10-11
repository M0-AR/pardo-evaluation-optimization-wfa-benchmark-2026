#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests/ -q
python3 experiments/01_preliminary.py
python3 experiments/02_optimization.py
python3 experiments/03_walkforward.py --config config/experiment.yaml
python3 experiments/04_live_verification.py
python3 experiments/05_hidden_pattern.py
echo "ALL EXPERIMENTS COMPLETE — see results/"
