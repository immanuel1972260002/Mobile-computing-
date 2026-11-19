# Assignment 3 — Mobile Computing
**SIMATS Engineering | Mobile Computing**

This submission answers Q1–Q7 from the supplied assignment sheet. Each answer follows the question's mark allocation and includes a technical explanation, comparison, design decision, or worked example as required. The algorithms are implementation-independent pseudocode; the Python program is the executable simulation.

---

## Q1 — Wireless Network Architecture and Mobility Analysis (6 Marks)

### A. Wireless network architecture
A wireless network connects mobile nodes through radio links to access points (APs) or cellular base stations (BSs). The access infrastructure connects to a gateway/router and then to the wired network or Internet.

```text
 Mobile node MN1 ))       (( Mobile node MN2
             \             /
          [Wireless AP / Base Station]
                     |
              [Access Router]
                     |
              [Core Network]
                     |
              [Server / CN]
```

**Components and roles**
- **Mobile nodes:** phones, laptops, ambulances or sensors that send and receive data while moving.
- **AP/base station:** provides radio coverage and bridges or schedules wireless access.
- **Wireless link:** radio channel between a node and its serving AP/BS; quality depends on distance, interference and obstacles.
- **Gateway/router:** forwards packets between the access network and other networks.
- **Correspondent/server:** endpoint communicating with the mobile node.

**Characteristics and constraints:** Wireless bandwidth is shared and variable. Signal strength, interference, congestion and obstacles affect throughput and packet loss. Mobility changes the serving AP/BS and may require handoff. Limited bandwidth makes unnecessary control messages expensive; weak connectivity increases delay and retransmissions.

### B. Mobility and performance analysis
When a node moves toward another coverage area, it detects the new AP/BS, evaluates signal quality, obtains access and transfers its active connection. A successful handoff keeps packet flow active with a short interruption. If the old link fails before the new link is ready, packets may be delayed or lost.

The mobility sequence is: **monitor signal → discover candidate network → authenticate/associate → update address or mobility binding → update route → resume traffic**. Increasing speed or overlapping less coverage generally increases handoff frequency and interruption risk.

### C. Small communication scenario
Assume MN1 sends packets to a server through BS1. While moving, MN1 enters BS2 coverage. With adequate overlap, BS2 is prepared before BS1 becomes unusable and packet delivery continues. With poor overlap, packets sent during the transition may be lost or retransmitted.

| Condition | Expected behaviour |
|---|---|
| Stationary, strong signal | Stable route, low loss and delay |
| Slow movement, overlapping cells | Handoff usually completes with brief interruption |
| Fast movement, small overlap | More handoffs and higher interruption risk |
| Weak signal/congestion | Lower throughput, higher delay and packet loss |

**Conclusion:** A suitable wireless design must balance coverage, available bandwidth, handoff time, packet delivery and mobility speed. The reproducible mobility test data is in `data/mobility_scenarios.csv` and generated measurements are in `results/mobility_results.csv`.

---

## Q2 — Mobile IP and Mobility Management (7 Marks)

### A. Architecture and entities
Mobile IP allows a Mobile Node (MN) to keep its permanent **Home Address** while using a temporary **Care-of Address (CoA)** in a visited network.

```text
 Correspondent Node (CN)
          |
       Internet
          |
    Home Agent (HA) ---- tunnel ----> CoA / Foreign Agent (FA)
                                         |
                                    Mobile Node (MN)
```

- **MN:** device that changes its point of attachment.
- **HA:** home-network router that stores the MN's current home-address-to-CoA binding and intercepts/forwards packets.
- **FA:** traditional Mobile IPv4 visited-network agent that assists the MN and may provide a CoA.
- **CN:** remote endpoint communicating with the MN.
- **CoA:** current reachable endpoint for the MN in the visited network.

### B. Agent discovery, registration and packet delivery
1. MN listens for agent advertisements; if none arrive, it may solicit an advertisement.
2. MN identifies whether it is at home or in a foreign network.
3. In a foreign network, MN obtains a CoA.
4. MN sends an authenticated registration request containing its home address, CoA and requested lifetime to HA (directly or via FA).
5. HA validates the request and stores the binding; it returns an acceptance or rejection.
6. CN sends a packet addressed to the permanent home address. HA intercepts it, encapsulates it and tunnels it to the CoA.
7. The tunnel endpoint decapsulates the packet and delivers the original packet to MN. Reverse traffic may be sent directly or through a reverse tunnel depending on policy.

