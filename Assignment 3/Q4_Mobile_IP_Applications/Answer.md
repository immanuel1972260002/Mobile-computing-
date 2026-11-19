Q4 – Applications of Mobile IP and Routing Requirements (7 marks)

**Selected application: Emergency ambulance communication.** Ambulances move between coverage areas while exchanging patient information, vital signs, location and hospital updates. Mobile entities are the ambulance's Mobile Node, dispatch centre/hospital Correspondent Nodes, Home Agent and visited-network access infrastructure/Foreign Agent.

Mobile IP preserves the ambulance's home address while it moves. In a visited network, the ambulance obtains a CoA and registers it with the HA. Packets addressed to the home address are tunnelled to the current CoA. Routing must provide reachability, low delay, reliable packet delivery, fast route repair and secure registration. Critical messages should receive priority; buffering/retransmission can reduce loss during short interruptions.

**Suitability:** Mobile IP is useful when sessions must continue across different IP networks. It does not itself guarantee low delay or reliable radio coverage; routing, QoS, authentication and redundant connectivity are also required.
