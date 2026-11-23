from lab import *
from strategies import BandSnap as A, GapFill as B, DailySwing as C
NO=101
a=dict(n=78, k=2.5, confirm=True, stop_atr=5.0)
bb=dict(gap_min=0.005, fill=1.25)
c=dict(rsi_entry=NO, trend_sma=None, ibs_max=0.20, min_drop=0.005, stop_pct=None, exit_sma=5)
G = [
 A(**a, t_to=90, name='A4a A3a entries 06:50-08:00'),
 A(**a, max_r20=0.05, name='A4b A3a + r20<=5%'),
 A(**a, max_r20=0.0, name='A4c A3a + r20<=0%'),
 A(**a, min_datr=0.022, name='A4d A3a + dailyATR>=2.2%'),
 A(**a, t_to=90, max_r20=0.05, name='A4e A3a 06:50-08:00 + r20<=5%'),
 A(**a, max_hold=120, name='A4f A3a + 2h time stop'),
 B(**bb, max_r20=0.05, name='B4a B3e + r20<=5%'),
 B(**bb, max_r20=0.0, name='B4b B3e + r20<=0%'),
 B(gap_min=0.005, fill=1.5, name='B4c gap>=0.5% target 150%'),
 B(gap_min=0.004, fill=1.25, name='B4d gap>=0.4% target 125%'),
 B(**bb, stop_gap=1.5, name='B4e B3e stop 1.5x gap'),
 B(**bb, min_datr=0.022, name='B4f B3e + dailyATR>=2.2%'),
 C(**c, max_days=3, name='C4a C3b + 3-day time stop'),
 C(**c, max_days=3, max_r20=0.05, name='C4b C3b 3-day + r20<=5%'),
 C(**c, max_days=2, name='C4c C3b + 2-day time stop'),
 C(rsi_n=2, rsi_entry=25, trend_sma=None, ibs_max=0.3, stop_pct=None, exit_sma=3, max_days=3, name='C4d C3e + 3-day time stop'),
 C(**{**c,'stop_pct':0.06}, max_days=3, name='C4e C3b 3-day + stop6%'),
 C(**{**c,'ibs_max':0.25}, max_days=3, name='C4f IBS<0.25 3-day'),
]
run_gen(4, G)
