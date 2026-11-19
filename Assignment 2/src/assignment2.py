#!/usr/bin/env python3
"""Assignment 2 Q1-Q7 simulations. Reproducible with NumPy and seed 20261119."""
from pathlib import Path
import csv, json, math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20261119
rng = np.random.default_rng(SEED)

def write_csv(name, rows):
    if rows:
        with (OUT / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader(); w.writerows(rows)

def jain(x):
    x=np.asarray(x,float)
    return float(x.sum()**2/(len(x)*np.dot(x,x))) if np.dot(x,x) else 0.0

def q1():
    rows=[]
    n=10000
    for avail in (0.90,0.60,0.30):
        first=rng.random(n)<avail
        delivered=int(first.sum())
        waits=np.zeros(n,dtype=int)
        pending=~first
        while pending.any():
            idx=np.flatnonzero(pending)
            ok=rng.random(len(idx))<avail
            waits[idx[ok]] += 1
            pending[idx[ok]]=False
            waits[idx[~ok]] += 1
        delays=np.where(first,0.02,waits+0.02)
        rows.append(dict(availability=avail,updates=n,immediate_delivered=delivered,
            immediate_lost=n-delivered,store_forward_delivered=n,
            store_forward_delayed=n-delivered,store_forward_lost=0,
            mean_store_forward_delay_min=round(float(delays.mean()),4)))
    write_csv("Q1_connectivity.csv",rows); return rows

def q2():
    usable={"FDMA":int(80*.92),"TDMA":int(80*.88)}
    datasets=[
      ("continuous_voice",70,1.0,False),
      ("bursty_10pct",70,.10,False),
      ("mixed_70voice_30data",70,.70,False),
      ("synchronised_edge",90,1.0,True)]
    rows=[]
    for label,devices,duty,edge in datasets:
      for scheme in ("FDMA","TDMA"):
        cap=usable[scheme]
        if edge:
            blocked=max(0,devices-cap); used=min(devices,cap); offered=devices
            util=used/cap; wasted=0
        else:
            active=int(round(devices*duty))
            blocked=max(0,active-cap); used=min(active,cap); offered=active
            util=used/cap; wasted=cap-used
        rows.append(dict(dataset=label,scheme=scheme,nominal_channels=80,
          usable_channels=cap,offered_active_users=offered,blocked_users=blocked,
          utilisation_of_usable_channels=round(util,4),
          idle_channels_per_interval=wasted,
          reserved_capacity_wasted_pct=round(100*wasted/cap,2)))
    write_csv("Q2_fdma_tdma.csv",rows); return rows

def hadamard(n):
    h=np.array([[1.0]])
    while len(h)<n: h=np.block([[h,h],[h,-h]])
    return h

def q3():
    rows=[]; corr=[]
    bits_n=4000; noise=.25
    for L in (8,16,64):
      for users in (2,4,8):
       for mode in ("walsh_synchronous","random_codes","near_far_10x"):
        errors=0; total=0
        if mode in ("walsh_synchronous","near_far_10x"):
            cmat=hadamard(L)[:users]/math.sqrt(L)
        else:
            cmat=rng.choice([-1.,1.],size=(users,L))/math.sqrt(L)
        powers=np.ones(users)
        if mode=="near_far_10x":
            powers[-1]=10
            cmat[-1]=np.roll(cmat[-1],1)
        for _ in range(bits_n):
            bits=rng.choice([-1.,1.],size=users)
            if mode=="near_far_10x":
                signal=np.sum((bits[:-1]*powers[:-1])[:,None]*cmat[:-1],axis=0)
                signal += bits[-1]*powers[-1]*cmat[-1]
            else:
                signal=np.sum((bits*powers)[:,None]*cmat,axis=0)
            received=signal+rng.normal(0,noise/math.sqrt(L),L)
            for u in range(users):
                decision=1 if np.dot(received,cmat[u])>=0 else -1
                errors += int(decision!=bits[u]); total += 1
        vals=[abs(float(np.dot(cmat[i],cmat[k]))) for i in range(users) for k in range(i+1,users)]
        corr.append(dict(code_length=L,users=users,condition=mode,
                         mean_abs_pair_correlation=round(float(np.mean(vals)),5) if vals else 0))
        rows.append(dict(code_length=L,processing_gain_db=round(10*math.log10(L),2),
          users=users,condition=mode,bits_tested=total,bit_errors=errors,ber=round(errors/total,7)))
    write_csv("Q3_cdma_ber.csv",rows); write_csv("Q3_cdma_correlation.csv",corr)
    return {"ber":rows,"correlation":corr}

def q4():
    U,K,R=8,64,1000
    totals={k:np.zeros(U) for k in ("fixed_contiguous","interleaved_round_robin","channel_aware")}
    for _ in range(R):
        gains=rng.exponential(1.0,size=(U,K))
        rates=np.log2(1+10*gains)
        for u in range(U): totals["fixed_contiguous"][u]+=rates[u,u*K//U:(u+1)*K//U].sum()
        for k in range(K): totals["interleaved_round_robin"][k%U]+=rates[k%U,k]
        winners=np.argmax(rates,axis=0)
        for k,u in enumerate(winners): totals["channel_aware"][u]+=rates[u,k]
    rows=[]
    for name,x in totals.items():
        x=x/R
        rows.append(dict(allocation=name,sum_throughput_bps_hz=round(float(x.sum()),5),
          jain_fairness=round(jain(x),6),minimum_user_rate_bps_hz=round(float(x.min()),5),
          per_user_rates=json.dumps([round(float(v),5) for v in x])))
    write_csv("Q4_ofdma.csv",rows)
    ortho=[]; n=np.arange(K)
    for a,b in ((1,2),(3,11),(17,42)):
        va=np.exp(2j*np.pi*a*n/K); vb=np.exp(2j*np.pi*b*n/K)
        ortho.append(dict(subcarrier_a=a,subcarrier_b=b,
             abs_normalised_inner_product=round(float(abs(np.vdot(va,vb))/K),12)))
    write_csv("Q4_orthogonality.csv",ortho)
    return {"allocation":rows,"orthogonality":ortho}

def q5():
    rows=[]; angles=np.linspace(-90,90,36001)
    for N in (2,4,8,16):
        af=np.abs(np.exp(1j*np.pi*np.arange(N)[:,None]*np.sin(np.deg2rad(angles))[None,:]).sum(axis=0)/N)
        peak=int(np.argmax(af)); half=1/math.sqrt(2)
        li=np.where(af[:peak]<=half)[0]; ri=np.where(af[peak+1:]<=half)[0]
        hpbw=float(angles[peak+1+ri[0]]-angles[li[-1]]) if len(li) and len(ri) else 180.0
        nulls=np.where(af[peak+1:]<1e-3)[0]
        first_null=float(angles[peak+1+nulls[0]]) if len(nulls) else 90.0
        side=af.copy(); side[np.abs(angles)<=first_null]=0
        psl=("N/A" if N==2 else round(20*math.log10(max(float(side.max()),1e-12)),3))
        minsep=None; sir_at_min=None
        for sep in range(5,61,5):
            leak=abs(np.exp(1j*np.pi*np.arange(N)*np.sin(np.deg2rad(sep))).sum()/N)
            sir=-20*math.log10(max(leak,1e-12))
            if sir>=10:
                minsep=sep; sir_at_min=round(sir,3); break
        rows.append(dict(elements=N,hpbw_deg=round(hpbw,3),first_null_deg=round(first_null,3),
             peak_sidelobe_db=psl,minimum_separation_for_10db_sir_deg=minsep,
             sir_at_minimum_db=sir_at_min))
    write_csv("Q5_sdma_array.csv",rows); return rows

def q6():
    weights={"spectral_efficiency":.25,"scalability":.20,"interference_resilience":.20,
             "fairness_qos":.20,"implementation_energy_cost":.15}
    ratings={
      "wide_area_cellular_voice":{
        "SDMA":[5,4,3,4,3],"TDMA":[3,3,4,4,4],"FDMA":[2,2,4,4,4],"CDMA":[4,4,3,3,3],"OFDMA":[5,5,4,5,3]},
      "jam_resistant_tactical":{
        "SDMA":[4,3,2,3,2],"TDMA":[2,3,3,4,4],"FDMA":[2,2,3,3,4],"CDMA":[4,4,5,4,3],"OFDMA":[5,4,2,4,2]},
      "stadium_high_rate_downlink":{
        "SDMA":[5,4,3,3,3],"TDMA":[3,3,4,4,4],"FDMA":[2,2,4,3,4],"CDMA":[3,3,3,3,3],"OFDMA":[5,5,4,4,3]},
      "5000_low_rate_sensors":{
        "SDMA":[4,3,3,3,2],"TDMA":[3,4,4,4,5],"FDMA":[2,2,4,3,4],"CDMA":[4,4,4,4,3],"OFDMA":[5,4,4,4,3]}}
    rows=[]
    for deployment,methods in ratings.items():
      for method,vals in methods.items():
        score=sum(weights[k]*v for k,v in zip(weights,vals))
        rows.append(dict(deployment=deployment,method=method,
          spectral_efficiency=vals[0],scalability=vals[1],interference_resilience=vals[2],
          fairness_qos=vals[3],implementation_energy_cost=vals[4],
          weighted_score=round(score,4)))
    write_csv("Q6_weighted_ratings.csv",rows)
    sens=[]
    for deployment,methods in ratings.items():
      base_scores={m:sum(weights[k]*v for k,v in zip(weights,vals)) for m,vals in methods.items()}
      for changed,w in weights.items():
        for factor in (.8,1.2):
          ww=dict(weights); ww[changed]=w*factor
          total=sum(ww.values()); ww={k:v/total for k,v in ww.items()}
          scores={m:sum(ww[k]*v for k,v in zip(ww,vals)) for m,vals in methods.items()}
          sens.append(dict(deployment=deployment,changed_weight=changed,factor=factor,
             selected_method=max(scores,key=scores.get),
             winning_score=round(max(scores.values()),4),
             base_winner=max(base_scores,key=base_scores.get)))
    write_csv("Q6_sensitivity.csv",sens)
    return {"ratings":rows,"sensitivity":sens}

def q7():
    U,K,R=60,64,1000
    old=np.zeros(U); new=np.zeros(U); old_tones=np.zeros(U); new_tones=np.zeros(U)
    for _ in range(R):
        gains=rng.exponential(1.0,size=(U,K)) * np.r_[np.ones(40),np.full(20,0.20)][:,None]
        rates=np.log2(1+10*gains)
        win=np.argmax(rates,axis=0)
        for k,u in enumerate(win): old[u]+=rates[u,k]; old_tones[u]+=1
        assigned=np.zeros(K,dtype=bool); user_rate=np.zeros(U)
        for u in rng.permutation(U):
            order=np.argsort(rates[u])[::-1]
            chosen=next(k for k in order if not assigned[k])
            assigned[chosen]=True; user_rate[u]+=rates[u,chosen]; new_tones[u]+=1
        averages=np.maximum(user_rate,1e-9)
        for k in np.where(~assigned)[0]:
            metric=rates[:,k]/averages
            u=int(np.argmax(metric))
            user_rate[u]+=rates[u,k]; averages[u]=.8*averages[u]+.2*user_rate[u]
            new_tones[u]+=1
        new+=user_rate
    old/=R; new/=R; old_tones/=R; new_tones/=R
    rows=[]
    for label,x,t in (("original_best_subcarrier",old,old_tones),("redesigned_minimum_1_tone",new,new_tones)):
        rows.append(dict(strategy=label,sum_throughput_bps_hz=round(float(x.sum()),5),
          jain_fairness=round(jain(x),6),minimum_user_rate_bps_hz=round(float(x.min()),5),
          maximum_user_rate_bps_hz=round(float(x.max()),5),
          average_minimum_tones_per_user=round(float(t.min()),3),
          average_maximum_tones_per_user=round(float(t.max()),3),
          users=U,subcarriers=K,realisations=R,
          per_user_rates=json.dumps([round(float(v),5) for v in x])))
    write_csv("Q7_redesign_comparison.csv",rows); return rows

def main():
    result={"seed":SEED,"Q1":q1(),"Q2":q2(),"Q3":q3(),"Q4":q4(),"Q5":q5(),"Q6":q6(),"Q7":q7()}
    (OUT/"all_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print("Assignment 2 Q1-Q7 completed; CSV files and all_results.json generated.")
    for q in ("Q1","Q2","Q3","Q4","Q5","Q6","Q7"):
        print(q, "results generated")

if __name__=="__main__": main()
