from lab import *
from strategies import BandSnap
D=data(); b=bench(D)
# learning probe for family A: is the edge in the entry at all? vary stop and threshold
for st in [1.5,3,6,99]:
    for k in [2.0,2.5,3.0]:
        r=simulate(BandSnap(k=k,stop_atr=st),D); print(row(f'k{k} stop{st}',is_metrics(r,D,b)))
