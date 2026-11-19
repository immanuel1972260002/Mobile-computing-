# Assignment 5 — Mobile Computing (50 Marks)

Completed question-wise submission for Part A (A1–A5) and Part B (B1–B4).

- `Answers_Part_A.md` — design answers, language-independent pseudocode, trace and classification.
- `Answers_Part_B.md` — implementation, tests, measurements and engineering decision.
- `patterns/` — architecture and reusable algorithm patterns.
- `data/` — workloads, test cases and device profiles.
- `src/` — runnable Python simulations and smoke tests.
- `results/` — deterministic captured console outputs.

Run from repository root:
```bash
python3 "Assignment 5/src/background_pipeline.py"
python3 "Assignment 5/src/feed_optimizer.py"
python3 "Assignment 5/src/video_encoder_selector.py"
cd "Assignment 5/src" && python3 -m unittest -v
```

**Evidence limitation:** These are deterministic platform-independent simulations, not a compiled Android APK or physical-device benchmark. Energy/frame-cost values are illustrative estimates. Real Android mapping: WorkManager for durable deferrable work, foreground services only for user-visible time-critical work, and permission/consent rechecks before sensitive operations.

Workflow: UNDERSTAND → DESIGN → CONSTRAINT-CHECK → IMPLEMENT → MEASURE → CHALLENGE → INTERPRET.