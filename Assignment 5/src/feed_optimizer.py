"""Exact and adaptive feed-configuration simulator (B3).
Synthetic cost = 10 * estimated frame drops + estimated energy units.
"""
from itertools import product

def cost(case,q,c,p):
    if case == "balanced":
        energy=3*q+2*c+2*p; drops=max(0,8-2*q-c-p)
    elif case == "low_end":
        energy=2*q+c+p; drops=max(0,12-q-2*c-p)
    elif case == "video_heavy":
        energy=5*q+c+3*p; drops=max(0,13-3*q-c-2*p)
    elif case == "trap":
        table={(1,3,0):8,(1,2,0):18,(2,1,1):16,(2,2,1):20,(3,1,1):19}
        return table.get((q,c,p),22+abs(q-3)+abs(c-1)+abs(p-1))
    else:
        raise ValueError(case)
    return 10*drops+energy

def exact(case):
    configs=list(product(range(1,4),range(1,4),range(0,3)))
    scored=[(cost(case,*x),x) for x in configs]
    return min(scored),len(scored)

def adaptive(case,frame_ms=18.0,battery=65):
    q,c,p=3,1,1; changes=0; trace=[]
    for step in range(4):
        measured=frame_ms+(q-2)*1.5-(c-1)*0.8-p*0.3
        if measured>16 and q>1:
            q-=1; action="lower_quality"
        elif battery<25 and p>0:
            p-=1; action="reduce_prefetch"
        elif measured<13 and battery>40 and c<3:
            c+=1; action="grow_cache"
        else:
            action="steady"; trace.append((step,(q,c,p),round(measured,1),action)); break
        changes+=1; trace.append((step,(q,c,p),round(measured,1),action))
    return (q,c,p),cost(case,q,c,p),changes,trace

def main():
    for case in ("balanced","low_end","video_heavy"):
        (ec,conf),n=exact(case); ac,aval,changes,tr=adaptive(case)
        print(case,"exact",ec,conf,"approx",aval,ac,"match",ec==aval,"configs",n,"changes",changes)
    case="trap"; (ec,conf),n=exact(case); ac,aval,changes,tr=adaptive(case,frame_ms=14,battery=60)
    print("counterexample","exact",ec,conf,"approx",aval,ac,"match",ec==aval,"trace",tr)
    for items,levels in ((10,3),(100,6),(1000,10)):
        exact_ops=levels*levels*3; adaptive_ops=4
        print("scale",{"feed_items":items,"quality_levels":levels,"exact_configurations":exact_ops,"adaptive_decision_steps":adaptive_ops})

if __name__=="__main__":
    main()