### C. Challenges and improvements
- **Registration/handoff delay:** discover and register quickly; use overlapping coverage and timely advertisements.
- **Tunnelling overhead:** encapsulation adds header bytes; use an appropriate tunnel mode and avoid unnecessary nested tunnels.
- **Triangular routing:** CN→HA→MN may be longer than a direct path; route optimisation can reduce path stretch where supported and secure.
- **Packet loss:** buffer packets during handoff, use link-layer assistance and retransmission, and avoid switching before the new link is usable.
- **Security:** authenticate registrations, protect mobility signalling and prevent replay or binding hijack.
- **Scalability:** aggregate signalling, manage binding lifetimes and distribute mobility load.

### D. Joint answer: frequent network changes
Frequent movement can cause repeated discovery and registration, stale bindings, tunnel changes, packet loss, increased delay and signalling overhead. Reduce these effects with fast handoff, make-before-break where possible, buffering, authenticated registration, sensible registration lifetimes, route optimisation and stable overlapping coverage.

**Registration/packet flow:** `MN → FA/CoA → HA (Registration Request)`; `HA → MN (Registration Reply)`; `CN → HA → tunnel → CoA/FA → MN`.

---

## Q3 — Cellular Networks versus Ad Hoc Wireless Networks (7 Marks)

### A. Architecture

```text
CELLULAR:                         AD HOC:
 Phone )) BS1                     Node A )) Node B
          |                              ))     ))
       Core Network                  Node C )) Node D
          |
       Internet
```

A cellular network is infrastructure-based: mobile devices communicate through base stations connected to a core network. An ad hoc network is infrastructure-less: nodes communicate directly when in range or forward packets for other nodes over multiple wireless hops.

### B. Comparison

| Parameter | Cellular network | Ad hoc network |
|---|---|---|
| Infrastructure | Fixed base stations and core | No fixed infrastructure required |
| Communication | Usually via BS/core | Direct or multi-hop peer forwarding |
| Routing | Infrastructure-assisted and centrally managed | Distributed routing among nodes |
| Mobility | Network-managed handoff | Routes change as nodes move |
| Topology | Planned cells | Dynamic, self-organising |
| Scalability | Large coverage with operator planning | Depends on density, radio range and routing overhead |
| Handoff | Between cells/base stations | Route repair or neighbour change |
| Failure handling | BS/core failure can disrupt a region | Alternate peer routes may survive if available |
| Applications | Public voice/data, broadband IoT | Disaster response, military, temporary field networks |

### C. Engineering decision for disaster conditions
If fixed infrastructure is unavailable, select an **ad hoc/mesh network** as the immediate communication layer. Rescue teams, ambulances and police vehicles can relay packets for one another without a working base station. If a temporary satellite link, portable cell or surviving cellular site is available, connect the ad hoc mesh to it as a gateway for wider reach.

**Conclusion:** Cellular provides managed wide-area coverage when infrastructure exists. Ad hoc networking is more suitable for rapid deployment in an infrastructure outage, but its capacity and connectivity depend on node density, battery power and changing routes.

---

## Q4 — Applications of Mobile IP and Routing Requirements (7 Marks)

### Selected application: ambulance and mobile healthcare communication
An ambulance sends patient vital signs, location, emergency status and video/voice data to a hospital while travelling between coverage areas.

**Entities:** ambulance mobile node (MN), home agent (HA), visited-network foreign agent/access gateway (FA), hospital monitoring server (correspondent node, CN), medical sensors and dispatch centre.

```text
 Patient sensors → Ambulance MN )) visited BS/FA
                                  |
                              Internet
                                  |
                           Home Agent (HA)
                                  |
                         Hospital server (CN)
```

### How Mobile IP supports the application
The ambulance keeps its home address as its stable identity. On entering a visited network it discovers an agent, obtains a CoA and registers that CoA with its HA. Packets sent by the hospital server to the home address are intercepted by HA and tunnelled to the current CoA. Thus, the application endpoint does not need to learn every new visited-network address.

