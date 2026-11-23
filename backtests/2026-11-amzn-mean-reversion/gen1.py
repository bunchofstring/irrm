from lab import *
from strategies import BandSnap, GapFill, DailySwing
import time
D = data(); k = split_index(D)
print('range', D.dates[D.i0], '->', D.dates[D.i1], 'sessions', D.i1-D.i0+1, '| IS', D.dates[D.i0], '->', D.dates[D.i0+k-1], '| OOS', D.dates[D.i0+k], '->', D.dates[D.i1])
b = bench(D); print(row('Buy & hold (IS)', is_metrics(b, D, b)))
G1 = [BandSnap(name='A1 band-snap z<=-2 (5m)'), GapFill(name='B1 gap-fill >=0.75%'), DailySwing(name='C1 daily RSI2<10 swing')]
for s in G1:
    t0=time.time(); r = simulate(s, D); m = is_metrics(r, D, b)
    print(row(s.name, m), f' ({time.time()-t0:.1f}s)'); diag(r, D)
