# PART A — Design, Analysis & Architectural Reasoning (25)

## A1 — Constraint-aware Intent and Service architecture (7)

### A1.1 Problem model (1)
**Inputs:** sensor events, network quality/type, battery/charging, Doze, permissions, consent/login state, encryption-key availability and upload preferences. **Outputs:** authenticated encrypted backend records, local critical-event notifications and durable task status. **Decisions:** collect/wait, persist/reject, upload/defer, select worker/service, notify/suppress, cancel on logout/revocation. **Constraints:** battery policy, Android background limits, valid network, sensor/notification permission, consent, encryption at rest/in transit, no upload after logout and bounded concurrency. **Goal:** every valid consented record is acknowledged logically once using an idempotency key or safely retained for retry; critical alerts are surfaced; plaintext sensitive data never leaves protected storage.

### A1.2 Runtime state (1)
Each task stores ID, type, encrypted payload reference, creation time, deadline, priority, status, attempts, idempotency key, permission/consent version, encryption state, required network, checkpoint and last error. Global state stores battery, charging, Doze, network quality/metering, login, permissions, key availability, active-worker count and durable queue. Intents carry task IDs only, never health payloads. Checkpoint uploaded chunks and server acknowledgement for restart recovery.

### A1.3 Feasibility / pruning (1)
- **Reject/cancel:** consent absent, logged out, permission revoked, invalid/expired record, key unavailable, sensitive payload unencrypted, or owner/authentication mismatch.
- **Defer:** Doze/background restriction, low battery and not charging, offline/poor or disallowed metered network, concurrency cap, retry-after not elapsed.
- **Execute:** authenticated and consented; permission still granted; encrypted payload and key available; network and battery policies pass; worker slot available.
- Critical local alert may be shown without upload if notification permission and privacy policy allow. Encryption and consent are never bypassed.

