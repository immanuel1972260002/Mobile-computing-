# Assignment 1 – Cellular Frequency Planning

This folder contains the question-wise answers (Q1–Q12), a Python implementation, and generated output files.

## Contents
- `Assignment_Answers.md` – answers arranged by question number.
- `src/planner.py` – frequency-planning calculations and simulation.
- `results/` – generated CSV/JSON experiment results.
- `requirements.txt` – Python dependencies.

## Run
```bash
python -m pip install -r "Assignment 1/requirements.txt"
python "Assignment 1/src/planner.py" --self-test
python "Assignment 1/src/planner.py" --out "Assignment 1/results"
```

## Modelling assumptions
The assignment data does not specify licensed channel count, busy-hour traffic per subscriber, cell radius, or propagation survey. For reproducibility, this implementation uses 420 channel equivalents, 0.5 km cell radius, 0.02 Erlang/subscriber, 12 km² service area, and 2% target blocking. These are illustrative assumptions and must be replaced by measured/operator data for deployment.
