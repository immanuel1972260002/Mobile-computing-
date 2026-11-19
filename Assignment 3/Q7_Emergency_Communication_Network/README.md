# Q7 – Design a Mobile Emergency Communication Network (10 marks)

## Joint Design Answer
**Scenario:** A disaster disables fixed infrastructure while ambulances, police, rescue teams and medical staff move continuously. The network must deliver critical information with minimum delay.

**Student A proposal – architecture and mobility:** Form a multi-hop wireless ad hoc network among rescue vehicles and portable devices. Use Mobile IP only where a reachable Home Agent/visited-network gateway remains available and session continuity across IP networks is required. When infrastructure is absent, local ad hoc addressing and routing provide local communication; Mobile IP alone cannot replace a missing route or gateway.

**Student B proposal – routing:** Use AODV for demand-driven route discovery in a dynamic network with intermittent traffic. Maintain active routes, detect link breaks, issue RERR and rediscover routes. Critical traffic can use priority queues and alternate paths when available.

**Joint final design:** Mobile nodes include ambulances, police vehicles, rescue teams and field hospitals. Wireless links form a changing graph. Gateways connect to surviving backhaul. Where Mobile IP service is available, MN registers its CoA with HA and packets are tunnelled to it. Within the disaster area, AODV discovers multi-hop paths. Use authentication, packet buffering, retransmission, redundant relay nodes and periodic connectivity checks.

**Evaluation:** Delay includes route discovery, queuing, transmission and (where used) Mobile IP registration/tunnelling. Packet delivery ratio = delivered packets / generated packets × 100. Routing overhead = control packets / data packets (or control bytes / total bytes). Increasing mobility can increase link failures, RERR messages, rediscovery delay and packet loss. If connectivity is partitioned, delivery is postponed until a path returns; store-and-forward buffering helps.

**Conclusion:** Analyse infrastructure availability, mobility rate, traffic pattern, bandwidth, delay tolerance, packet loss, network size, security, power, coverage and failure recovery before choosing Mobile IP and a routing protocol. AODV suits dynamic intermittent ad hoc traffic; Mobile IP is useful when cross-network address continuity and agent infrastructure are available.

## Pseudocode
```text
ALGORITHM EmergencyNetwork(MobileNodes, Packets, InfrastructureState)
INPUT: mobile nodes, generated packets, link states, infrastructure availability
OUTPUT: delivered packets, lost/pending packets, control overhead
BEGIN
  Initialise neighbor tables and route tables
  FOR each packet DO
    IF destination is local THEN DELIVER packet
    ELSE IF valid AODV route exists THEN FORWARD packet to NextHop
    ELSE
      BROADCAST RREQ
      WAIT for RREP or timeout
      IF RREP received THEN install route and FORWARD packet
      ELSE BUFFER packet and count pending
      END IF
    END IF
  END FOR
  ON link failure DO
    Mark route INVALID
    SEND RERR to affected source
    IF alternate route exists THEN switch route
    ELSE initiate route discovery
    END IF
  END ON
  IF infrastructure is AVAILABLE AND external session continuity is required THEN
    Obtain CoA; register with HA; tunnel external packets
  END IF
  RETURN performance counters
END
```

## Data / Test Scenario
Six mobile nodes (ambulance, police, rescue, field hospital and two relay nodes); fixed infrastructure unavailable; traffic is intermittent; route Ambulance—Relay-1—Relay-2—Field-Hospital exists. AODV discovers this route on demand. A link failure triggers RERR and rediscovery. Measure generated/delivered packets, delay and control messages.

## Program (program.py)
```python
def emergency_network():
    generated = 5
    delivered = 0
    control = 0
    route = ['Ambulance', 'Relay-1', 'Relay-2', 'Field-Hospital']
    print('Fixed infrastructure: UNAVAILABLE')
    print('AODV: broadcast RREQ for first data packet')
    control += 1
    print('RREP received; route:', ' -> '.join(route))
    control += 1
    for packet in range(1, generated + 1):
        delivered += 1
        print(f'Packet {packet}: delivered to Field-Hospital')
    print('Generated:', generated)
    print('Delivered:', delivered)
    print('Packet delivery ratio:', f'{delivered/generated*100:.1f}%')
    print('Control messages (simplified count):', control)

if __name__ == '__main__':
    emergency_network()
```

## Output
```text
Fixed infrastructure: UNAVAILABLE
AODV: broadcast RREQ for first data packet
RREP received; route: Ambulance -> Relay-1 -> Relay-2 -> Field-Hospital
Packet 1: delivered to Field-Hospital
Packet 2: delivered to Field-Hospital
Packet 3: delivered to Field-Hospital
Packet 4: delivered to Field-Hospital
Packet 5: delivered to Field-Hospital
Generated: 5
Delivered: 5
Packet delivery ratio: 100.0%
Control messages (simplified count): 2
```

**Note:** This is a deterministic educational demonstration, not a full packet-level simulator. The reported 100% delivery applies only to this ideal sample run.
