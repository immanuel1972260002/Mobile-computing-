# Assignment 1 – Program output

## Verification
Command:
```bash
python "Assignment 1/src/planner.py" --self-test
```

Expected verification line:
```
PASS: geometry, reuse, SIR, Erlang-B and splitting recurrence
```

## Generated experiment files
Run:
```bash
python "Assignment 1/src/planner.py" --out "Assignment 1/results"
```

This creates:
- `capacity_experiments.csv` – 16 combinations (4 cluster sizes × 4 subscriber loads).
- `sir_experiments.csv` – 24 combinations (3 path-loss exponents × 4 cluster sizes × 2 sectoring cases).
- `event_surge.json` – stadium traffic calculation.
- `cell_splitting_recurrence.csv` – four-way split recurrence.

## Key event calculation
- Attendees: 25,000
- Traffic per attendee: 0.05 Erlang
- Total event traffic: 1,250 Erlangs
- Event zone: 1 km²
- Township reference density: 166.67 Erlang/km²
- Event density: 7.5 times the township reference
- N = 7 gives 60 channels per cell under the 420-channel assumption
- Idealized temporary-cell lower bound at 2% blocking: 26

These are illustrative model outputs, not field measurements. Actual deployment needs measured traffic, spectrum, propagation and site data.
