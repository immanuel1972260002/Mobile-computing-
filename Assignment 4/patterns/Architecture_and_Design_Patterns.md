# Assignment 4 — Patterns and Structured Design Artifacts

This folder contains non-executable design patterns. The assignment prohibits source code and implementation using IDEs, emulators or SDKs.

## P1 — Android layered architecture

```text
Application components (Activity / Service / Receiver / Provider)
                 |
          Android Framework APIs
                 |
       Binder IPC / System Services
                 |
 Native Libraries / ART / JNI
                 |
        HAL / Vendor Services
                 |
 Linux Kernel (scheduler, VM, VFS, network, Binder, SELinux)
                 |
 CPU / RAM / Flash / Radio / Sensors / Display
```

**Trust boundary:** each application has a distinct UID and sandbox. Framework services authenticate Binder caller identity and check permissions. SELinux and kernel isolation provide lower-level enforcement.

## P2 — Incoming push event

```text
Network radio event
   -> kernel network driver / network stack
   -> platform push broker (FCM / APNs / WNS)
   -> OS notification or eligible background activation
   -> app process/runtime initialisation if needed
   -> application callback
   -> TLS fetch + authenticated local persistence
   -> notification/UI update
```

A push is a wake-up or notification signal, not proof that the full message is durably stored.

## P3 — App launch dependency chain

```text
User tap
 -> launcher / package lookup
 -> process creation and UID assignment
 -> runtime and class-loader initialisation
 -> framework Application callback
 -> Activity lifecycle callback
 -> view construction
 -> compositor / display
```

Cold start creates the process and initialises runtime. Warm start can reuse a live process/runtime but may still recreate the Activity.

## P4 — Power-state transition pattern

| Current state | Event/guard | Next state | Action |
|---|---|---|---|
| ACTIVE | No input for idle timeout and no critical work | IDLE | Dim/off display; batch timers; defer nonurgent jobs. |
| IDLE | No active wake lock and suspend permitted | SUSPENDED | Enter low-power CPU state; arm wake sources. |
| SUSPENDED | Push/hardware interrupt/alarm/user input | ACTIVE (brief) | Resume OS; handle urgent event; return to idle when finished. |
| ACTIVE | Battery ≤15% and saver enabled | ACTIVE-SAVER | Reduce clocks/display and noncritical app work. |
| ACTIVE-SAVER | Battery > threshold with hysteresis or user disables saver | ACTIVE | Restore normal policy gradually. |

**Invariant:** no application may hold an indefinite wake lock solely to poll for messages or sensor changes.

## P5 — Offline record lifecycle

```text
CAPTURED
  -> VALIDATED
  -> ENCRYPTED
  -> LOCAL_COMMIT
  -> PENDING_SYNC
  -> IN_FLIGHT
  -> SERVER_COMMITTED
  -> ACK_VERIFIED
  -> SYNCED
```

On timeout or process death: IN_FLIGHT returns to PENDING_SYNC; reuse the same record UUID and idempotency key. A server ACK is accepted only when UUID and payload hash match.

## P6 — Synchronisation decision pattern

1. Is the device enrolled and not revoked? If no, reject sync.
2. Is connectivity available and battery policy permissive? If no, retain queue.
3. Select pending records in sequence order.
4. Send encrypted batch over validated TLS.
5. Does server already have UUID?
   - Same UUID and same hash: return existing ACK.
   - Same UUID and different hash: quarantine conflict.
   - New UUID: validate and commit record + idempotency ledger atomically.
6. Verify ACK at client.
7. Mark only acknowledged records SYNCED.
8. Retry unacknowledged records using unchanged UUIDs.

## P7 — Security repair pattern

| Asset | Threat | Control | Verification |
|---|---|---|---|
| Permissions | Overbroad access | Request only feature-required permission at point of use | Denial path still works |
| Login token | Local app/data theft | App-private storage + Keystore-protected encryption | Other UID cannot read token |
| Updates | Malicious package substitution | Verify signing identity and trusted distribution | Altered/unsigned package rejected |
| Network traffic | Sniffing / modification | TLS with certificate validation | Invalid certificate fails closed |
| Offline records | Lost device | Authenticated encryption + protected key + remote credential revocation | Ciphertext unreadable without authorised key |

## P8 — Class C capability gate

```text
Device enrolment
 -> Does model have persistent storage?
 -> Does model have approved cryptographic API / secure element?
 -> Can key be protected separately from RMS data?
 -> Does vendor pass loss/lock and recovery tests?
    YES -> enable encrypted offline PHI queue
    NO  -> disable PHI offline mode; allow non-sensitive online WML only
```

## P9 — Adversarial test checklist

- [ ] App process killed during capture: last committed record survives.
- [ ] App process killed during upload: retry uses same UUID.
- [ ] Server commits but ACK is dropped: retry does not duplicate.
- [ ] Device revoked before reconnect: sync rejected.
- [ ] Device clock is wrong: sequence ordering remains correct.
- [ ] Class C lacks protected crypto: PHI offline feature remains disabled.
- [ ] Battery reaches 15%: saver defers noncritical work but does not delete local records.
