# Assignment 2 — Mobile Computing (Q1–Q7)

**Implementation:** Python 3 + NumPy  
**Random seed:** `20261119`  
**Realisations:** 1,000 for OFDMA and Q7; Q1 uses 10,000 updates; Q3 uses 4,000 transmitted bit intervals per code length/user-count/condition.

All figures are simulation outputs under the assumptions stated below. They are not measurements from a live cellular network.

---

## Q1 — Mobile Communication or Mobile Computing? (5 marks)

### Classification criteria

1. **Physical mobility:** can the user/device move while operating?
2. **Access medium:** wired or wireless?
3. **Session continuity:** can the application keep working during disconnection?
4. **Context awareness:** does it use location, time or device context?
5. **Local resources:** does it depend on local processing, storage and battery?

Wireless and mobile are not synonyms. A fixed wireless router is wireless but not mobile. A laptop carried between offices is nomadic, even if it connects through Ethernet. Mobile communication concerns connectivity while moving; mobile computing also includes local processing, applications, storage and work continuity.

| Case | Classification | Main problem | Reason |
|---|---|---|---|
| Rugged tablet fetching work orders over cellular | Mobile | Both; mainly mobile computing | It moves and uses wireless data, but the work-order application must manage network changes, local data and battery |
| Laptop connected to Ethernet at different offices | Nomadic | Mainly mobile computing | The user changes location between sessions, but the active link is wired |
| Fixed wireless router at remote substation | Fixed wireless | Mainly mobile communication | Wireless access is provided at a fixed location |
| Push-to-talk handset | Mobile | Mainly mobile communication | Voice connectivity must continue while the user moves |
| Offline meter-reading tablet | Mobile | Mainly mobile computing | Data is recorded locally and synchronised after connectivity returns |

**Additional ambiguous case:** a vehicle-mounted service tablet using cellular data, GPS and a local job cache. It is mobile and uses mobile communication, but offline job execution, map caching, conflict handling and synchronisation make it a mobile-computing problem too.

### Store-and-forward simulation

10,000 meter updates are attempted. Immediate send succeeds only when the link is available at the attempt. Store-and-forward queues an update and retries once per minute until a connection is available. A successful transfer adds 0.02 minute of transfer time.

| Link availability | Immediate delivered | Immediate lost | Store-forward delivered | Delayed in queue | Store-forward lost | Mean store-forward delay (min) |
|---:|---:|---:|---:|---:|---:|---:|
| 90% | 9,027 | 973 | 10,000 | 973 | 0 | 0.1277 |
| 60% | 5,944 | 4,056 | 10,000 | 4,056 | 0 | 0.7023 |
| 30% | 2,981 | 7,019 | 10,000 | 7,019 | 0 | 2.3626 |

**Conclusion:** a wireless link alone does not provide durable storage, retry logic, duplicate prevention, data validation or conflict resolution. Offline meter tablets, field-service tablets and vehicle-mounted terminals need application-level queues, timestamps, idempotent uploads, sync status and local storage.

---

## Q2 — Sharing the Channel: FDMA vs TDMA (6 marks)

### Usable capacity assumptions

Both alternatives are specified as 80 nominal channels in the 2 MHz band per direction. For a transparent estimate, assume:

- FDMA: 8% capacity loss for guard bands and control → `floor(80 × 0.92) = 73` usable channels.
- TDMA: 12% capacity loss for guard times, synchronisation and control → `floor(80 × 0.88) = 70` usable channels.

These are illustrative overhead assumptions, not standard-mandated values. Actual capacity depends on system framing and implementation.

### Predictions

- **Continuous voice:** dedicated channels work well because each call occupies a resource continuously. TDMA has 70 usable channels versus FDMA's 73 in this overhead model.
- **Bursty 10%-duty data:** dedicated allocation wastes most reservations while a device is idle. A dynamically scheduled shared system would use capacity more efficiently than either fixed reservation.
- **70/30 voice-data mix:** voice needs predictable resource holding; bursty data should use shared/dynamic slots. A hybrid scheduler is preferable to reserving a full channel for every data terminal.
- **Synchronized-arrival edge case:** simultaneous requests can exceed available channels and cause blocking.

### Simulation

