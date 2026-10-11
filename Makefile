test:
	python3 -m pytest tests/ -q
exp01:
	python3 experiments/01_preliminary.py
exp02:
	python3 experiments/02_optimization.py
exp03:
	python3 experiments/03_walkforward.py --config config/experiment.yaml
exp04:
	python3 experiments/04_live_verification.py
exp05:
	python3 experiments/05_hidden_pattern.py
all: test exp01 exp02 exp03 exp04 exp05
