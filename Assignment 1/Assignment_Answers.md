# Assignment 1 – Frequency Planning for a Cellular Township

## Common assumptions
Service area = 12 km²; total channel equivalents S = 420; nominal cell radius R = 0.5 km; busy-hour traffic = 0.02 Erlang/subscriber; target blocking = 2%. These are illustrative assumptions because the brief does not provide a measured traffic map, channel allocation, propagation data or site-cost schedule.

## Q1. Design alternative frequency-planning strategies
1. **Fixed frequency reuse:** Divide spectrum into N groups and repeat them over a hexagonal grid. Valid cluster sizes satisfy N = i² + ij + j². Reuse distance D = R√(3N), channels/cell ≈ S/N. It is simple and predictable, but uniform fixed allocation can waste capacity in low-load cells.
2. **120° sectoring:** Use three directional antennas per site. Directional filtering reduces the number of dominant co-channel interferers (ideally from six to about two). It improves SIR without new spectrum, but adds antennas and may create sector load imbalance.
3. **Dynamic channel assignment/channel borrowing:** Assign a free channel when a call arrives, excluding channels active in interfering neighbours. Borrow from a lightly loaded neighbour only when interference constraints remain satisfied. It improves pooling under uneven traffic but needs fast measurements, control signalling and a neighbour map.
4. **Hierarchical macro–micro layer:** Keep macrocells for broad coverage and add micro/pico cells in persistent hotspots. Halving radius approximately quadruples cell density. It localizes capacity but increases site, backhaul and handoff costs.

## Q2. Governing parameters
- Fixed reuse: cluster size N / reuse ratio Q = √(3N).
- Sectoring: antenna discrimination and effective number of first-tier interferers.
- Dynamic assignment: number of currently free non-conflicting channels.
- Hierarchical splitting: cell radius R; cell density scales as 1/R².

For rising subscriber counts, use measured hotspot loads rather than increasing N alone. Sectoring, pooling and localized splitting address different bottlenecks.

## Q3. Capacity and interference functions
Hexagonal cell area:
A_h = 6(√3/4)R² = (3√3/2)R².
At R = 0.5 km, A_h ≈ 0.6495 km² and 12/A_h ≈ 18.48, or about 19 ideal cells before edge/overlap margin.

Reuse geometry:
D = R√(3N), Q = √(3N). For N = 7, Q = √21 ≈ 4.583.

Channels per cell:
C = floor(S/N). With S = 420 and N = 7, C = 60.

Erlang-B blocking:
B(0,A)=1 and B(C,A)=A·B(C−1,A)/(C+A·B(C−1,A)).
Numerically find the largest offered traffic A_c with B(C,A_c) ≤ 0.02. Approximate network capacity is cell_count × A_c.

Co-channel SIR:
SIR = r^(−n) / Σ(d_m^(−n)).
For i₀ equal-distance interferers at D, cell edge r=R:
SIR ≈ (D/R)^n / i₀ = (3N)^(n/2)/i₀.
For N=7, n=4 and six interferers, SIR = 10log₁₀(441/6) ≈ 18.67 dB. With two ideal dominant sector interferers, it is ≈ 23.44 dB.

Lifecycle cost can be compared using survey cost, per-site cost, sector upgrade cost, controller cost and micro-site/backhaul cost. Monetary values cannot be justified without a supplied cost schedule.

## Q4. Best, average and worst cases
- Best SIR: mobile near serving base station; desired signal is strongest.
- Average SIR: mobile at a typical interior position with ordinary shadowing.
- Worst SIR: cell edge/corner or sector boundary, where desired signal is weaker and nearby co-channel cells can be strong.
- Best blocking: off-peak low offered traffic.
- Average blocking: normal busy-hour traffic.
- Worst blocking: event surge or overloaded sector.
Lognormal shadowing broadens the SIR distribution. A larger path-loss exponent reduces distant interference but makes coverage more sensitive to distance and obstacles.

