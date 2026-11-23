from lab import *
from strategies import BandSnap as A, GapFill as B, DailySwing as C
D=data(); b=bench(D)
NO=101
er=set(['2024-08-02','2024-11-01','2025-02-07','2025-05-02','2025-08-01','2025-10-31','2026-02-06','2026-04-30','2026-07-31','2026-10-30'])  # first session after post-market earnings
for s in [B(gap_min=0.005, fill=1.25, name='B3e'), A(n=78,k=2.5,confirm=True,stop_atr=5.0,name='A3a'), C(rsi_entry=NO,trend_sma=None,ibs_max=0.20,min_drop=0.005,stop_pct=None,exit_sma=5,max_days=5,name='C3b')]:
    r=simulate(s,D); print('==',s.name); t=diag(r,D)
    t['date']=t.entry_i.map(lambda i:D.dates[i]); t['earn']=t.date.isin(er)
    print('  earnings-day trades:', t.groupby('earn').bp.agg(['count','mean']).round(1).to_dict('index'))
    # regime: prior 20-day return of AMZN
    dc=D.dly_close; t['r20']=t.entry_i.map(lambda i:(D.official_close[i-1]/dc[D.dpos[D.dates[i]]-21]-1))
    t['r20b']=pd.cut(t.r20,[-1,-0.05,0,0.05,1]); print('  by prior-20d return:', t.groupby('r20b',observed=True).bp.agg(['count','mean']).round(1).to_dict('index'))
    # vol regime: daily ATR% at entry
    da=D.daily_atr(14); t['atrp']=t.entry_i.map(lambda i: da[D.dpos[D.dates[i]]-1]/D.official_close[i-1])
    t['atrb']=pd.qcut(t.atrp,3,labels=['lowvol','midvol','highvol']); print('  by vol tercile:', t.groupby('atrb',observed=True).bp.agg(['count','mean']).round(1).to_dict('index'))
    if s.name=='B3e':
        t['gb']=pd.cut(t.sig_gap,[-1,-0.02,-0.01,-0.0075,-0.005]); print('  by gap size:', t.groupby('gb',observed=True).bp.agg(['count','mean']).round(1).to_dict('index'))
    if s.name=='C3b':
        t['days']=t.exit_i-t.entry_i; print('  by hold days:', t.groupby('days').bp.agg(['count','mean']).round(1).to_dict('index'))
