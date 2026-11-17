# Assignment 1 — Answers Q1–Q7

Numerical results below use the assumptions stated and fixed seed 197226. They are simulations, not measurements from a live network.

## Q1 — Mobile communication vs mobile computing

**Criteria:** (1) physical mobility of user/device; (2) wired vs wireless link; (3) ability to tolerate disconnection; (4) use of location/context; (5) battery, processing and storage constraints.

Wireless and mobile are not identical. A fixed wireless router is wireless but not mobile. A laptop used at different offices is nomadic even if each session uses wired Ethernet. Mobile communication focuses on connectivity while moving; mobile computing also includes local applications, processing, storage and continuity during disconnection.

| Case | Classification | Main area | Reason |
|---|---|---|---|
| Cellular rugged tablet | Mobile | Both, mainly computing | User moves; work-order application uses network data |
| Ethernet laptop at different offices | Nomadic | Computing | Location changes between sessions; wired while connected |
| Fixed substation wireless router | Fixed-wireless | Communication | Wireless access, fixed installation |
| Push-to-talk handset | Mobile | Communication | Real-time voice while moving |
| Offline meter-reading tablet | Mobile | Computing | Captures data offline and synchronises later |

**Ambiguous case:** a vehicle-mounted tablet using cellular data, GPS and a local cache. It is mobile and combines communication with computing. It needs offline maps, queued jobs, conflict handling and battery-aware synchronisation.

**Store-and-forward model:** 10,000 updates; immediate send loses updates attempted during an outage. Store-and-forward retains them until connectivity returns. The table uses the fixed-seed simulation's delay model (mean outage wait 2 minutes; connected transfer 0.02 minutes).

| Availability | Immediate delivered | Immediate lost | Store-forward delivered | Delayed | Mean delay (min) |
|---:|---:|---:|---:|---:|---:|
| 90% | 9,026 | 974 | 10,000 | 974 | 0.107 |
| 60% | 5,974 | 4,026 | 10,000 | 4,026 | 0.669 |
| 30% | 2,955 | 7,045 | 10,000 | 7,045 | 2.311 |

A wireless link alone does not provide durable storage, retries, duplicate prevention or conflict resolution. Offline meter apps and field tablets need local queues, timestamps, idempotent uploads, validation and sync-status feedback.

## Q2 — FDMA vs TDMA

Both schemes have 80 nominal channels. Assume FDMA loses 8% to guard bands/control: floor(80×0.92) = **73 usable**. Assume TDMA loses 12% to timing, synchronisation and control: floor(80×0.88) = **70 usable**. Equal nominal capacity is not equal usable capacity.

Predictions: continuous voice suits dedicated channels in either scheme; bursty 10%-duty data wastes FDMA reservations while TDMA can reuse idle slots; a 70/30 voice-data mix benefits from dynamic TDMA scheduling; synchronised arrivals can block either scheme.

| Traffic | Scheme | Requests | Blocked | Utilisation |
|---|---|---:|---:|---:|
| Continuous voice | FDMA | 5,148 | 0 | 50.818% |
| Continuous voice | TDMA | 5,148 | 0 | 52.996% |
| Bursty 10%-duty | FDMA | 8,499 | 0 | 2.817% |
| Bursty 10%-duty | TDMA | 8,499 | 0 | 2.938% |
| Synchronized 90-device edge | FDMA | 54,000 | 10,200 | 5.000% |
| Synchronized 90-device edge | TDMA | 54,000 | 12,000 | 5.000% |

The blocking counters reflect different allocation events. At a telemetry site where 90% of devices send 200 bytes per minute, dedicated channels are wasteful. Prefer scheduled shared access, aggregation or controlled grant-free access; reserve dedicated resources for strict latency/QoS needs.

## Q3 — DS-CDMA and near-far

A data bit is mapped to +1/−1 and multiplied by its spreading code. The receiver correlates received chips with the intended code and decides from the sign. Processing gain = 10 log10(L) dB.

| Length | Processing gain |
|---:|---:|
| 8 | 9.03 dB |
| 16 | 12.04 dB |
| 64 | 18.06 dB |

At eight users, 3,000 bits/user, noise σ=0.25, the observed BER was:

| Condition | L=8 | L=16 | L=64 |
|---|---:|---:|---:|
| Synchronous Walsh | 0.000000 | 0.000042 | 0.000000 |
| Random non-orthogonal | 0.167417 | 0.067792 | 0.006750 |
| Asynchronous near-far | 0.125750 | 0.125458 | 0.122250 |

For BER target 10⁻³, synchronous Walsh supports all eight tested users; random codes at length 64 support four but not eight; asynchronous near-far fails. Walsh orthogonality assumes alignment; timing offsets and multipath create cross-correlation. A 10× stronger user can overwhelm a weak user's detector, making power control essential.

## Q4 — OFDMA