### Routing and performance requirements
- Low end-to-end delay for alarms and urgent patient data.
- High packet delivery and reliable acknowledgements for critical records.
- Fast handoff with minimal interruption during movement.
- Priority/QoS for vital signs and emergency voice; video may adapt its bitrate.
- Authentication, encryption, access control and patient-data confidentiality.
- Redundant paths or store-and-forward buffering during temporary outages.

**Suitability:** Mobile IP is useful when the ambulance must retain a stable IP identity across IP networks. It does not itself guarantee low latency or reliable radio coverage; it must be combined with suitable routing, QoS, security and buffering. A local ad hoc link can keep nearby responders connected if infrastructure fails.

---

## Q5 — Proactive Routing Protocols in Mobile Networks (6 Marks)

### A. Proactive routing and DSDV
A proactive protocol maintains routes before data is requested. **DSDV (Destination-Sequenced Distance-Vector)** is a table-driven protocol based on distance-vector routing. Each route records destination, next hop, hop count and destination sequence number.

Sequence numbers indicate route freshness. A route with a newer sequence number is preferred; if sequence numbers are equal, the route with the smaller hop count is preferred. Periodic and triggered updates distribute changes. A broken route is advertised with an infinite metric and a newer sequence number so stale routes are not reused.

### B. Sample topology and route change

```text
Before: S —— A —— D       (S reaches D in 2 hops)
After:  S —— B —— D       (link A-D fails; S uses B)
```

| State | Destination | Next hop | Hops | Sequence | Status |
|---|---|---:|---:|---:|---|
| Before | D | A | 2 | 10 | Valid |
| After update | D | B | 2 | 12 | Valid |
| Old path | D | A | ∞ | 11 | Invalid |

### C. Performance
Advantages: routes are available before data transmission, so route setup delay is low; sequence numbers help prevent loops caused by stale information. Disadvantages: periodic table updates consume bandwidth, battery and processing even when traffic is absent. High mobility causes frequent updates and convergence work. Larger networks increase table size and control traffic.

**Conclusion:** DSDV suits relatively stable or frequently communicating networks where low initial route delay matters. For sparse traffic and highly dynamic topologies, reactive routing may reduce unnecessary periodic updates. Sample data and a route-update trace are included in `data/dsdv_trace.csv`.

---

## Q6 — Reactive Routing and Protocol Comparison (7 Marks)

### A. AODV operation
AODV (Ad hoc On-Demand Distance Vector) discovers routes only when a source needs them.

1. **RREQ:** source broadcasts a Route Request with source/destination identifiers and sequence information. Intermediate nodes record a reverse route and discard duplicate requests.
2. **RREP:** destination, or an intermediate node with a sufficiently fresh route, sends a Route Reply along the reverse path. Nodes install forward-route entries.
3. **Data:** packets follow the discovered next hops.
4. **RERR:** when a link breaks, affected routes are invalidated and a Route Error is sent to nodes using the route. The source can start a new discovery if communication is still required.

AODV reduces idle periodic control traffic, but the first packet may wait for route discovery. Mobility can break active routes, trigger RERR and cause rediscovery delay.

### B. DSDV versus AODV

| Feature | DSDV (proactive) | AODV (reactive) |
|---|---|---|
| Route discovery | Maintained continuously | On demand |
| Initial data delay | Usually low if route is current | Route-discovery delay if unknown |
| Control overhead | Periodic/triggered table updates | RREQ/RREP/RERR when needed |
| Idle traffic | Updates continue | Little route-discovery traffic when idle |
| Mobility | Updates and convergence | Broken-route detection and repair |
| Best fit | Frequent traffic, lower setup delay | Intermittent traffic, bandwidth constraints |

### C. Joint decision
For a highly dynamic network with intermittent communication and limited bandwidth, select **AODV**. It avoids continuously advertising complete routing tables and discovers paths only when needed. Its cost is extra delay during discovery and after a break. If the network carries constant high-priority traffic with a strict route-setup deadline and has enough bandwidth for updates, DSDV may be preferable.

**Conclusion:** Protocol choice depends on traffic rate, mobility, bandwidth, network size and acceptable setup delay—not mobility alone.

---

## Q7 — Design a Mobile Emergency Communication Network (10 Marks)

### Stage 1 — Independent proposals

