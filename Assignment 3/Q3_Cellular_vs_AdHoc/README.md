# Q3 – Cellular Networks versus Ad Hoc Wireless Networks (7 marks)

## Answer
A cellular network is infrastructure-based. Mobile devices communicate through base stations connected to a core network. Coverage is divided into planned cells, and mobility is supported by handoff between base stations. Routing and resource management are infrastructure-assisted. It provides broad managed coverage but depends on functioning infrastructure.

An ad hoc network is infrastructure-less. Nodes communicate directly or through multiple peer nodes. Each node may act as both host and router. Its topology changes as nodes move, and distributed routing discovers and maintains multi-hop paths. It can be deployed rapidly for disaster relief, military and temporary field communication, but routes may be unstable.

| Parameter | Cellular | Ad hoc |
|---|---|---|
| Infrastructure | Base stations/core network | No fixed infrastructure |
| Communication | Through base station | Direct or multi-hop |
| Routing | Infrastructure-assisted | Distributed |
| Mobility | Cellular handoff | Route discovery/repair |
| Topology | Planned cells | Dynamic |
| Scalability | Broad managed coverage | Depends on density and routing overhead |
| Failure | Infrastructure failure may disrupt service | Alternate peer routes may exist |
| Applications | Public voice/data | Disaster, military, temporary networks |

**Decision:** In a disaster area with unavailable fixed infrastructure, select an ad hoc network. Rescue devices can form multi-hop paths without base stations; redundant paths and route repair improve resilience.

## Pseudocode
```text
ALGORITHM SelectWirelessArchitecture(Infrastructure, Deployment, MultiHop)
INPUT: infrastructure availability, deployment time, multi-hop requirement
OUTPUT: CELLULAR or AD_HOC
BEGIN
  IF Infrastructure = UNAVAILABLE AND Deployment = IMMEDIATE THEN
    RETURN AD_HOC
  ELSE IF MultiHop = REQUIRED THEN
    RETURN AD_HOC
  ELSE
    RETURN CELLULAR
  END IF
END
```

## Data / Scenario
Fixed cellular infrastructure unavailable; immediate deployment required; rescue nodes can relay packets over multiple hops.

## Program (program.py)
```python
def select_architecture(infrastructure, deployment, multihop):
    if infrastructure == 'UNAVAILABLE' and deployment == 'IMMEDIATE':
        return 'AD_HOC'
    if multihop == 'REQUIRED':
        return 'AD_HOC'
    return 'CELLULAR'

if __name__ == '__main__':
    print('Selected architecture:', select_architecture('UNAVAILABLE', 'IMMEDIATE', 'REQUIRED'))
```

## Output
```text
Selected architecture: AD_HOC
Reason: no fixed infrastructure and immediate multi-hop deployment is required.
```
