# Assignment 4 — Expected Outputs and Desk-Check Results

## R1 — Task 2 background message delivery

| Scenario | Android expected result | iOS expected result |
|---|---|---|
| App backgrounded, screen off | FCM and OS policy deliver notification or eligible callback; Doze may defer nonurgent work. | APNs alert can be shown by OS; silent callback is discretionary. |
| Process terminated by OS | Eligible FCM event may cause process recreation; app callback runs only if policy permits. | Alert can be displayed without app execution; app runs after tap or eligible background wake. |
| User force-stops/force-quits | Background delivery/relaunch is restricted until user reopens app. | Ordinary background relaunch is suppressed until user opens app. |
| Network unavailable | Server retains message; client fetches on reconnect. | Same; push is not a durable message store. |

## R2 — Task 3 launch desk-check

**Cold start:** tap → package resolution → Zygote fork/UID assignment → ART initialisation/class loading → Application callback → Activity callbacks → view construction → compositor displays first frame.

**Warm start with process alive:** tap → package/activity resolution → reuse process and ART → resume or recreate Activity → redraw/reattach window if needed. Process creation and full runtime initialisation are skipped.

## R3 — Task 4 attack result

- First confidentiality loss: malicious app reads the shared login-token file.
- Second confidentiality loss: attacker observes plaintext server traffic.
- Integrity compromise: unverified update source permits malicious package substitution.
- Repair verification: private encrypted token storage, signature verification and TLS certificate validation close the three paths; point-of-use permission keeps legitimate contact access possible after consent.

## R4 — Task 5 power result

Normal path: ACTIVE → IDLE → SUSPENDED. Push/sensor wake event causes a short resume; after handling, return to IDLE/SUSPENDED. Permanent application wake lock prevents this transition and is therefore rejected.

At 15%: ACTIVE-SAVER defers noncritical sync, reduces optional sampling and UI work, retains transactional local writes and urgent notifications.

## R5 — Task 6 lost-device trace

| Time/event | Local state | Server state | Confidentiality/availability result |
|---|---|---|---|
| Shift begins | Key unlocked by platform; queue empty | No new records | Normal operation |
| Offline for six hours | Encrypted records committed, all PENDING | No copy of pending records | Payload protected at rest; server cannot yet recover new records |
| Battery reaches 20% | Queue retained; nonurgent sync deferred | Unchanged | No intentional data deletion |
| Device lost before sync | Device inaccessible; key remains platform-protected | Device credential revoked | Ciphertext should remain unreadable; unsynced records unavailable until device/key recovered |
| Recovery possible | If device and authorised key recover, pending queue can be uploaded | Server accepts only non-revoked authenticated device | Records recoverable after re-enrolment/recovery procedure; if device/key destroyed, unsynced data is lost |

## R6 — Adversarial test conclusions

| Attack | Survives? | Reason / refinement |
|---|---|---|
| Stolen unlocked phone | Partially | At-rest encryption does not stop access during an unlocked session. Enforce short app auto-lock and re-authentication for export. |
| Server commits but ACK is lost | Yes, if protocol implemented as specified | Stable UUID + atomic idempotency ledger makes retry return prior ACK. |
| Legacy phone has no secure key facility | Yes by fail-closed exclusion; no if PHI offline is forced | Capability gate disables offline PHI. Replace or qualify device if requirement is non-negotiable. |
| Wrong device clock | Yes | Monotonic sequence and clock-quality metadata preserve ordering independent of wall clock. |

## Acceptance criteria

1. No record is labelled SYNCED before a matching server ACK is verified.
2. Repeating an upload with the same UUID and same hash creates no duplicate logical record.
3. Repeating an upload with same UUID and different hash creates a conflict, not an overwrite.
4. A revoked device cannot upload or fetch patient records.
5. No PHI is stored offline on a Class C model without approved cryptographic key protection.
6. A process kill during capture or sync does not corrupt previously committed records.
7. Ten-hour battery performance is measured on each qualified device model under representative sensor, screen, network and idle workloads; design assumptions alone are not accepted as a battery measurement.