**Student A — architecture and mobility proposal**
- Use a self-organising wireless mesh among ambulances, police vehicles, rescue teams and portable medical devices.
- Use surviving cellular, satellite or portable base-station access as optional gateways.
- Use Mobile IP when a stable home address and reachability across IP networks are required; HA maintains the home-address/CoA binding.
- Prioritise alarms, patient vitals and dispatch messages over video.

**Student B — routing and reliability proposal**
- Use AODV for the rapidly changing mesh because route discovery is demand-driven and avoids continuous full-table updates.
- Monitor neighbour/link status, invalidate broken routes, send RERR and rediscover.
- Use alternate next hops where available, queue critical packets during short disconnections, retry with limits and use multiple gateways if present.
- Measure packet delivery ratio, end-to-end delay, route-discovery delay and control overhead.

### Stage 2 — comparison
Both proposals support moving nodes, redundant communication and priority traffic. Student A focuses on stable network identity and access across networks; Student B focuses on finding paths inside the changing mesh. Mobile IP does not replace the mesh routing protocol: Mobile IP handles reachability across IP networks, while AODV selects paths among ad hoc nodes. The combined design introduces registration/tunnel overhead plus route-discovery control traffic.

### Stage 3 — joint final architecture

```text
 Ambulance MN ─┐
 Police MN ────┼── multi-hop AODV wireless mesh ── Portable gateway
 Rescue MN ────┤                                  / surviving BS
 Medical nodes ┘                                         |
                                                    Internet
                                                        |
                                                   Home Agent
                                                        |
                                               Hospital / Dispatch CN
```

**Mobility and packet flow**
1. Nodes discover neighbours and maintain link status.
2. AODV discovers a mesh route when a destination is not in the routing table.
3. If an MN moves to a different IP network, it obtains a CoA and registers it with HA.
4. CN sends to the MN's stable home address; HA tunnels packets to the registered CoA.
5. Inside the visited mesh, AODV forwards packets hop by hop to the MN.
6. When a link fails, nodes invalidate the route, send RERR and rediscover; if a temporary partition remains, critical packets are queued and retried when connectivity returns.

**Mobile IP entities:** MN = ambulance/responder device; HA = home-network mobility anchor; FA = traditional Mobile IPv4 visited-network agent (or visited access gateway/CoA service in a modern implementation); CN = hospital or dispatch server.

### Stage 4 — validation plan and measured test design
Test with 10, 25 and 50 mobile nodes under low, medium and high mobility. Send a fixed number of packets per run. Record end-to-end delay, packet delivery ratio and routing-control overhead. Compare AODV with DSDV using the same traffic and mobility inputs.

The included Python model is a **deterministic educational simulation**, not a packet-level radio simulator. It uses explicit assumptions to generate reproducible illustrative measurements. Results must therefore be interpreted as model output, not real-world or ns-3 measurements.

### Stage 5 — validation findings
- AODV is appropriate for intermittent traffic and changing routes because it avoids continuous periodic route-table broadcasts.
- Mobile IP preserves a stable home address by updating the HA binding to the current CoA and tunnelling packets to that location.
- More nodes and faster movement increase contention, route changes and control overhead; packet delivery can fall and delay can rise.
- During a full partition, neither Mobile IP nor AODV can deliver packets over a nonexistent path. Buffering, alternate gateways and later retransmission reduce—but do not eliminate—the interruption.

### Stage 6 — joint evaluation and conclusion
The mesh is suitable when fixed infrastructure is unavailable because participating nodes forward traffic for one another. Mobile IP is needed only where stable IP reachability across visited networks is required; local mesh-only communication may work without it. AODV is selected for the dynamic, intermittently connected mesh. Costs include RREQ/RREP/RERR signalling, route-discovery delay, Mobile IP registration and tunnel headers. Performance depends on node density, mobility speed, radio range, traffic priority, battery, bandwidth and gateway availability.

A network designer should evaluate infrastructure availability, coverage, mobility rate, traffic pattern, bandwidth, delay target, packet delivery, control overhead, security, power, node density and partition duration before selecting a mobility mechanism and routing protocol.

---

## References and scope
The terminology, required entities, algorithm expectations and comparison criteria follow the supplied Assignment 3 handout. Numerical results in the repository are generated by the accompanying illustrative program and are not claimed as measured physical-network performance.
