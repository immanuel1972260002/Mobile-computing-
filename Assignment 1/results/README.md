# Generated results

Run `python ../src/planner.py --out .` from this directory (or use the root README command) to generate:

- `capacity_experiments.csv`: Erlang-B capacity and blocking estimates for N = 3, 4, 7, 12 and 1k–100k users.
- `sir_experiments.csv`: ideal cell-edge SIR estimates for path-loss exponents 2.5, 3 and 4, with six-interferer and ideal sectorized two-interferer cases.
- `event_surge.json`: stadium event traffic estimate.
- `cell_splitting_recurrence.csv`: relative cell count, capacity and radius by split round.

All values are estimates based on the assumptions documented in the parent README.
