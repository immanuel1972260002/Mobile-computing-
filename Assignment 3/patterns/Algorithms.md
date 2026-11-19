# Assignment 3 — Algorithmic Patterns and Pseudocode

The following language-independent algorithms use the notation required by the assignment handout.

## 1. Wireless neighbour discovery
```text
ALGORITHM DiscoverWirelessNeighbors(MN, TransmissionRange)
INPUT: MN, TransmissionRange
OUTPUT: NeighborSet
BEGIN
  NeighborSet ← EMPTY_SET
  BROADCAST HELLO from MN
  WAIT for neighbor responses
  FOR each Response received DO
    IF SignalStrength(Response) > MIN_SIGNAL AND
       Distance(MN, Response.Node) ≤ TransmissionRange THEN
      ADD Response.Node TO NeighborSet
    END IF
  END FOR
  RETURN NeighborSet
END
```

## 2. Mobile IP registration
```text
ALGORITHM RegisterMobileNode(MN, HA, CoA)
INPUT: MN, HA, CoA
OUTPUT: RegistrationStatus
BEGIN
  Create RegistrationRequest
  Request.HomeAddress ← MN.HomeAddress
  Request.CareOfAddress ← CoA
  Request.Lifetime ← RequestedLifetime
  Authenticate Request
  SEND Request TO HA
  WAIT FOR RegistrationReply
  IF RegistrationReply.Status = ACCEPTED THEN
    Binding[MN.HomeAddress] ← CoA
    RETURN REGISTRATION_SUCCESS
  ELSE
    RETURN REGISTRATION_FAILURE
  END IF
END
```

## 3. Mobile IP packet tunnelling
```text
ALGORITHM TunnelPacketToMobileNode(Packet, DestinationHomeAddress)
INPUT: Packet, DestinationHomeAddress
OUTPUT: Delivery status
BEGIN
  IF Binding[DestinationHomeAddress] does not exist THEN
    DROP Packet
    RETURN DELIVERY_FAILURE
  END IF
  CoA ← Binding[DestinationHomeAddress]
  EncapsulatedPacket ← ENCAPSULATE(Packet, CoA)
  FORWARD EncapsulatedPacket TO CoA
  IF TunnelDeliverySuccessful THEN
    Decapsulate at tunnel endpoint
    DELIVER original Packet TO MobileNode
    RETURN DELIVERY_SUCCESS
  ELSE
    RETURN DELIVERY_FAILURE
  END IF
END
```

## 4. Handoff management
```text
ALGORITHM PerformHandoff(MN, OldNetwork, NewNetwork)
INPUT: MN, OldNetwork, NewNetwork
OUTPUT: HandoffStatus
BEGIN
  Detect NewNetwork
  Measure SignalQuality(NewNetwork)
  IF SignalQuality(NewNetwork) < MIN_SIGNAL THEN
    RETURN HANDOFF_REJECTED
  END IF
  Obtain new network address or CoA
  Pause non-critical transmissions if required
  UPDATE mobility registration
  UPDATE routing information
  IF RegistrationStatus = SUCCESS THEN
    SWITCH active attachment TO NewNetwork
    Resume data transmission
    RETURN HANDOFF_SUCCESS
  ELSE
    Restore OldNetwork if available
    RETURN HANDOFF_FAILURE
  END IF
END
```

## 5. DSDV-style route update
```text
ALGORITHM UpdateDSDVRoute(Node, ReceivedRoute)
INPUT: Node, ReceivedRoute = {Destination, NextHop, HopCount, SequenceNumber}
OUTPUT: Updated RouteTable
BEGIN
  Destination ← ReceivedRoute.Destination
  NewHopCount ← ReceivedRoute.HopCount + 1
  IF Destination not in RouteTable THEN
    ADD route with NextHop = Node.Neighbor
  ELSE IF ReceivedRoute.SequenceNumber > RouteTable[Destination].SequenceNumber THEN
    REPLACE RouteTable[Destination]
  ELSE IF ReceivedRoute.SequenceNumber = RouteTable[Destination].SequenceNumber
       AND NewHopCount < RouteTable[Destination].HopCount THEN
    REPLACE RouteTable[Destination]
  END IF
  RETURN RouteTable
END
```

## 6. AODV-style route discovery and maintenance
```text
ALGORITHM ReactiveRouteDiscovery(Source, Destination)
INPUT: Source, Destination
OUTPUT: Route or ROUTE_NOT_FOUND
BEGIN
  IF RouteTable[Destination].State = VALID THEN
    RETURN RouteTable[Destination]
  END IF
  RouteRequestID ← RouteRequestID + 1
  Create RouteRequest(Source, Destination, RouteRequestID)
  Broadcast RouteRequest to neighbors
  WAIT for RouteReply or RouteFailure
  IF RouteReply received THEN
    Establish reverse path and forward path
    Mark RouteTable[Destination] as VALID
    RETURN RouteTable[Destination]
  ELSE
    RETURN ROUTE_NOT_FOUND
  END IF
END
```

```text
ALGORITHM MaintainReactiveRoute(Source, Destination)
INPUT: Source, Destination
OUTPUT: RouteStatus
BEGIN
  MONITOR active route
  IF LinkFailureDetected THEN
    Mark failed link as INVALID
    IF AlternateValidRoute exists THEN
      Select alternate route
      RETURN ALTERNATE_ROUTE_USED
    ELSE
      Generate and SEND RouteError toward affected source
      IF Source still requires communication THEN
        RETURN ReactiveRouteDiscovery(Source, Destination)
      ELSE
        RETURN ROUTE_TERMINATED
      END IF
    END IF
  END IF
  RETURN ROUTE_ACTIVE
END
```

## 7. Emergency packet forwarding
```text
ALGORITHM ForwardEmergencyPacket(Node, Packet)
INPUT: Node, Packet
OUTPUT: DELIVERED, FORWARDED, BUFFERED or DROPPED
BEGIN
  IF Node = Packet.Destination THEN
    DELIVER Packet
    RETURN DELIVERED
  END IF
  IF ValidRouteTo(Packet.Destination) AND LinkStatus(NextHop) = UP THEN
    FORWARD Packet TO NextHop
    RETURN FORWARDED
  ELSE
    Mark unavailable route as INVALID
    IF Packet.Priority = CRITICAL AND BufferCapacityAvailable THEN
      STORE Packet with ExpiryTime
      RETURN BUFFERED
    END IF
    RETURN DROPPED
  END IF
END
```
