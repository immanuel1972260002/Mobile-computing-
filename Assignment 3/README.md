# Assignment 3 — Mobile Computing

## Contents
- `Answers_Q1-Q7.md`: written answers, architecture sketches, comparison tables and design justification.
- `patterns/Algorithms.md`: language-independent pseudocode for discovery, Mobile IP, handoff, DSDV, AODV and emergency forwarding.
- `src/mobile_network_sim.py`: executable deterministic educational model.
- `data/`: input scenarios for mobility and routing tests.
- `results/`: reproducible output CSVs and run summary.

## Run the program
From the repository root:

```bash
python "Assignment 3/src/mobile_network_sim.py"
```

Python 3.10+; no third-party packages required.

## Important interpretation
The script is an illustrative analytical model, not a packet-level wireless simulator. Its outputs demonstrate trends under explicit simplified assumptions and must not be represented as physical measurements or ns-3 results. The written answers distinguish protocol concepts from model-generated values.


## Question-wise implementation folders

The `Q1_Wireless_Network_Architecture`, `Q2_Mobile_IP`, `Q3_Cellular_vs_AdHoc`, `Q4_Mobile_IP_Applications`, `Q5_Proactive_DSDV`, `Q6_Reactive_AODV_Comparison`, and `Q7_Emergency_Communication_Network` folders provide question-by-question answers, input data, standard pseudocode, runnable Python demonstrations, and sample output files. Q3–Q7 also include a combined `README.md` for each question.
