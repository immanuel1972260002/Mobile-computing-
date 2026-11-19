# Q4 – Applications of Mobile IP and Routing Requirements (7 marks)

## Answer
**Selected application: Emergency ambulance communication.** Ambulances move between coverage areas while exchanging patient information, vital signs, location and hospital updates. Mobile entities are the ambulance Mobile Node (MN), dispatch centre/hospital Correspondent Nodes (CN), Home Agent (HA), and visited-network access infrastructure/Foreign Agent (FA).

Mobile IP preserves the ambulance's home address while it moves. In a visited network, the ambulance obtains a Care-of Address (CoA) and registers it with the HA. Packets addressed to the home address are tunnelled to the current CoA. Routing must provide reachability, low delay, reliable delivery, fast route repair and secure registration. Critical messages should receive priority; buffering and retransmission can reduce loss during short interruptions.

**Suitability:** Mobile IP is useful when sessions must continue across different IP networks. It does not itself guarantee low delay or radio coverage; routing, QoS, authentication and redundant connectivity are also required.

## Pseudocode
```text
ALGORITHM AmbulanceMobility(MN, HA, VisitedNetwork, EmergencyPacket)
INPUT: ambulance MN, HA, visited network, emergency packet
OUTPUT: packet delivery result
BEGIN
  Detect visited network
  Obtain CareOfAddress
  SEND authenticated registration to HA
  IF registration fails THEN
    BUFFER EmergencyPacket
    RETURN REGISTRATION_FAILURE
  END IF
  UPDATE HA binding from HomeAddress to CareOfAddress
  SEND EmergencyPacket to HomeAddress
  HA tunnels packet to CareOfAddress
  IF tunnel delivery succeeds THEN
    DELIVER packet to dispatch centre
    RETURN DELIVERY_SUCCESS
  ELSE
    BUFFER and retry packet when connectivity returns
    RETURN DELIVERY_PENDING
  END IF
END
```

## Data / Scenario
Ambulance home address=10.1.0.20; new CoA=198.51.100.20; HA registration accepted; packet contains patient status and GPS location.

## Program (program.py)
```python
def ambulance_communication():
    home = '10.1.0.20'
    coa = '198.51.100.20'
    registered = True
    packet = 'Patient status + GPS location'
    if not registered:
        print('Packet buffered: registration failed')
        return
    print(f'Register {home} -> {coa} with Home Agent')
    print(f'HA tunnels emergency packet to {coa}')
    print(f'Dispatch centre receives: {packet}')
    print('Result: DELIVERY_SUCCESS')

if __name__ == '__main__':
    ambulance_communication()
```

## Output
```text
Register 10.1.0.20 -> 198.51.100.20 with Home Agent
HA tunnels emergency packet to 198.51.100.20
Dispatch centre receives: Patient status + GPS location
Result: DELIVERY_SUCCESS
```