The program models four traffic cases and dedicated-channel allocation. For the mixed case, 70 voice users are assumed with a 70% active interval, giving 49 active resources in the measured interval; the data component is treated as bursty rather than a permanent reservation.

| Dataset | Scheme | Usable channels | Offered active users | Blocked | Utilisation | Idle channels |
|---|---|---:|---:|---:|---:|---:|
| Continuous voice (70 active) | FDMA | 73 | 70 | 0 | 95.89% | 3 |
| Continuous voice (70 active) | TDMA | 70 | 70 | 0 | 100% | 0 |
| Bursty 10% duty (70 devices) | FDMA | 73 | 7 | 0 | 9.59% | 66 |
| Bursty 10% duty (70 devices) | TDMA | 70 | 7 | 0 | 10.00% | 63 |
| Mixed 70/30 (49 active interval) | FDMA | 73 | 49 | 0 | 67.12% | 24 |
| Mixed 70/30 (49 active interval) | TDMA | 70 | 49 | 0 | 70.00% | 21 |
| 90 synchronised arrivals | FDMA | 73 | 90 | 17 | 100% | 0 |
| 90 synchronised arrivals | TDMA | 70 | 90 | 20 | 100% | 0 |

**Where they diverge:** the usable capacity differs because of overhead. Dedicated-channel utilisation depends on how many users are active at the same time; burstiness creates idle reservations, while synchronised demand creates blocking.

**Campus telemetry decision:** dedicated FDMA/TDMA allocation is not justified when 90% of devices send only a 200-byte report per minute. Use scheduled shared access, aggregation or a low-power random-access method with collision control. Reserve dedicated resources for devices with strict latency or guaranteed-QoS needs.

---

## Q3 — CDMA: Orthogonality, Spreading and Near-Far (7 marks)

### Operation and processing gain

For each data bit (b in {-1,+1}), the transmitter multiplies the bit by a length-(L) spreading code. The receiver correlates the received chip sequence with the intended code and decides from the sign of the correlation.

[
G_p = 10log_{10}(L)	ext{ dB}
]

| Code length | Processing gain |
|---:|---:|
| 8 | 9.03 dB |
| 16 | 12.04 dB |
| 64 | 18.06 dB |

### Predictions before execution

- Synchronous Walsh codes should have zero pairwise cross-correlation and low BER in the ideal aligned model.
- Random non-orthogonal codes should produce more multi-user interference as the number of users rises; longer codes should reduce average cross-correlation.
- A user transmitting at ten times the power can dominate a weak user's correlator, especially when timing is offset and orthogonality is lost.

### Simulation evidence

The implementation tests 2, 4 and 8 users; lengths 8, 16 and 64; and 4,000 bit intervals per user/condition. The near-far case uses Walsh codes but shifts the strongest user's code by one chip and raises its power to 10×.

For eight simultaneous users:

| Length | Condition | Bits tested | Bit errors | BER |
|---:|---|---:|---:|---:|
| 8 | Synchronous Walsh | 32,000 | 0 | 0.000000 |
| 8 | Random codes | 32,000 | 4,480 | 0.140000 |
| 8 | 10× near-far, 1-chip offset | 32,000 | 6,059 | 0.189344 |
| 16 | Synchronous Walsh | 32,000 | 0 | 0.000000 |
| 16 | Random codes | 32,000 | 2,136 | 0.066750 |
| 16 | 10× near-far, 1-chip offset | 32,000 | 5,977 | 0.186781 |
| 64 | Synchronous Walsh | 32,000 | 0 | 0.000000 |
| 64 | Random codes | 32,000 | 58 | 0.001813 |
| 64 | 10× near-far, 1-chip offset | 32,000 | 6,025 | 0.188281 |

**Inquiry:** orthogonality assumes correct timing and aligned code boundaries. An offset changes the correlation between users' codes. Unequal received powers let a strong user overwhelm a weak user's signal. Power control is essential so the base station receives users at reasonably balanced power levels.

For a target BER of (10^{-3}), the ideal synchronous Walsh simulation supports all eight tested users at all three lengths. The random length-64 result is close but above the target (0.001813); the near-far case fails. This is a simulation-based estimate, not a universal CDMA user capacity.

---

## Q4 — OFDMA: Subcarrier Allocation (6 marks)

