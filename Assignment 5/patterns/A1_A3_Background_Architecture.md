# Patterns — A1/A3 Background Architecture

## Component flow
\`\`\`text
Sensor event
   |
   v
Permission + consent gate ---- fail ----> Reject / privacy-safe audit
   |
   v
Encrypt + durable local store
   |
   v
Explicit Intent(task ID only) -> WorkManager upload worker
   |
   v
Constraint evaluator: Doze / battery / network / key / permission / concurrency
   | feasible                         | not feasible
   v                                  v
Execute idempotent upload             Security failure? -- yes --> cancel + cleanup
   |                                  transient limit? -- yes --> defer + checkpoint
   v
ACK? -- yes --> commit + mark delivered
  \-- no --> rollback partial effect + retry/backoff or permanent cancel

Critical event -> explicit ordered local alert intent -> privacy-safe notification
\`\`\`

## Common state-machine pattern
\`QUEUED -> CHECKING -> RUNNING -> SUCCEEDED\` with side paths \`CHECKING -> DEFERRED\`, \`CHECKING -> REJECTED\`, \`RUNNING -> RETRYABLE\`, and \`RUNNING -> CANCELLED\`. Only SUCCEEDED commits final durable state. Deferred tasks retain encrypted payload/checkpoint; rejected/cancelled tasks clean up authority-bound secrets.

## A2 pruning invariant
A record is uploadable only if owner and consent are valid, sensitive payload is encrypted, key is available and version/conflict checks pass. Resource failure creates a defer edge, not a delete edge. Security failure cannot be repaired by further upload attempts; transform/encrypt first or reject.

## A5 feedback controller
\`\`\`text
measure frame p95, battery, memory
if frame > 16ms or memory high: lower quality, then trim cache, then prefetch
else if frame < 13ms and battery > 40% and memory low: cautiously increase prefetch
else: hold steady
repeat until safe bounds or stable for 3 windows
\`\`\`
