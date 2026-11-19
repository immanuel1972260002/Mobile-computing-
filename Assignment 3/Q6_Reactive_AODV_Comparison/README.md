# Q6 – Reactive Routing and Protocol Comparison (7 marks)

## Answer
Reactive routing discovers routes only when a source needs to send data. AODV (Ad hoc On-Demand Distance Vector) uses Route Request (RREQ), Route Reply (RREP) and Route Error (RERR). The source broadcasts RREQ. Intermediate nodes record a reverse route to the source and forward the request if they have not processed that request ID. The destination or a node with a fresh route returns RREP. If an active-route link fails, RERR informs affected nodes and a new discovery may begin.

| Feature | DSDV (proactive) | AODV (reactive) |
|---|---|---|
| Route setup | Maintained continuously | On demand |
| Initial delay | Usually low | Route discovery delay |
| Control overhead | Periodic updates | RREQ/RREP/RERR when needed |
| Infrequent traffic | May waste updates | Often efficient |
| Mobility | Table convergence required | Repair/discovery after break |

**Decision:** For a highly dynamic network with intermittent traffic, select AODV because it avoids continuous periodic table broadcasts and discovers routes when needed. Its trade-off is route-discovery delay and broadcast overhead during frequent breaks. For continuous high-rate traffic with strict low setup delay, DSDV may be preferable if topology is sufficiently stable.

## Pseudocode
```text
ALGORITHM AODVRouteDiscovery(Source, Destination)
INPUT: source, destination, neighbor table
OUTPUT: route or ROUTE_NOT_FOUND
BEGIN
  IF valid route exists THEN RETURN route
  END IF
  Increment RouteRequestID
  BROADCAST RREQ(Source, Destination, RouteRequestID)
  Each receiver records reverse route and forwards unseen RREQ
  IF destination or valid-route node receives RREQ THEN
    SEND RREP along reverse route
    Install forward route at source
    RETURN route
  ELSE
    RETURN ROUTE_NOT_FOUND
  END IF
END
```

## Data / Scenario
Network S—A—D. S has no route to D. RREQ travels S to A to D; RREP returns D to A to S. S installs next hop A.

## Program (program.py)
```python
def aodv_discovery(source, destination, path):
    print(f'{source}: no valid route to {destination}; broadcast RREQ')
    for node in path[1:]:
        print(f'{node}: receive RREQ and record reverse route')
    print(f'{destination}: generate RREP')
    for node in reversed(path[:-1]):
        print(f'{node}: receive RREP and install forward route')
    print(f'{source}: route established via ' + ' -> '.join(path[1:]))

if __name__ == '__main__':
    aodv_discovery('S', 'D', ['S', 'A', 'D'])
```

## Output
```text
S: no valid route to D; broadcast RREQ
A: receive RREQ and record reverse route
D: receive RREQ and record reverse route
D: generate RREP
A: receive RREP and install forward route
S: receive RREP and install forward route
S: route established via A -> D
```
