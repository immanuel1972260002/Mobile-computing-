"""Deterministic simulator for constraint-aware mobile background work (B1/B2).
Platform-independent simulation, not an Android APK/device benchmark.
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Job:
    jid: str
    priority: int
    size_mb: float
    sensitive: bool = True
    encrypted: bool = True
    permission: bool = True
    attempts: int = 0
    status: str = "queued"

@dataclass
class Env:
    battery: int = 80
    network: str = "good"  # good, poor, offline
    doze: bool = False
    permission: bool = True
    min_battery: int = 20
    permission_revoked_mid_execution: bool = False

def run(jobs: List[Job], env: Env, strategy: str):
    pending = list(jobs)
    if strategy == "priority":
        pending.sort(key=lambda j: (-j.priority, j.size_mb, j.jid))
    enqueued = len(jobs)
    deferred = cancelled = success = processed = peak = 0
    events = []
    for j in pending:
        processed += 1
        j.attempts += 1
        reason = None
        if not env.permission or not j.permission:
            reason = "permission_revoked"
            j.status = "cancelled"; cancelled += 1
        elif j.sensitive and not j.encrypted:
            reason = "unencrypted_sensitive_data"
            j.status = "rejected"; cancelled += 1
        elif env.doze or env.battery < env.min_battery or env.network != "good":
            reason = "doze" if env.doze else ("low_battery" if env.battery < env.min_battery else "network_unavailable_or_poor")
            j.status = "deferred"; deferred += 1
        else:
            peak = max(peak, 1)  # serial worker limit in this simulator
            # Revalidate authority after worker start, before network commit.
            if env.permission_revoked_mid_execution:
                reason = "permission_revoked_mid_execution"
                j.status = "cancelled"; cancelled += 1
            else:
                j.status = "uploaded"; success += 1
                env.battery = max(0, env.battery - max(1, int(j.size_mb * 1.2)))
        events.append({"id":j.jid,"priority":j.priority,"battery":env.battery,"network":env.network,"doze":env.doze,"decision":reason or "execute","status":j.status})
    backlog = sum(j.status == "deferred" for j in pending)
    return {"strategy":strategy,"enqueued":enqueued,"processed":processed,"deferred":deferred,"cancelled":cancelled,"successful":success,"peak_concurrent_workers":peak,"residual_backlog":backlog,"events":events}

def clone(jobs):
    return [Job(**j.__dict__) for j in jobs]

def main():
    scenarios = {
      "good_connectivity": ([Job("S1",3,1),Job("S2",5,1),Job("S3",2,2)], Env(85,"good",False,True), "priority"),
      "doze_low_battery": ([Job("D1",5,1),Job("D2",2,1)], Env(12,"good",True,True), "priority"),
      "permission_revoked_mid_execution": ([Job("P1",5,1)], Env(80,"good",False,True,80,True), "priority"),
    }
    for name,(jobs,env,_) in scenarios.items():
      r=run(clone(jobs),env,"priority")
      print(name, {k:v for k,v in r.items() if k!="events"})
      for e in r["events"]: print(" ",e)
    A=[Job("A1",5,1),Job("A2",4,1),Job("A3",3,1),Job("A4",2,1),Job("A5",1,1),Job("A6",2,1)]
    B=[Job("B1",5,1,True,False),Job("B2",4,1),Job("B3",3,1),Job("B4",2,1),Job("B5",1,1),Job("B6",2,1)]
    for name,jobs,env in [("workload_A",A,Env(90,"good",False,True)),("workload_B",B,Env(90,"poor",False,True))]:
      r=run(jobs,env,"priority")
      print(name,{k:v for k,v in r.items() if k!="events"})
      for e in r["events"]: print(" ",e)
    W=[Job("low",1,1),Job("critical",5,1),Job("medium",3,1),Job("high",4,1)]
    for strategy in ("fifo","priority"):
      r=run(clone(W),Env(90,"good",False,True),strategy)
      print("order_"+strategy,{k:v for k,v in r.items() if k!="events"},"order",[e["id"] for e in r["events"]])

if __name__ == "__main__":
    main()
