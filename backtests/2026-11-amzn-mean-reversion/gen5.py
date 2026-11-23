from lab import *
from strategies import BandSnap as A, GapFill as B, DailySwing as C
a=dict(n=78, k=2.5, confirm=True, stop_atr=5.0)
bb=dict(gap_min=0.005, fill=1.25)
cd=dict(rsi_n=2, rsi_entry=25, trend_sma=None, ibs_max=0.3, stop_pct=None, exit_sma=3, max_days=3)
G = [
 A(**a, min_datr=0.022, max_r20=0.05, name='A5a vol>=2.2% + r20<=5%'),
 A(**a, min_datr=0.022, t_to=90, name='A5b vol>=2.2% + 06:50-08:00'),
 A(**a, min_datr=0.020, name='A5c vol>=2.0% (robustness)'),
 A(**a, min_datr=0.022, max_r20=0.05, t_to=90, name='A5d vol + r20 + 06:50-08:00'),
 A(**{**a,'k':2.0}, min_datr=0.022, max_r20=0.05, name='A5e z-2.0 + vol + r20'),
 A(**a, min_datr=0.025, name='A5f vol>=2.5% (robustness)'),
 B(**bb, max_r20=0.05, stop_gap=1.5, name='B5a r20<=5% + stop 1.5x gap'),
 B(gap_min=0.005, fill=1.5, max_r20=0.05, name='B5b r20<=5% + target 150%'),
 B(**bb, max_r20=0.03, name='B5c r20<=3% (robustness)'),
 B(**bb, max_r20=0.08, name='B5d r20<=8% (robustness)'),
 B(gap_min=0.004, fill=1.25, max_r20=0.05, name='B5e gap>=0.4% + r20<=5%'),
 B(**bb, max_r20=0.05, entry_t=1, name='B5f r20<=5% enter 06:31'),
 C(**cd, max_r20=0.05, name='C5a C4d + r20<=5%'),
 C(**cd, min_datr=0.02, name='C5b C4d + vol>=2.0%'),
 C(**{**cd,'max_days':5}, name='C5c C4d 5-day time stop'),
 C(**{**cd,'rsi_entry':20}, name='C5d C4d RSI2<20'),
 C(**{**cd,'ibs_max':0.25}, name='C5e C4d IBS<0.25 (robustness)'),
 C(**{**cd,'exit_sma':5}, name='C5f C4d exit>SMA5'),
]
run_gen(5, G)
