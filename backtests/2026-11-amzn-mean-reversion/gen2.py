from lab import *
from strategies import BandSnap as A, GapFill as B, DailySwing as C
G = [
 A(confirm=True, k=2.0, stop_atr=2.0, name='A2a reclaim z-2, stop2ATR'),
 A(k=2.0, stop_atr=3.0, trend_ema=200, name='A2b z-2 + above EMA200'),
 A(n=78, k=2.5, confirm=True, stop_atr=3.0, name='A2c 1-day band reclaim z-2.5'),
 A(k=2.0, stop_atr=3.0, rsi_n=14, rsi_max=25, name='A2d z-2 + RSI14<=25'),
 A(k=2.0, stop_atr=6.0, t_from=60, t_to=300, name='A2e z-2 midday 07:30-11:30'),
 A(confirm=True, k=2.0, stop_atr=2.0, exit_z=-0.5, name='A2f reclaim, quick exit z>=-0.5'),
 B(gap_min=0.005, name='B2a gap>=0.5%'),
 B(gap_min=0.010, name='B2b gap>=1.0%'),
 B(gap_min=0.0075, fill=0.5, name='B2c gap>=0.75% half-fill target'),
 B(gap_min=0.0075, stop_daily_atr=1.0, name='B2d gap>=0.75% stop 1xdailyATR'),
 B(gap_min=0.0075, entry_t=20, confirm=True, name='B2e gap>=0.75% enter 06:50 if >open'),
 B(gap_min=0.0075, gap_max=0.04, name='B2f gap 0.75-4%'),
 C(trend_sma=None, name='C2a RSI2<10 no trend filter'),
 C(trend_sma=None, stop_pct=None, name='C2b RSI2<10 no filter no stop'),
 C(trend_sma=None, exit_rsi=65, name='C2c RSI2<10 exit RSI2>65'),
 C(trend_sma=None, rsi_entry=5, stop_pct=0.12, name='C2d RSI2<5 stop12%'),
 C(trend_sma=None, rsi_entry=20, ibs_max=0.25, name='C2e RSI2<20 + IBS<0.25'),
 C(trend_sma=50, name='C2f RSI2<10 above SMA50'),
]
run_gen(2, G)
