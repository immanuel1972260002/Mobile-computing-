# Assignment 1 — Mobile Computing (Q1–Q7)

This folder contains the written answers and Python/NumPy simulations for all seven questions in the supplied assignment brief.

## Folder structure

- `Answers_Q1-Q7.md` — answers, assumptions, predictions, analysis and design decisions.
- `src/assignment1.py` — Q1–Q7 simulation program (fixed random seed: 197226).
- `requirements.txt` — Python dependency.
- `results/` — question-wise CSV outputs. Running the program also generates a combined `all_results.json` file.

## Run the simulations

From the repository root:

```bash
python -m pip install -r "Assignment 1/requirements.txt"
python "Assignment 1/src/assignment1.py"
```

The program writes result files to `Assignment 1/results/`.

## Questions covered

1. Mobile communication vs mobile computing; intermittent connectivity.
2. FDMA vs TDMA capacity and traffic utilisation.
3. DS-CDMA spreading, despreading, processing gain and near-far effects.
4. OFDMA subcarrier orthogonality, allocation, throughput and fairness.
5. SDMA uniform linear array patterns and angular separation.
6. Weighted access-method selection and deployment decisions.
7. Diagnosis, redesign and validation of a fairness bottleneck.

## Notes

Simulation figures are model outputs, not measurements from a live cellular network. Assumptions are documented in `Answers_Q1-Q7.md`; use the supplied seed to reproduce the random experiments.
