Q1 – Wireless Network Architecture and Mobility Analysis (6 marks)

**Answer:** A wireless network connects mobile nodes through radio links to access points/base stations and then to a gateway or Internet. Main components are mobile nodes, access points/base stations, wireless links, routers and servers. Wireless links have limited bandwidth, variable signal strength, interference, higher error rates and changing connectivity. A mobile node communicates by associating with an access point, obtaining network configuration, sending frames to the access point and forwarding packets through the wired backbone. When it moves, signal quality may fall and a handoff to another access point may be needed.

**Architecture:** Mobile Node → Access Point/Base Station → Wireless Router/Gateway → Internet/Server. A second access point provides the next coverage cell.

**Mobility analysis:** With stationary users, the path remains stable. With a moving user, signal strength changes; handoff may cause temporary interruption, packet loss and delay. Limited bandwidth increases queuing and transmission time. Successful communication requires a usable link and reachable destination.

**Worked scenario:** MN moves from AP1 coverage to AP2. It detects AP2, compares signal quality, reassociates, updates connectivity and resumes packet transmission. The test program models this process and counts delivered and lost packets.
