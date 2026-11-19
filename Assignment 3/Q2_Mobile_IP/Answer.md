Q2 – Mobile IP and Mobility Management (7 marks)

**Answer:** Mobile IP allows a Mobile Node (MN) to retain its permanent home address while visiting another network. The Home Agent (HA) maintains a binding between the home address and Care-of Address (CoA). In traditional Mobile IPv4, a Foreign Agent (FA) may provide the CoA and assist registration. The Correspondent Node (CN) sends packets to the MN's home address. The HA intercepts them, encapsulates them and tunnels them to the CoA; the tunnel endpoint decapsulates and delivers them.

**Registration sequence:** MN discovers an agent → obtains CoA → sends authenticated registration request to HA → HA validates and stores home-address/CoA binding → HA returns registration reply. When the MN changes networks, it obtains a new CoA and updates the binding.

**Challenges:** registration and handoff delay, packet loss, tunnelling overhead, triangular routing, security and scalability. Frequent movement causes repeated signalling and interruption. Reduce problems using fast agent discovery, timely registration, buffering during handoff, route optimisation where supported, authentication, and suitable registration lifetimes.
