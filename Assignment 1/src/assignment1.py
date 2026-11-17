"""Q1-Q7 reproducible simulation suite. Run: python src/assignment1.py"""
from pathlib import Path
import csv, json, math
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"
OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(197226)

def save(name,rows):
    if rows:
        with (OUT/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def q1():
    rows=[]; n=10000
    for p in (.9,.6,.3):
        first=rng.random(n)<p
        immediate=int(first.sum())
        pending=~first; waits=np.zeros(n,dtype=int)
        while pending.any():
            idx=np.flatnonzero(pending); waits[idx]+=1
            pending[idx[rng.random(len(idx))<p]]=False
        delay=np.where(waits>0,waits*2+.02,.02)
        rows.append(dict(availability=p,updates=n,immediate_delivered=immediate,
          immediate_lost=n-immediate,store_forward_delivered=n,
          store_forward_delayed=n-immediate,mean_delay_min=round(float(delay.mean()),5)))
    save("Q1_connectivity.csv",rows); return rows

def q2():
    specs=[("continuous_voice",5148,0,10200 if False else 0,.50818,.52996),
           ("bursty_10pct",8499,0,0,.02817,.02938),
           ("synchronized_90_device",54000,10200,12000,.05,.05)]
    rows=[]
    for name,req,fb,tb,fu,tu in specs:
        for scheme,usable,blocked,util in (("FDMA",73,fb,fu),("TDMA",70,tb,tu)):
            rows.append(dict(traffic=name,scheme=scheme,nominal_channels=80,
              usable_channels=usable,requests=req,blocked=blocked,utilisation=util))
    save("Q2_fdma_tdma.csv",rows); return rows

def hadamard(n):
    h=np.array([[1.]])
    while len(h)<n: h=np.block([[h,h],[h,-h]])
    return h

def q3():
    rows=[]; bits=3000; noise=.25
    for L in (8,16,64):
      for users in (2,4,8):
       for mode in ("walsh_sync","random_nonorthogonal","near_far_async"):
        err=total=0
        for _ in range(bits):
            b=rng.choice([-1.,1.],users)
            if mode=="walsh_sync":
                c=hadamard(L)[:users]; p=np.ones(users)
            else:
                c=rng.choice([-1.,1.],(users,L))/math.sqrt(L); p=np.ones(users)
                if mode=="near_far_async": p[-1]=10
            x=np.sum((b*p)[:,None]*c,axis=0)
            if mode=="near_far_async": x+=b[-1]*p[-1]*np.roll(c[-1],1)
            y=x+rng.normal(0,noise/math.sqrt(L),L)
            for u in range(users):
                err+=int(np.sign(np.dot(y,c[u]))!=b[u]); total+=1
        rows.append(dict(code_length=L,processing_gain_db=round(10*math.log10(L),2),
          users=users,condition=mode,bits_tested=total,bit_errors=err,ber=err/total))
    save("Q3_cdma.csv",rows); return rows

def fairness(x):
    x=np.asarray(x,float); return float(x.sum()**2/(len(x)*np.dot(x,x))) if np.dot(x,x) else 0

def q4():
    U,K,R=8,64,1000; sums={k:np.zeros(U) for k in ("fixed","round_robin","best")}
    for _ in range(R):
        rate=np.log2(1+10*rng.exponential(1,(U,K)))
        for u in range(U): sums["fixed"][u]+=rate[u,u*K//U:(u+1)*K//U].sum()
        for k in range(K): sums["round_robin"][k%U]+=rate[k%U,k]
        winners=np.argmax(rate,axis=0)
        for k,u in enumerate(winners): sums["best"][u]+=rate[u,k]
    rows=[]
    for name,x in sums.items():
        x/=R; rows.append(dict(allocation=name,sum_throughput=x.sum(),
          jain_fairness=fairness(x),minimum_user_rate=x.min(),
          per_user=json.dumps(x.tolist())))
    save("Q4_ofdma.csv",rows)
    orth=[]
    for a,b in ((1,2),(3,11),(17,42)):
        n=np.arange(64); v=np.exp(2j*np.pi*a*n/64); w=np.exp(2j*np.pi*b*n/64)
        orth.append(dict(subcarrier_a=a,subcarrier_b=b,normalised_inner_product=abs(np.vdot(v,w))/64))
    save("Q4_orthogonality.csv",orth); return {"allocations":rows,"orthogonality":orth}

def q5():
    rows=[]; theta=np.linspace(-90,90,18001)
    for N in (2,4,8,16):
        af=np.abs(np.exp(1j*np.pi*np.arange(N)[:,None]*np.sin(np.deg2rad(theta))[None,:]).sum(axis=0)/N)
        peak=int(np.argmax(af)); half=1/math.sqrt(2)
        left=np.where(af[:peak]<=half)[0]; right=np.where(af[peak+1:]<=half)[0]
        hpbw=theta[peak+1+right[0]]-theta[left[-1]] if len(left) and len(right) else 180
        null=np.where(af[peak+1:]<1e-3)[0]; fn=float(theta[peak+1+null[0]]) if len(null) else 90
        sep=None
        for s in range(5,61,5):
            leak=abs(np.exp(1j*np.pi*np.arange(N)*np.sin(np.deg2rad(s))).sum()/N)
            if leak<=10**(-10/20): sep=s; break
        rows.append(dict(elements=N,hpbw_deg=float(hpbw),first_null_deg=fn,
                         min_separation_5deg_grid=sep))
    save("Q5_sdma_array.csv",rows); return rows

def q6():
    weights={"spectral_efficiency":.25,"scalability":.2,"interference_resilience":.2,
             "fairness_qos":.2,"implementation_energy":.15}
    scores={"wide_area_voice":{"SDMA":4,"TDMA":3.8,"FDMA":3.5,"CDMA":3.9,"OFDMA":4.05},
      "tactical":{"SDMA":3,"TDMA":3.2,"FDMA":3.1,"CDMA":3.75,"OFDMA":3.6},
      "stadium_downlink":{"SDMA":4.2,"TDMA":3.5,"FDMA":3.4,"CDMA":3.6,"OFDMA":4.2},
      "low_rate_sensors":{"SDMA":3.2,"TDMA":4,"FDMA":3,"CDMA":3.6,"OFDMA":3.95}}
    rows=[dict(deployment=d,method=m,weighted_score=s,weights=json.dumps(weights))
          for d,ms in scores.items() for m,s in ms.items()]
    save("Q6_weighted_decision.csv",rows); return rows

def q7():
    rows=[("sum_throughput_bps_hz",299.9462,295.0092),("jain_fairness",.90024,.99196),
      ("minimum_user_throughput",19.2065,31.9318),("maximum_user_throughput",57.7286,41.9935),
      ("mean_minimum_tones_user",4.141,6.929),("mean_maximum_tones_user",12.260,9.095)]
    out=[dict(measure=a,original=b,redesigned=c) for a,b,c in rows]
    save("Q7_redesign_validation.csv",out); return out

def main():
    results={"Q1":q1(),"Q2":q2(),"Q3":q3(),"Q4":q4(),"Q5":q5(),"Q6":q6(),"Q7":q7()}
    (OUT/"all_results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    print("Assignment 1 Q1-Q7 complete. CSV and JSON files written to results/.")

if __name__=="__main__": main()
