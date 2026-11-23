from lab import *
from engine import segment_metrics
from strategies import BandSnap as A, GapFill as B, DailySwing as C
import math
D=data(); k=split_index(D); n=D.i1-D.i0+1
a=dict(n=78, k=2.5, confirm=True, stop_atr=5.0)
bb=dict(gap_min=0.005, fill=1.25)
cd=dict(rsi_n=2, rsi_entry=25, trend_sma=None, ibs_max=0.3, stop_pct=None, exit_sma=3, max_days=3)
FIN = {
 'A5f': lambda: A(**a, min_datr=0.025, name='A5f Volatile-day band reclaim'),
 'A5b': lambda: A(**a, min_datr=0.022, t_to=90, name='A5b Early band reclaim (vol>=2.2%)'),
 'A5a': lambda: A(**a, min_datr=0.022, max_r20=0.05, name='A5a Band reclaim, vol + 20d filter'),
 'B5a': lambda: B(**bb, max_r20=0.05, stop_gap=1.5, name='B5a Gap-fill overshoot, 20d filter'),
 'B4a': lambda: B(**bb, max_r20=0.05, name='B4a Gap-fill overshoot, 20d filter, 1x stop'),
 'C4d': lambda: C(**cd, name='C4d Weak-close RSI2 swing (3-day)'),
 'C5b': lambda: C(**cd, min_datr=0.02, name='C5b Weak-close RSI2 swing + vol'),
 'G1A': lambda: A(name='A1 (gen-1 baseline)'), 'G1B': lambda: B(name='B1 (gen-1 baseline)'), 'G1C': lambda: C(name='C1 (gen-1 baseline)'),
}
def total(res): return res['equity'][-1]/5-1
out={}
bres={c: bench(D,c) for c in [0,1e-4,2e-4,5e-4]}
b=bres[1e-4]
def months(res):
    eq=pd.Series(res['equity'],index=pd.to_datetime(res['dates']))
    me=eq.resample('ME').last(); prev=me.shift(1); prev.iloc[0]=5.0
    return {d.strftime('%Y-%m'):v for d,v in (me/prev-1).items()}
def years(res):
    eq=pd.Series(res['equity'],index=pd.to_datetime(res['dates']))
    ye=eq.resample('YE').last(); prev=ye.shift(1); prev.iloc[0]=5.0
    return {d.strftime('%Y'):v for d,v in (ye/prev-1).items()}
def breakeven(mk, target_fn):
    lo,hi=0.0,0.02
    f=lambda c: total(simulate(mk(),D,cost=c))-target_fn(c)
    if f(lo)<=0: return None
    if f(hi)>0: return hi
    for _ in range(30):
        mid=(lo+hi)/2
        (lo,hi)=(mid,hi) if f(mid)>0 else (lo,mid)
    return (lo+hi)/2
bh_total=lambda c: total(simulate(BuyHold(),D,cost=c))
for key,mk in list(FIN.items())+[('BH',BuyHold)]:
    s=mk(); res={c:simulate(mk(),D,cost=c) for c in [0,1e-4,2e-4,5e-4]}; r=res[1e-4]
    e=dict(name=getattr(s,'name','AMZN buy & hold'), params=getattr(s,'p',{}),
      full=segment_metrics(r,D,b), is_=segment_metrics(r,D,b,0,k), oos=segment_metrics(r,D,b,k,None),
      cost={str(int(c*1e4)):total(res[c]) for c in res},
      years=years(r), months=months(r), equity=list(r['equity']),
      time_in_mkt=r['minutes_in']/sum(D.close_min[D.i0:D.i1+1]), nights=r['nights']/(n-1),
      open_trade=r['open_trade'], end_bal=r['equity'][-1], pnl=r['equity'][-1]-5, pnl_day=(r['equity'][-1]-5)/n,
      exits=pd.Series([t['why'].split(':')[0] for t in r['trades']]).value_counts().to_dict())
    if key not in ('BH',) and not key.startswith('G1'):
        e['be_zero']=breakeven(mk, lambda c:0.0); e['be_bh']=breakeven(mk, bh_total)
    out[key]=e
    f,i_,o=e['full'],e['is_'],e['oos']
    print(f"{key:4s} {e['name'][:40]:40s} FULL {f['total']*100:6.2f}% shp {f['sharpe']:5.2f} mdd {f['mdd']*100:6.2f}% n {f['n']:3d} t {f.get('t',0) if f['n'] else 0:5.2f} | IS {i_['total']*100:6.2f}% shp {i_['sharpe']:5.2f} | OOS {o['total']*100:6.2f}% shp {o['sharpe']:5.2f} mdd {o['mdd']*100:6.2f}% n {o['n']:3d} | cost0/1/2/5 " + ' '.join(f"{v*100:.1f}" for v in e['cost'].values()) + (f" | BE0 {e['be_zero']*1e4 if e['be_zero'] else 0:.1f}bp BEbh {e['be_bh']*1e4 if e['be_bh'] else 0:.1f}bp" if 'be_zero' in e else ''))
out['_meta']=dict(dates=D.dates[D.i0:D.i1+1], split=D.dates[D.i0+k], is_range=[D.dates[D.i0],D.dates[D.i0+k-1]], oos_range=[D.dates[D.i0+k],D.dates[D.i1]], sessions=n)
json.dump(out,open(BASE+'work/final.json','w'),default=lambda x: float(x) if isinstance(x,(np.floating,np.integer)) else str(x),indent=1)
