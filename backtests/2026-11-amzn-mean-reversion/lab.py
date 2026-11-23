import sys, json, pickle, numpy as np, pandas as pd
sys.path.insert(0, '/tmp/claude-0/-home-user-irrm/58f3d338-e66f-5e8a-96e7-9564be3ab107/scratchpad/work')
from engine import Data, simulate, segment_metrics, split_index, BuyHold, BASE
from strategies import hm

_D = None
def data():
    global _D
    if _D is None:
        p = BASE + 'data/D.pkl'
        try:
            _D = pickle.load(open(p, 'rb'))
        except Exception:
            _D = Data(); pickle.dump(_D, open(p, 'wb'))
    return _D

def bench(D, cost=1e-4):
    return simulate(BuyHold(), D, cost=cost)

def is_metrics(res, D, b):
    k = split_index(D)
    return segment_metrics(res, D, b, 0, k)

def oos_metrics(res, D, b):
    k = split_index(D)
    return segment_metrics(res, D, b, k, None)

def row(name, m):
    return (f"{name:34s} ret {m['total']*100:7.2f}%  shp {m['sharpe']:5.2f}  mdd {m['mdd']*100:6.2f}%  n {m['n']:4d}  "
            f"hit {m['hit']*100 if m['n'] else 0:5.1f}%  pf {m['pf']:5.2f}  mean {m['mean_trade']*1e4 if m['n'] else 0:6.1f}bp  t {m['t'] if m['n'] else 0:5.2f}")

def diag(res, D, k_is=None):
    """Learning diagnostics on in-sample trades only."""
    k_is = split_index(D) if k_is is None else k_is
    t = pd.DataFrame([x for x in res['trades'] if x['exit_i'] < D.i0 + k_is])
    if t.empty:
        print('  no trades'); return t
    t['bp'] = t.ret * 1e4
    t['hold_min'] = (t.exit_i - t.entry_i) * 390 + t.exit_T - t.entry_T
    t['hour'] = t.entry_T.map(lambda x: hm(x)[:2] + 'h')
    t['why2'] = t.why.str.split(':').str[0]
    print('  by exit:', t.groupby('why2').bp.agg(['count', 'mean']).round(1).to_dict('index'))
    print('  by entry hour:', t.groupby('hour').bp.agg(['count', 'mean']).round(1).to_dict('index'))
    print('  hold min median', t.hold_min.median(), ' win median bp', t.bp[t.bp > 0].median().round(1), ' loss median bp', t.bp[t.bp <= 0].median().round(1))
    return t

def run_gen(gen, strats, D=None, show_diag=False, min_n=30):
    """Backtest a generation; selection uses IN-SAMPLE metrics only. Saves params + IS metrics."""
    import copy
    D = D or data(); b = bench(D); out = []
    for s in strats:
        r = simulate(s, D); m = is_metrics(r, D, b)
        out.append(dict(gen=gen, name=s.name, cls=type(s).__name__, params=s.p, is_=m))
        if show_diag:
            print(row(s.name, m)); diag(r, D)
    ok = [o for o in out if o['is_']['n'] >= min_n]
    out.sort(key=lambda o: (o['is_']['n'] >= min_n, o['is_']['sharpe']), reverse=True)
    print(f'--- generation {gen}: {len(strats)} variants (ranked by in-sample Sharpe, n>={min_n} trades) ---')
    for o in out:
        print(row(o['name'], o['is_']) + ('' if o['is_']['n'] >= min_n else '  [too few trades]'))
    json.dump(out, open(BASE + f'work/gen{gen}.json', 'w'), default=float, indent=1)
    return out
