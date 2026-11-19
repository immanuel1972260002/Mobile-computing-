# PART B — Implementation & Computational Investigation (25 marks)

## Implementation note
These are deterministic platform-independent Python simulations. They model Android-style durable workers, permission checks, Doze, network and battery constraints; they are **not** an installed Android APK and do not claim physical-device energy measurements. Run from repository root:

\`\`\`bash
python3 "Assignment 5/src/background_pipeline.py"
python3 "Assignment 5/src/feed_optimizer.py"
python3 "Assignment 5/src/video_encoder_selector.py"
cd "Assignment 5/src" && python3 -m unittest -v
\`\`\`

## B1 — Instrumented background architecture (7)
The background simulator records enqueued, processed, deferred, cancelled, successful, peak worker count, residual backlog and battery/network/Doze state at each decision. It runs one worker at a time; peak concurrency is 1 when a worker starts and 0 otherwise.

### B1.1 Validation (2)
| Test | Setup | Observed | Verification |
|---|---|---|---|
| Good connectivity | Battery 85%, good network, no Doze, permission granted, 3 encrypted records | 3 successful, 0 deferred/cancelled, backlog 0 | Normal queue selection and acknowledgement |
| Doze + low battery | Battery 12%, good network, Doze active, 2 records | 2 deferred, 0 uploads, backlog 2 | Deferral preserves data and avoids background execution |
| Permission revoked mid-execution | Granted at enqueue/start, revoked before upload commit point | 1 cancelled, 0 uploads | Re-check authority after worker start; do not commit partial work |

### B1.2 Design vs implementation (1)
The implementation uses a deterministic event-loop simulator and serial worker rather than Android APIs, making decisions reproducible. Real Android mapping: WorkManager for durable deferrable uploads, foreground service only for user-visible time-critical activity, explicit intents for internal communication. Permission is revalidated immediately before commit to model revocation after enqueue/start.

### B1.3 Scheduling order (2)
- **Version 1 FIFO:** preserve arrival order.
- **Version 2 priority:** descending clinical priority, then smaller payload first to reduce radio time, then stable ID. This lexicographic policy never bypasses consent, encryption, permission or Doze checks.

### B1.4 Effect (2)
| Measure | FIFO | Priority |
|---|---:|---:|
| Enqueued | 4 | 4 |
| Deferred/cancelled | 0 / 0 | 0 / 0 |
| Successful | 4 | 4 |
| Peak concurrency | 1 | 1 |
| Order | low, critical, medium, high | critical, high, medium, low |

Total work is unchanged in this all-feasible test; priority improves time-to-first-critical-record (critical moves from second to first). Under an offline constraint affecting all records, ordering cannot create feasibility or reduce total deferrals. Full outputs are in \`results/B1_B2_background_metrics.txt\`.

## B2 — Adversarial workload (5)
Both workloads contain six records and use the same thresholds: minimum battery 20%, network must be good, Doze off, sensitive records encrypted, permission/consent required.

- **A prediction:** all records encrypted, battery 90%, good network, no Doze → six successful deliveries, no deferral.
- **B prediction:** one sensitive record unencrypted; network poor for all remaining records → one security rejection, five deferrals, no successful upload.

| Metric | A observed | B observed |
|---|---:|---:|
| Enqueued | 6 | 6 |
| Processed decisions | 6 | 6 |
| Deferred | 0 | 5 |
| Cancelled/rejected | 0 | 1 |
| Successful deliveries | 6 | 0 |
| Residual backlog | 0 | 5 |

Workload B combines an invalid security state and a network state blocking every otherwise valid upload. Its difficulty comes from constraint density and retry/backlog structure, not count. Input size alone hides sensitivity, payload size, conflict/dependency structure and retry probability, which drive radio wakeups, CPU work and energy.

## B3 — Exact vs approximate feed optimisation (8)
The feed program enumerates 27 configurations for 3 quality × 3 cache × 3 prefetch choices. Synthetic objective: 10 × estimated frame drops + estimated energy units. Adaptive policy uses a bounded four-step rule based on frame time and battery. These are transparent simulations, not GPU benchmarks.

### B3.1 Three cases (2)
| Instance | Exact minimum cost/config | Approx cost/config | Match |
|---|---|---|---|
| Balanced | 13 at (3,1,1) | 47 at (1,1,1) | No |
| Low-end | 21 at (3,3,2) | 84 at (1,1,1) | No |
| Video-heavy | 19 at (2,3,2) | 79 at (1,1,1) | No |

The conservative policy lowers quality under its starting frame-time signal; it may meet feasibility but not global cost minimum.

### B3.2 Counter-example (2)
For the non-convex \`trap\` surface, exhaustive search finds cost 8 at (1,3,0). Adaptive starts at (3,1,1); measured frame time is 15.2 ms, so it judges the setting steady and stops at cost 19. The stopping rule (“below 16 ms”) optimises feasibility, not global energy; the better basin is not explored.

### B3.3 Scale counts (2)
| Feed items | Quality levels | Exact configurations (Q×C×P, P=3) | Adaptive decision steps |
|---:|---:|---:|---:|
| 10 | 3 | 27 | 4 |
| 100 | 6 | 108 | 4 |
| 1,000 | 10 | 300 | 4 |

Counts are configuration evaluations/decision steps, not GPU draw calls. A full exact cost simulation also grows with feed length, approximately O(N×Q×C×P). Adaptive controller steps are bounded here, though actual rendering still scales with visible items.

### B3.4 Trade-off (2)
Approximation gains bounded decision effort and fast reaction without enumerating the configuration space. It sacrifices global optimality and can return higher cost. It is reasonable for a live feed where missing the 16 ms budget is worse than temporary energy inefficiency, provided quality floors/memory caps hold and telemetry enables retuning.

## B4 — Multimedia engineering decision (5)

### B4.1 Practical strategy (2)
The video selector chooses the highest supported resolution/bitrate under CPU, battery and network caps. It estimates upload time for a 20-second clip, encode/radio energy units and remaining battery. It queues upload until unmetered network/charging for low battery or poor connectivity.

| Device | Resolution | Bitrate | Upload timing | Est. upload | Est. energy | Battery after |
|---|---:|---:|---|---:|---:|---:|
| Budget phone | 480p | 0.8 Mbps | Queue until unmetered/charging | 8.0 s | 2.61 | 19.39 |
| Midrange | 1080p | 4.0 Mbps | Upload now | 10.0 s | 3.40 | 54.60 |
| Flagship | 2160p | 12.0 Mbps | Upload now | 9.6 s | 3.98 | 78.02 |
| Wi-Fi, low battery | 720p | 1.8 Mbps | Queue until unmetered/charging | 0.5 s | 1.62 | 10.38 |

Estimates are illustrative and must be calibrated against device telemetry before production use.

### B4.2 Challenge (1)
A custom device with CPU score 0.85, battery 19%, 40 Mbps Wi-Fi and a 2160p camera is capped at 720p and queued. For a three-second clip, a carefully modelled 1080p encode may fit the thermal/energy budget and provide better quality. The fixed battery threshold ignores clip duration and can be suboptimal.

### B4.3 Production decision note (2)
**Decision:** use a conservative on-device heuristic for immediate parameter selection, with a server-provided policy table updated from fleet telemetry. Exhaustive resolution × bitrate × codec × upload-window search on every capture adds latency/CPU/battery and multiplies across hardware profiles and changing networks. The heuristic guarantees only that selected settings satisfy declared caps; it does **not** guarantee minimum energy or maximum quality. It reduces decision cost to a few profile checks and avoids repeated search. Exact search suits offline tuning of a small calibrated device matrix; cloud-assisted selection can use coarse capability metadata and a signed policy, without uploading raw video merely to decide encoding. Monitor p50/p95 encode time, upload completion, battery delta, thermal throttling, crashes, bitrate adaptation, user-visible quality, network bytes and retry rates. Deploy gradually with a safe fallback.

## Overall conclusion
Equal task counts can have different execution costs because feasibility, security, connectivity and workload structure govern useful work. A sound mobile design persists state, checks authority/resources before execution, defers transient failures, rejects unsafe work and instruments outcomes. Heuristics improve responsiveness and bounded decision cost, but quality/energy trade-offs must be measured.
