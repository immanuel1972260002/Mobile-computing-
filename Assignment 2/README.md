# Assignment 2 — Mobile Computing (Q1–Q7)

This folder contains the question-wise written answers, executable Python/NumPy implementation and generated simulation outputs for the supplied Assignment 2 brief.

## Structure
- `Answers_Q1-Q7.md` — answers, assumptions, predictions, result analysis and design decisions.
- `src/assignment2.py` — reproducible simulations for Q1–Q7 (seed `20261119`).
- `requirements.txt` — NumPy dependency.
- `results/` — CSV output for each question and combined `all_results.json`.

## Run from repository root
```bash
python -m pip install -r "Assignment 2/requirements.txt"
python "Assignment 2/src/assignment2.py"
```

The program regenerates the question-wise CSV files and combined JSON output in `Assignment 2/results/`.

## Reproducibility
Figures are simulated using the assumptions documented in `Answers_Q1-Q7.md`. They are not measurements from a live cellular network. Fixed seed: `20261119`.