Subcarrier spacing Δf gives useful symbol duration Tu=1/Δf. A cyclic prefix copies the symbol tail to its front; when it covers the channel delay spread, it limits inter-symbol interference and preserves orthogonality, at the cost of overhead. Distinct FFT basis vectors have zero inner product (up to numerical precision).

Simulation: 8 users, 64 tones, 1,000 fading realisations, SNR=10 linear. Per-tone rate is log2(1+SNR×gain).

| Allocation | Sum throughput (bps/Hz) | Jain fairness | Mean minimum user rate |
|---|---:|---:|---:|
| Fixed contiguous | 186.0999 | 0.97787 | 17.8444 |
| Interleaved round-robin | 185.8278 | 0.97735 | 17.8054 |
| Channel-aware best-tone | 299.9412 | 0.90131 | 19.6065 |

Greedy channel-aware allocation maximises sum rate by assigning tones to the strongest instantaneous channels, which can starve weak users. More users increase competition for favourable tones. For a lecture hall, use interleaved round-robin as a baseline plus an explicit per-interval minimum-rate admission/scheduling guard; a mean rate is not a guarantee.

## Q5 — SDMA array

For N equally spaced elements, array factor AF(θ)=Σ exp(jn(kd sinθ+β)), n=0…N−1, where k=2π/λ. For broadside steering d=λ/2 and β=0. Increasing N narrows the main lobe and improves angular separation. Define same-resource sharing as SIR≥10 dB.

| N | HPBW | First null | Peak sidelobe | Minimum 5°-grid separation for 10 dB SIR |
|---:|---:|---:|---:|---:|
| 2 | 60.01° | 90.00° | N/A | 55° |
| 4 | 26.33° | 30.00° | −11.30 dB | 25° |
| 8 | 12.81° | 14.48° | −12.80 dB | 15° |
| 16 | 6.36° | 7.18° | −13.15 dB | 10° |

Angular spread, multipath, calibration errors and clustered users limit SDMA. Users in nearly the same direction have similar spatial signatures and cannot be separated reliably by a simple array. At a toll plaza, most vehicles arrive from a similar direction; use time/frequency scheduling as the primary separation and SDMA only as a supplement.

## Q6 — Access-method selection

Weights: spectral efficiency 0.25, scalability 0.20, interference/jamming resilience 0.20, fairness/QoS 0.20, implementation/energy cost 0.15. Rate methods 1–5 using Q2–Q5 evidence.

| Deployment | Primary method | Score | Hybrid / justification |
|---|---|---:|---|
| Wide-area cellular voice | OFDMA | 4.05 | Scheduling and spatial reuse |
| Jam-resistant tactical link | CDMA | 3.75 | Spreading/frequency hopping and power control |
| High-rate stadium downlink | OFDMA | 4.20 | Combine with SDMA/MIMO |
| 5,000 low-rate sensors | OFDMA | 3.95 | Scheduled aggregation; TDMA/grant-free may save energy if OFDMA control cost dominates |

Changing each weight by ±20% and renormalising leaves most choices stable; the tactical choice is least robust and can flip under some perturbations. Systems combine techniques because no single access method optimises capacity, mobility, QoS, interference and energy simultaneously.

## Q7 — Diagnose, redesign and validate

**Chosen bottleneck:** greedy best-subcarrier OFDMA can starve weak users. Strong users receive a disproportionate share of tones; fairness was about 0.900 and the weakest user received about 19.21 bps/Hz.

**Objective:** improve minimum-user throughput and Jain fairness while keeping sum-rate loss below 5%.

**Redesign:** reserve at least four tones per user, then assign remaining tones using a proportional-fair metric: instantaneous rate divided by the user's running average rate. This uses channel state while preventing a user from receiving no resources.

Pseudocode:
1. Initialise each user's allocation.
2. Give each user its four best currently unassigned tones.
3. For each remaining tone, calculate rate(user,tone)/(average_rate(user)+ε).
4. Assign the tone to the user with the largest metric and update its average.
5. Measure sum throughput, fairness and minimum user rate.

Prediction: a small sum-rate reduction should be accompanied by a large increase in fairness and minimum rate.

| Measure | Original greedy | Redesigned |
|---|---:|---:|
| Sum throughput (bps/Hz) | 299.9462 | 295.0092 |
| Jain fairness | 0.90024 | 0.99196 |
| Minimum user throughput | 19.2065 | 31.9318 |
| Maximum user throughput | 57.7286 | 41.9935 |
| Mean minimum tones/user | 4.141 | 6.929 |
| Mean maximum tones/user | 12.260 | 9.095 |

Sum rate falls about 1.65%, fairness rises to 0.992, and minimum-user throughput improves about 66.2%. The prediction is supported. The trade-off is scheduler state and extra per-tone computation. Greedy allocation remains suitable when total throughput is the only objective and no minimum user rate is required.

## Run instructions

Install NumPy with `pip install -r requirements.txt`, then run `python src/assignment1.py`. The program writes question-wise CSV and combined JSON files under `results/`. Seed: 197226.
