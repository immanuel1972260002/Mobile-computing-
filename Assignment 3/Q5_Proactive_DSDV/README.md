# Q5 – Proactive Routing Protocols in Mobile Networks (6 marks)

## Answer
A proactive routing protocol maintains routes before data is requested. DSDV (Destination-Sequenced Distance Vector) is a table-driven distance-vector protocol. Each entry stores destination, next hop, hop count and destination sequence number. Nodes periodically broadcast routing updates. A higher sequence number represents fresher information; if sequence numbers are equal, the route with the smaller hop count is preferred. Sequence numbers help prevent routing loops.

**Example topology:** A—B—C—D. Initially A reaches D through B and C (3 hops). If a link fails, nodes advertise changed reachability and update their tables. Periodic and triggered updates consume bandwidth, especially in large or highly mobile networks, but a valid table can reduce route-discovery delay.

**Evaluation:** DSDV suits frequent traffic and moderate topology changes where low route lookup delay is important. High mobility can cause frequent updates, overhead and convergence delay.

## Pseudocode
```text
ALGORITHM UpdateDSDVRoute(Node, ReceivedRoute)
INPUT: destination, next hop, hop count, sequence number
OUTPUT: updated route table
BEGIN
  NewHopCount ← ReceivedRoute.HopCount + 1
  IF destination is absent THEN
    ADD route
  ELSE IF ReceivedSequence > StoredSequence THEN
    REPLACE stored route
  ELSE IF ReceivedSequence = StoredSequence AND NewHopCount < StoredHopCount THEN
    REPLACE stored route
  END IF
  RETURN RouteTable
END
```

## Data / Scenario
Topology A—B—C—D. A receives an advertised route to D from B with hop count 2 and sequence number 8. A records next hop B and hop count 3.

## Program (program.py)
```python
def update_route(table, destination, next_hop, received_hops, received_seq):
    new_hops = received_hops + 1
    old = table.get(destination)
    if old is None or received_seq > old['seq'] or (received_seq == old['seq'] and new_hops < old['hops']):
        table[destination] = {'next_hop': next_hop, 'hops': new_hops, 'seq': received_seq}
    return table

if __name__ == '__main__':
    routes = {}
    update_route(routes, 'D', 'B', 2, 8)
    print('A routing table:', routes)
```

## Output
```text
A routing table: {'D': {'next_hop': 'B', 'hops': 3, 'seq': 8}}
```
