from lab import *
from strategies import BandSnap as A, GapFill as B, DailySwing as C
NO=101  # RSI gate off
G = [
 A(n=78, k=2.5, confirm=True, stop_atr=5.0, name='A3a 1d band reclaim z-2.5 stop5'),
 A(n=78, k=2.0, confirm=True, stop_atr=3.0, name='A3b 1d band reclaim z-2.0'),
 A(n=78, k=3.0, confirm=True, stop_atr=3.0, name='A3c 1d band reclaim z-3.0'),
 A(n=156, k=2.5, confirm=True, stop_atr=3.0, name='A3d 2d band reclaim z-2.5'),
 A(n=78, k=2.5, confirm=True, stop_atr=3.0, exit_z=-0.5, name='A3e 1d reclaim exit z>=-0.5'),
 A(n=78, k=2.5, confirm=True, stop_atr=3.0, trail_atr=4.0, exit_z=0.5, name='A3f 1d reclaim, trail4ATR, exit z>=+0.5'),
 B(gap_min=0.0025, name='B3a gap>=0.25%'),
 B(gap_min=0.0035, name='B3b gap>=0.35%'),
 B(gap_min=0.005, entry_t=1, name='B3c gap>=0.5% enter 06:31'),
 B(gap_min=0.0035, entry_t=1, name='B3d gap>=0.35% enter 06:31'),
 B(gap_min=0.005, fill=1.25, name='B3e gap>=0.5% target 125% fill'),
 B(gap_min=0.005, stop_daily_atr=1.5, name='B3f gap>=0.5% stop 1.5xdailyATR'),
 C(rsi_entry=NO, trend_sma=None, ibs_max=0.15, min_drop=0.01, stop_pct=None, exit_sma=5, max_days=5, name='C3a IBS<0.15 & down>=1%'),
 C(rsi_entry=NO, trend_sma=None, ibs_max=0.20, min_drop=0.005, stop_pct=None, exit_sma=5, max_days=5, name='C3b IBS<0.20 & down>=0.5%'),
 C(rsi_n=3, rsi_entry=20, trend_sma=None, stop_pct=None, exit_sma=5, max_days=7, name='C3c RSI3<20'),
 C(rsi_n=2, rsi_entry=25, trend_sma=None, stop_pct=None, exit_sma=5, max_days=7, name='C3d RSI2<25'),
 C(rsi_n=2, rsi_entry=25, trend_sma=None, ibs_max=0.3, stop_pct=None, exit_sma=3, max_days=5, name='C3e RSI2<25 & IBS<0.3, exit>SMA3'),
 C(rsi_entry=NO, trend_sma=None, ibs_max=0.15, min_drop=0.01, stop_pct=0.06, exit_sma=5, max_days=5, name='C3f IBS<0.15 & down>=1%, stop6%'),
]
run_gen(3, G)