## Q5. Scaling and sensitivity
Channels/cell scale approximately as S/N. Approximate SIR scales as N^(n/2)/i₀. Cell count in a fixed area scales as 1/R²; halving R yields about four times as many cells. Under the assumed traffic rate, demand is 20 E at 1,000 subscribers, 200 E at 10,000, 400 E at 20,000 and 2,000 E at 100,000. Fixed reuse suits stable uniform demand; dynamic assignment suits uneven loads; sectoring suits interference-limited sites; microcells suit persistent hotspots.

## Q6. Recurrence for cell splitting
For uniform four-way splitting:
M_k = 4M_(k−1), R_k = R_(k−1)/2, C_k = 4C_(k−1).
An idealized child transmit-power relation is P_k = P_(k−1)/2^n. For selective splitting where fraction f_k of cells is split:
M_k = M_(k−1)(1+3f_k), and under equal child-capacity assumptions aggregate capacity scales by the same factor. More cells increase handoffs and coordination.

## Q7. Solve the recurrence
Repeated substitution gives C_k = 4^k C_0. To support demand D:
k_min = ceil(log₄(D/C₀)) when D > C₀, otherwise zero.
For constant selective split fraction f:
C_k = C₀(1+3f)^k and k_min = ceil(log(D/C₀)/log(1+3f)).
Selective splitting avoids multiplying every site when only a few hotspots are overloaded.

## Q8. Implementation and tests
The Python program implements hexagonal area, valid cluster sizes, Erlang-B recursion and inversion, a first-tier SIR estimate, a dynamic allocation example and cell-splitting recurrence. Run the commands in README. The test checks geometry, cluster values, blocking and recurrence calculations. The N=7, n=4 analytical cell-edge SIR check is approximately 18.67 dB.

## Q9. Experimental performance
The program writes:
- `results/capacity_experiments.csv` – capacity estimates across N and subscriber levels.
- `results/sir_experiments.csv` – SIR summary across path-loss exponents and sectoring cases.
- `results/event_surge.json` – event demand and density calculation.
- `results/cell_splitting_recurrence.csv` – cell count/capacity by split round.
Results should be compared at equal traffic, seed, channel pool and propagation assumptions.

## Q10. Theory versus simulation
The 18.67 dB analytical result assumes a cell-edge mobile and six equal-distance first-tier interferers. A location-sampled simulation uses unequal distances and therefore produces a distribution rather than the same single value. Erlang-B assumes Poisson arrivals, exponential holding times and a fixed loss-system circuit pool. Real handoffs, correlated arrivals, terrain, shadowing, antenna side lobes and adjacent-channel interference explain differences. Treat simulation as comparative planning, not a field guarantee.

## Q11. Recommended design
Use a **hybrid design**: fixed-reuse macro layer for continuous coverage, 120° sectoring at high-load/interference-limited sites, dynamic channel assignment or coordinated resource scheduling for short-term imbalance, and selective microcells in persistent hotspots. N=7 is a reasonable starting comparison point under the stated assumptions, not a final licensed plan. Validate with a propagation survey, actual spectrum, busy-hour traffic and local site costs.

## Q12. Event-day surge
Event demand = 25,000 × 0.05 = 1,250 Erlangs in 1 km². At 100,000 township subscribers, assumed baseline demand is 2,000 E over 12 km², or 166.7 E/km²; event density is about 7.5 times the township average. A 60-channel/cell N=7 plan is unlikely to absorb this concentrated load in only one or a few sectors. Deploy temporary cells-on-wheels/small cells around the stadium, directional sectors, dynamic borrowing, coordinated macro/micro channels, additional backhaul and power. Calculate the final number of temporary cells from measured event arrival patterns and Erlang-B capacity with a safety margin. With two four-hour events per month, temporary localized capacity is a sensible first option; make sites permanent only if measurements show recurring non-event congestion.

## Conclusion
Fixed reuse gives a stable baseline; sectoring improves spatial isolation; dynamic assignment improves statistical pooling; and hierarchical splitting localizes capacity. A measured hybrid macro network with temporary event capacity is the most defensible approach under the stated assumptions.