### Symbol duration and cyclic prefix

For subcarrier spacing (Delta f), the useful OFDM symbol duration is:

[
T_u = rac{1}{Delta f}
]

A cyclic prefix copies the end of the symbol to its beginning. If its duration covers the channel's significant delay spread, it reduces inter-symbol interference and helps preserve subcarrier orthogonality. It adds overhead and therefore reduces useful payload time.

### Numerical orthogonality check

For a 64-point DFT, different basis subcarriers have zero normalised inner product in exact arithmetic. The program checks three pairs:

| Subcarrier pair | Absolute normalised inner product |
|---|---:|
| 1 and 2 | 0.0 |
| 3 and 11 | 0.0 |
| 17 and 42 | 0.0 |

### Allocation simulation

Eight users share 64 subcarriers. The implementation generates independent frequency-selective Rayleigh power gains and evaluates 1,000 realisations at SNR=10 (linear), using (R=log_2(1+mathrm{SNR}cdot g)).

| Allocation | Sum throughput (bps/Hz) | Jain fairness | Minimum user rate (bps/Hz) |
|---|---:|---:|---:|
| Fixed contiguous blocks | 186.22587 | 0.999961 | 23.07598 |
| Interleaved round-robin | 186.23150 | 0.999961 | 22.91487 |
| Channel-aware best-subcarrier | 300.16969 | 0.999815 | 36.58590 |

Channel-aware allocation has the highest sum throughput in this independent, identically distributed fading experiment. Fairness remains high because many tones and 1,000 realisations average out user differences. In a finite interval or with persistently weak users, a greedy scheduler can repeatedly select stronger users and starve others.

**Design decision:** for a lecture hall, use proportional-fair or round-robin scheduling with an explicit minimum-rate guarantee. The minimum rate is a policy/QoS target that the scheduler must enforce; a high average rate or Jain index alone is not a guarantee.

---

## Q5 — SDMA: Directional Antenna Reuse (6 marks)

### Array factor

For an (N)-element uniform linear array with element spacing (d), wavenumber (k=2pi/lambda), and progressive phase (eta):

[
AF(	heta)=sum_{n=0}^{N-1}e^{jn(kdsin	heta+eta)}
]

The simulation uses half-wavelength spacing, broadside steering and normalises the peak array factor to one. Increasing (N) narrows the main lobe, improving angular separation. Sidelobe level depends on the array weighting; a uniform amplitude array has sidelobes around −13 dB for larger N.

### Pattern and SIR results

The same-resource sharing threshold is **SIR ≥ 10 dB**. The table gives the smallest tested 5° angular separation meeting the threshold.

| Elements | HPBW | First null | Peak sidelobe | Minimum separation for 10 dB SIR |
|---:|---:|---:|---:|---:|
| 2 | 60.01° | 87.96° | Not resolved | 55° |
| 4 | 26.33° | 29.98° | −11.303 dB | 25° |
| 8 | 12.81° | 14.47° | −12.797 dB | 15° |
| 16 | 6.36° | 7.18° | −13.147 dB | 10° |

The 2-element array does not produce a distinct sidelobe region in this sampled broadside pattern, so its sidelobe level is not reported.

**Practical limits:** multipath, angular spread, calibration error, finite antenna size and users clustered in the same direction reduce spatial separation. Two users arriving from nearly the same angle have similar spatial signatures and cannot be separated reliably by beamforming alone.

**Toll-plaza decision:** do not rely only on SDMA because most vehicles approach from similar directions. Use time/frequency scheduling as the primary separation method and directional beams as a supplement.

---

## Q6 — Choosing Access Methods (7 marks)

### Weighted criteria

Ratings use a 1–5 scale (5 = strongest). Weights total 100%.

| Criterion | Weight | Reason |
|---|---:|---|
| Spectral efficiency | 25% | Important when spectrum is limited |
| Scalability | 20% | Supports growing user/device counts |
| Interference resilience | 20% | Important in crowded or contested bands |
| Fairness and QoS | 20% | Protects users with service requirements |
| Implementation and energy cost | 15% | Matters for terminals and large deployments |

The per-method ratings are recorded in `results/Q6_weighted_ratings.csv`; they are engineering judgements informed by the Q2–Q5 experiments, not universal standards scores.