### A1.4 Architectural pseudocode (3)
\`\`\`text
PROCEDURE RUN_BACKGROUND_COORDINATOR
  state ← LOAD_DURABLE_STATE()
  WHILE application_has_pending_work DO
    event ← RECEIVE_EVENT_OR_WORK_SIGNAL()
    UPDATE_GLOBAL_STATE(state,event)

    IF event.type = SENSOR_READING THEN
      IF NOT state.logged_in OR NOT state.sensor_permission OR NOT state.consent THEN
        RECORD_REJECTION(event.id,"no authority")
      ELSE
        safe_ref ← ENCRYPT_AND_PERSIST(event.payload,state.device_key)
        task ← NEW_TASK("UPLOAD",safe_ref,priority_from(event),idempotency_key(event))
        ENQUEUE_DURABLY(state.queue,task)
      ENDIF
    ENDIF

    IF event.type = CRITICAL_SENSOR_ALERT THEN
      intent ← EXPLICIT_INTENT("AlertReceiver",privacy_safe_metadata)
      SEND_ORDERED_BROADCAST(intent)
      POST_LOCAL_NOTIFICATION_IF_ALLOWED()
    ENDIF

    task ← SELECT_NEXT(state.queue,priority_then_deadline_then_oldest)
    IF task = NONE THEN CONTINUE ENDIF
    worker ← SELECT_WORKER(task.type)  // upload worker, collection service, notification worker
    intent ← EXPLICIT_INTENT(worker,task.id_only)

    feasible ← state.logged_in AND state.consent
      AND REQUIRED_PERMISSION_STILL_GRANTED(task)
      AND task.encryption_state = "encrypted" AND KEY_AVAILABLE(task)
      AND NETWORK_POLICY_PASSES(state,task)
      AND BATTERY_POLICY_PASSES(state,task)
      AND NOT state.doze_without_exemption
      AND state.active_workers < MAX_WORKERS

    IF NOT feasible THEN
      IF AUTHORITY_REVOKED(task) OR task.encryption_state ≠ "encrypted" THEN
        CANCEL_TASK(task); DELETE_OR_QUARANTINE_LOCAL_SECRET(task)
        RECORD_CANCEL(task,"security/authority failure")
      ELSE
        SET_STATUS(task,"DEFERRED")
        SET_NEXT_CHECK(task,NEXT_FEASIBLE_WINDOW(state))
        RECORD_DEFERRAL(task,FAILED_CONDITION(state,task))
      ENDIF
      CONTINUE
    ENDIF

    INCREMENT(state.active_workers)
    CHECKPOINT(task,"started")
    result ← START_OR_ENQUEUE_WORK(worker,intent,task.id)
    DECREMENT(state.active_workers)

    IF result = ACKNOWLEDGED THEN
      MARK_DELIVERED(task.idempotency_key)
      DELETE_ENCRYPTED_LOCAL_COPY_AFTER_RETENTION_POLICY(task)
    ELSE IF result = TRANSIENT_FAILURE THEN
      ROLLBACK_PARTIAL_REMOTE_TRANSACTION_IF_SUPPORTED(task)
      CHECKPOINT(task,"retryable")
      INCREMENT(task.attempt_count)
      APPLY_EXPONENTIAL_BACKOFF_WITH_JITTER(task)
      SET_STATUS(task,"DEFERRED")
    ELSE
      CANCEL_TASK(task); REVOKE_TEMPORARY_CREDENTIALS(task)
      RECORD_PERMANENT_FAILURE(task)
    ENDIF
  ENDWHILE
END PROCEDURE
\`\`\`
**Communication:** explicit intents target internal services/receivers. Implicit intents are only for user-selected external actions and carry no health payload. Ordered broadcasts are limited to controlled local alert acknowledgement. WorkManager persists deferrable uploads; foreground service is limited to user-visible time-critical collection. UI observes durable status asynchronously.

### A1.5 Manual trace (1)
| Event | Choose | Constraint check | Action/state |
|---|---|---|---|
| Sensor reading R1 | Create upload task | Login, consent, sensor permission; encryption succeeds | Persist encrypted R1; enqueue U1 |
| Connectivity becomes good | Select U1 | Battery 70%, network good, key valid | Start upload worker; ACK; mark delivered |
| Device enters Doze | Select U2 from next reading | Doze, no exemption | Defer U2; retain encrypted payload/checkpoint |
| Critical reading | Select alert path | Notification permission valid; local alert needs no network | Ordered local alert intent; privacy-safe notification; upload remains deferred |
| User logs out | Re-evaluate U2 | Session/consent authority invalid | Cancel U2, revoke token and clear session secrets; never upload after logout |

## A2 — Safe incremental synchronisation (5)

### A2.1 Waste in naïve design (1)
It attempts every record even offline, low on battery or unauthorised/unencrypted. It retransmits unchanged data, wastes radio wakeups/CPU, ignores priority and deadlines, and may expose plaintext. Continuing after failure creates repeated timeouts. Without version checks it can overwrite concurrent edits.

### A2.2 Incremental algorithm (2)
\`\`\`text
PROCEDURE BUILD_SYNC_SET(local_store,remote_versions,environment)
  sync_set ← EMPTY
  FOR EACH record IN local_store ORDERED BY priority DESC, age ASC DO
    IF NOT record.consent OR record.owner ≠ current_user THEN
      DISCARD(record,"unauthorised/consent withdrawn"); CONTINUE
    ENDIF
    IF record.sensitive AND NOT record.encrypted THEN
      QUARANTINE(record); CONTINUE
    ENDIF
    IF remote_versions[record.id] > record.local_version THEN
      RESOLVE_CONFLICT_USING_VERSION_OR_USER_POLICY(record); CONTINUE
    ENDIF
    IF record.already_acknowledged THEN
      DISCARD_LOCAL_DUPLICATE_AFTER_RETENTION(record); CONTINUE
    ENDIF
    IF environment.network_quality < record.minimum_network OR
       environment.battery < record.minimum_battery OR
       (environment.metered AND record.large AND NOT user_allows_metered) THEN
      DEFER(record,"resource constraint"); CONTINUE
    ENDIF
    ADD(sync_set,record)
  ENDFOR
  FOR EACH record IN sync_set DO
    result ← UPLOAD_IDEMPOTENT(record.id,record.version,record.ciphertext)
    IF result = ACK THEN MARK_ACKNOWLEDGED(record)
    ELSE IF result = VERSION_CONFLICT THEN RESOLVE_CONFLICT(record)
    ELSE DEFER(record,"transient failure")
  ENDFOR
END PROCEDURE
\`\`\`

### A2.3 Five-record pruning trace (1)
| Record | Priority | Size | Sensitivity | State | Decision |
|---|---:|---:|---|---|---|
| R1 emergency alert | 5 | 8 KB | high | encrypted, good network | Upload first |
| R2 routine pulse | 2 | 4 KB | high | encrypted, good network | Upload |
| R3 raw location | 4 | 2 MB | high | **not encrypted** | Reject/quarantine; terminate branch |
| R4 app theme | 1 | 2 KB | low | encrypted | Upload when convenient |
| R5 long video | 3 | 40 MB | medium | encrypted, battery 12% | Defer |

For R3, all descendants of the upload-now branch are unsafe because encryption is false. More search cannot make that plaintext payload safe; encrypt a new representation or reject. R5 is deferred, not discarded.

### A2.4 Eventual consistency challenge (1)
“Do not schedule unless network is good” is not a valid discard rule offline-first. Local writes must be accepted and retained for later replication; network failure means defer, not delete. The violated assumption was that immediate cloud delivery is required before an operation is useful. Consent/encryption pruning remains valid; conflicts need version vectors, CRDT merge or explicit resolution instead of blind last-write overwrite.

## A3 — Common mobile background-work pattern (5)

| Component | Sensor collection | Data sync | Push notification |
|---|---|---|---|
| State | permission, schedule, last sample, buffer | dirty records, versions, retry cursor | token, message ID, delivery/ack state |
| Decision variable | sample now/wait | upload/defer/resolve | deliver/retry/suppress |
| Candidate choices | sensor service, scheduled worker | upload/chunk worker | receiver, notification worker |
| Feasibility test | permission, battery, sampling policy | encryption, consent, network, battery | valid token, permission, privacy policy, rate limit |
| Goal condition | durable valid sample | acknowledged consistent record | delivered/acknowledged message |
| Pruning/deferral | Doze, low battery, revoked permission | offline, low battery, conflict, unsafe payload | no permission, invalid token, expired message, rate limit |
| Undo/cancel | stop listener; discard partial sample | abort transaction; retain checkpoint; revoke credentials | cancel notification; deduplicate; clear pending ack |

### A3.1 Common pattern (2)
All are event-driven state machines with durable state, candidate actions, feasibility constraints, a goal predicate and recovery. They schedule around OS lifecycle, battery, connectivity, permissions and privacy. Common architecture: durable queue + policy evaluator + bounded executor + result/rollback handler.

### A3.2 Generic framework (2)
\`\`\`text
PROCEDURE SCHEDULE_OR_EXECUTE(state)
  event ← GET_NEXT_EVENT_OR_DUE_TASK()
  APPLY_EVENT_TO_STATE(state,event)
  candidates ← GENERATE_CANDIDATE_ACTIONS(state)
  action ← SELECT_BY_PRIORITY_DEADLINE_AND_FAIRNESS(candidates)
  IF action = NONE THEN RETURN "IDLE" ENDIF
  IF NOT AUTHORIZED(action,state) THEN
    CANCEL_AND_CLEANUP(action,state); RETURN "REJECTED"
  ENDIF
  IF NOT RESOURCES_AVAILABLE(action,state) THEN
    PERSIST_DEFERRED_CHECKPOINT(action,state); RETURN "DEFERRED"
  ENDIF
  snapshot ← SAVE_RECOVERY_POINT(state,action)
  result ← EXECUTE_BOUNDED(action)
  IF result = SUCCESS AND GOAL_REACHED(action,state) THEN
    COMMIT_STATE(action,state); RETURN "COMPLETE"
  ELSE
    UNDO_PARTIAL_EFFECTS(action,snapshot,state)
    CLASSIFY_FAILURE_AND_SCHEDULE_RETRY_OR_CANCEL(action,state)
    RETURN "RECOVERED"
  ENDIF
END PROCEDURE
\`\`\`

### A3.3 Undo/cancellation (1)
Undo prevents partial work appearing complete. If sync is cancelled after sending some chunks, abort the server transaction or retain a resumable checkpoint and idempotency key. Without cleanup, the backend may expose a truncated record, duplicate it on retry, or retain temporary credentials after logout.

## A4 — Local vs cloud vs hybrid tractability (4)
| Problem | What constitutes a solution? | Efficiently verified? | Resource class | Reason |
|---|---|---|---|---|
| Tiny on-device image classifier | Label and confidence for an image | Yes: labelled test set, accuracy/latency; not proof over all images | On-device feasible | Small model avoids network latency and preserves image privacy; monitor CPU/RAM/battery |
| Cloud speech recognition | Transcript with timestamps/confidence | Partly: labelled corpus and latency/error metrics | Network-bound | Large models fit cloud; upload latency, bandwidth, privacy and outages dominate |
| Nearby peer-to-peer file sharing | Authenticated, integrity-checked transfer to intended peer | Protocol/checksum tests; large failure-state space | Hybrid required | Local discovery/transfer, identity/integrity checks; intermittent radio/battery |
| End-to-end encrypted messaging | Confidential, authenticated message to intended devices | Formal review and protocol tests; secrecy not inferred from UI success | Security-critical | Key management, forward secrecy, metadata leakage and secure storage dominate |
| Real-time multiplayer sync | Consistent-enough state within latency budget | Deterministic replay, invariants, latency/load tests; global state explodes | Network-bound | Local prediction/interpolation plus authoritative network reconciliation |
| Large offline vector-map rendering | Correct visible tiles/labels at target frame rate | Bounded tile snapshots; sampled broad-geography tests | Hybrid required | Local cache/render for responsiveness; cloud updates/downloads; memory/storage/thermal limits |

**Why “runs slowly” is inadequate:** performance is workload-dependent and multidimensional. State measurable objectives such as p95 frame time, end-to-end latency, energy/task, peak RAM, radio bytes and deadline-miss rate, then identify CPU, network, battery-throttle, memory, OS-scheduling or security bottlenecks.

**Why local vs cloud matters:** offloading shifts bottlenecks from device CPU/RAM to network latency, availability, cost and server scale. It also changes the trust boundary: local processing can retain raw data privately; cloud processing requires transport encryption, access control, retention rules and threat modelling. Hybrid designs balance responsiveness/privacy with model size and compute.

## A5 — Exact vs approximate feed optimisation (4)

### A5.1 Exact perspective (1)
Enumerate every (decode resolution, cache capacity, prefetch distance) tuple, simulate the workload, reject tuples violating the 16 ms frame budget or memory/battery caps, then choose the feasible tuple with minimum energy/quality cost. With R resolutions, C cache sizes and P prefetch distances, there are R×C×P configurations per device/workload; evaluating interactions across feed items and many profiles multiplies cost. Measurements are noisy and stale as feed/network conditions change.

### A5.2 Adaptive strategy (2)
\`\`\`text
PROCEDURE ADAPT_FEED(metrics,parameters,device_profile)
  REPEAT
    metrics.frame_p95 ← MEASURE_P95_FRAME_TIME()
    metrics.battery ← READ_BATTERY_LEVEL()
    metrics.memory_pressure ← READ_MEMORY_PRESSURE()
    IF metrics.frame_p95 > 16 OR metrics.memory_pressure = HIGH THEN
      IF parameters.decode_quality > MIN_QUALITY THEN
        parameters.decode_quality ← NEXT_LOWER_QUALITY(parameters.decode_quality)
      ELSE IF parameters.cache_capacity > MIN_CACHE THEN
        parameters.cache_capacity ← parameters.cache_capacity - 1
      ELSE
        parameters.prefetch_distance ← MAX(0,parameters.prefetch_distance - 1)
      ENDIF
    ELSE IF metrics.frame_p95 < 13 AND metrics.battery > 40 AND
            metrics.memory_pressure = LOW THEN
      parameters.prefetch_distance ← MIN(MAX_PREFETCH,parameters.prefetch_distance + 1)
    ELSE
      RETURN "STEADY"
    ENDIF
    APPLY(parameters)
  UNTIL parameters_at_safe_bounds OR stable_for_three_windows
  RETURN parameters
END PROCEDURE
\`\`\`
Selection criterion: relieve the measured bottleneck first while preserving minimum quality and hard memory/battery limits. Re-measure after each update; steady state means p95 frame time ≤16 ms and no parameter change for three windows.

### A5.3 Sacrifice (1)
A feasible smooth experience means the observed workload meets frame-time and memory limits. It does not prove global minimum energy: the heuristic may stop at a local/policy-selected point, measurements vary, and the cost surface may be non-convex. Exact optimality requires a complete accurate model and exhaustive comparison; production UI usually accepts a bounded safe heuristic and monitors quality/energy.
