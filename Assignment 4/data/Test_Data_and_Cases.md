# Assignment 4 — Data, Assumptions and Test Vectors

These are design test inputs, not executable source code or measured device benchmarks.

## D1 — Platform comparison input

| Platform | Kernel | Runtime/code model | IPC | Push/background mechanism |
|---|---|---|---|---|
| Android | Linux monolithic | Dalvik historically; ART currently, DEX + JIT/AOT | Binder, intents, providers, sockets | FCM, Doze, JobScheduler/WorkManager |
| iOS | Darwin/XNU hybrid | Native Mach-O; Objective-C runtime; ARC | XPC, Mach messages, extensions | APNs, BackgroundTasks, background URLSession |
| Windows | Windows NT hybrid | Native PE or .NET IL; WinRT is API contract | COM/RPC, App Services, pipes | WNS and app-model background activation |

## D2 — RuralCare sample record schema

| Field | Example value | Purpose |
|---|---|---|
| record_uuid | 9f2a...-unique-id | Stable idempotency identity |
| patient_ref | PSEUDO-00482 | Pseudonymous patient reference |
| worker_ref | W-017 | Audit attribution |
| device_ref | DEV-A-009 | Device enrolment/revocation |
| shift_ref | SHIFT-2026-11-19-A | Shift-level grouping |
| sequence_no | 000126 | Local capture ordering |
| client_time | 2026-11-19T09:20:00+05:30 | Event chronology |
| clock_quality | SYNCED / UNSYNCED | Indicates clock confidence |
| schema_version | 3 | Payload interpretation |
| payload_hash | SHA-256 digest | Detects altered payload |
| key_version | K-04 | Supports key rotation |
| sync_state | PENDING | Retry state |

Patient details and cryptographic keys are not included in this test-vector document.

## D3 — Synchronisation test vectors

| Test | Client state | Server state | Expected result |
|---|---|---|---|
| T01 First upload | UUID-A pending | UUID-A absent | Server commits once; client verifies ACK and marks synced. |
| T02 ACK lost | UUID-B pending after timeout | UUID-B already committed with hash H | Retry UUID-B/H; server returns same ACK; no second row. |
| T03 Conflicting retry | UUID-C payload changed, same UUID | UUID-C stored with different hash | Server quarantines conflict; does not overwrite. |
| T04 Interrupted batch | UUID-D and UUID-E pending; only D ACKed | D committed, E absent | Client marks D synced; E remains pending and retries. |
| T05 Revoked device | Device marked revoked | Any pending UUIDs | Server rejects authentication; no upload accepted. |
| T06 Wrong local clock | Sequence 10 has later client timestamp than sequence 11 | Both new | Preserve sequence order; store timestamps as supplied evidence and flag clock quality. |
| T07 Low battery | Battery 20% | Queue has 30 records | Defer nonurgent sync; preserve all records. |
| T08 Battery saver | Battery 14% | Queue has 30 records | Saver activates; no record deletion; sync only urgent/allowed work. |

## D4 — Security regression test inputs

| Test | Action | Expected outcome |
|---|---|---|
| S01 Permission denied | User denies Contacts permission | Manual contact entry remains available; no contact data is read. |
| S02 Permission granted | User grants Contacts permission when feature is used | Contacts Provider returns permitted data. |
| S03 Cross-app token read | Separate app attempts to read token | Access denied by private storage/UID sandbox; encrypted key is not exported. |
| S04 Unsigned update | Install/update package with mismatched signer | Package Manager rejects update. |
| S05 TLS interception | Server presents invalid certificate | Client connection fails closed; no plaintext fallback. |
| S06 Device loss | Administrator revokes device | New server sessions/uploads rejected; local data remains encrypted. |

## D5 — Power-policy test inputs

| Input | Expected state/policy |
|---|---|
| User actively enters a patient form | ACTIVE; display and UI responsive |
| Screen off, no critical work | IDLE then SUSPENDED |
| Urgent push arrives while suspended | OS wake/notification path; short authorised work |
| Sensor FIFO reaches threshold | Brief wake to drain and persist batch |
| Battery reaches 20% | Defer nonurgent sync and reduce optional activity |
| Battery reaches 15% | Battery-saver policy active; urgent safety path remains |