### Weighted outcomes

| Deployment | Highest weighted method | Score | Recommended design |
|---|---|---:|---|
| Wide-area cellular voice | OFDMA | 4.50 | OFDMA with scheduling and SDMA/MIMO spatial reuse |
| Jam-resistant tactical link | CDMA | 4.05 | CDMA/spreading with strict power control; use frequency agility and robust coding where available |
| High-rate stadium downlink | OFDMA | 4.30 | OFDMA plus SDMA/MIMO; fairness-aware scheduling |
| 5,000 low-rate sensors | OFDMA | 4.10 | Scheduled OFDMA/aggregation; consider TDMA where battery simplicity is more important than peak spectrum efficiency |

### Sensitivity

Each criterion weight was changed independently by −20% and +20%, with all weights renormalised after each change. The selected method remained the same in all tested perturbations: OFDMA for wide-area voice, stadium downlink and the sensor deployment; CDMA for the tactical link.

Real systems combine methods because each solves a different part of the problem. FDMA can separate carriers, TDMA can divide each carrier into time slots, and coding/spatial scheduling can further manage interference and capacity. The tactical selection is the least transferable because its result depends strongly on the assumed interference/jamming environment and power-control capability.

---

## Q7 — Diagnose, Redesign and Validate (13 marks)

### A. Diagnose the bottleneck

The selected limitation is **best-subcarrier OFDMA under strongly unequal user channel quality**. The original scheduler assigns each tone to the user with the largest instantaneous rate. When 20 of 60 users have only 20% of the average channel gain of the other 40 users, weak users can lose every tone in an interval. In the 1,000-realisation experiment, the original minimum user rate is 0 and Jain fairness is 0.666260.

### B. Measurable objective

Guarantee at least one subcarrier to every admitted user in each scheduling interval, raise Jain fairness above 0.90, and keep the sum-throughput reduction within a stated 20% trade-off budget.

### C. Revised strategy

The revised scheduler first reserves each user their best available tone, then allocates the remaining tones using a proportional-fair metric:

[
M(u,k)=rac{R(u,k)}{ar R_u+epsilon}
]

where (R(u,k)) is the instantaneous rate for user (u) on tone (k), and (ar R_u) is the user's running average rate.

**Pseudocode**

1. Generate per-user, per-tone channel rates.
2. Mark all tones unassigned.
3. In a shuffled user order, give each user their best unassigned tone.
4. For each remaining tone, compute (R(u,k)/(ar R_u+epsilon)).
5. Assign the tone to the user with the largest metric and update that user's average.
6. Measure sum throughput, minimum user rate and Jain fairness.

The redesign adds scheduler state and computation, but avoids leaving a weak user with no allocated resource.

### D. Prediction before validation

The minimum user rate should become non-zero and Jain fairness should increase. Sum throughput is expected to decrease because some tones are reserved for users with weaker instantaneous channels.

### E. Validation

The same 60-user, 64-subcarrier, 1,000-realisation test is used for both strategies. Forty users have unit mean channel gain; twenty users have mean gain 0.20.

| Measure | Original best-subcarrier | Redesigned (minimum one tone/user) |
|---|---:|---:|
| Sum throughput (bps/Hz) | 345.30934 | 289.02607 |
| Jain fairness | 0.666260 | 0.947084 |
| Minimum user rate (bps/Hz) | 0.00000 | 3.16143 |
| Maximum user rate (bps/Hz) | 9.06796 | 5.72559 |
| Average minimum tones/user | 0.000 | 1.031 |
| Average maximum tones/user | 1.678 | 1.100 |

### F. Final defence

The prediction was supported. Jain fairness improved by about 42.2% relative to the original value, and the minimum user rate rose from zero to 3.16143 bps/Hz. Sum throughput fell by about 16.3%, within the 20% design budget. The new cost is additional scheduling state and per-tone metric computation. The original greedy scheduler remains preferable when maximum aggregate throughput is the only objective and weak-user service guarantees are not required.

---

## Reproducibility and files

Run from the repository root:

```bash
python -m pip install -r "Assignment 2/requirements.txt"
python "Assignment 2/src/assignment2.py"
```

The program writes question-wise CSV files and `results/all_results.json`. All random experiments use seed `20261119`.
