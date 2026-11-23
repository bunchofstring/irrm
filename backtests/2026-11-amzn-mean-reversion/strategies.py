"""Mean-reversion strategy families. All long-only. Times are minutes after 06:30 PT."""
import numpy as np


def regime_ok(D, i, max_r20=None, min_datr=None):
    """Regime filter using only data known before the session: prior 20-session return and daily ATR%."""
    p = D.dpos[D.dates[i]]; dc = D.dly_close
    if max_r20 is not None and dc[p - 1] / dc[p - 21] - 1 > max_r20:
        return False
    if min_datr is not None and D.daily_atr(14)[p - 1] / dc[p - 1] < min_datr:
        return False
    return True


def hm(t):
    return f"{6 + (30 + t) // 60:02d}:{(30 + t) % 60:02d}"


# ------------------------------------------------------------- Family A: intraday band snap-back
class BandSnap:
    """5-min Bollinger z-score reversion inside the session.
    BUY when the latest completed 5-min close is >= k standard deviations below its n-bar SMA.
    SELL when a later completed 5-min close is back at/above the SMA (mean), or the ATR stop fills, or EOD."""
    intraday = True

    def __init__(self, n=20, k=2.0, t_from=20, t_to=360, stop_atr=1.5, exit_z=0.0, trend_ema=None,
                 max_hold=None, rsi_n=None, rsi_max=None, trail_atr=None, min_sd_pct=None, name=None, confirm=False, max_r20=None, min_datr=None):
        self.p = dict(max_r20=max_r20, min_datr=min_datr, n=n, k=k, t_from=t_from, t_to=t_to, stop_atr=stop_atr, exit_z=exit_z, trend_ema=trend_ema,
                      max_hold=max_hold, rsi_n=rsi_n, rsi_max=rsi_max, trail_atr=trail_atr, min_sd_pct=min_sd_pct,
                      confirm=confirm)
        self.name = name or 'A'
        self.extra_checks = ()

    def reset(self, D):
        p = self.p; self.D = D
        self.sma = D.sma5(p['n']); self.sd = D.sd5(p['n']); self.atr = D.atr5(14)
        self.ema_t = D.ema5(p['trend_ema']) if p['trend_ema'] else None
        self.rsi = D.rsi5(p['rsi_n']) if p['rsi_n'] else None
        self.last_sig = -1

    def z(self, j):
        return (self.D.c5[j] - self.sma[j]) / self.sd[j] if self.sd[j] > 0 else 0.0

    def entry(self, c):
        p = self.p
        if not (p['t_from'] <= c.T <= p['t_to']): return False
        if not regime_ok(self.D, c.i, p['max_r20'], p['min_datr']): return False
        j = c.j5
        if j == self.last_sig or self.D.day5[j] != c.i: return False
        z = self.z(j)
        if p['confirm']:
            # reclaim: previous completed bar closed >= k SD below the mean, this bar closed back above -k
            if self.D.day5[j - 1] != c.i or not (self.z(j - 1) <= -p['k'] < z): return False
        elif z > -p['k']: return False
        if p['min_sd_pct'] and self.sd[j] / self.sma[j] < p['min_sd_pct']: return False
        if self.ema_t is not None and self.D.c5[j] < self.ema_t[j]: return False
        if self.rsi is not None and self.rsi[j] > p['rsi_max']: return False
        self.last_sig = j
        return dict(z=z, atr=self.atr[j], j=j)

    def init_stop(self, pos, c):
        pos['atr'] = pos['sig']['atr']
        pos['stop'] = pos['cost_price'] - self.p['stop_atr'] * pos['atr']; pos['stop_reason'] = 'initial'

    def update_stop(self, pos, c):
        pos['peak'] = max(pos['peak'], c.price)
        if self.p['trail_atr']:
            tr = pos['peak'] - self.p['trail_atr'] * pos['atr']
            if tr > pos['stop']:
                pos['stop'] = tr; pos['stop_reason'] = 'trailing'

    def exit(self, pos, c):
        j = c.j5
        if j > pos['sig']['j'] and self.z(j) >= self.p['exit_z']:
            return 'mean'
        if self.p['max_hold'] and (c.T - pos['entry_T']) >= self.p['max_hold'] and c.i == pos['entry_i']:
            return 'time'
        return None


# ------------------------------------------------------------- Family B: opening-gap fill
class GapFill:
    """Session-to-session reversion. BUY at the entry check when today's open gapped down by >= gap_min
    versus the previous official close. SELL when price recovers `fill` of the gap, or the stop fills, or EOD."""
    intraday = True

    def __init__(self, gap_min=0.0075, gap_max=None, entry_t=4, fill=1.0, stop_gap=1.0, confirm=False,
                 max_t=None, name=None, stop_daily_atr=None, max_r20=None, min_datr=None):
        self.p = dict(max_r20=max_r20, min_datr=min_datr, gap_min=gap_min, gap_max=gap_max, entry_t=entry_t, fill=fill, stop_gap=stop_gap,
                      confirm=confirm, max_t=max_t, stop_daily_atr=stop_daily_atr)
        self.name = name or 'B'
        self.extra_checks = (entry_t,)

    def reset(self, D):
        self.D = D; self.datr = D.daily_atr(14)

    def entry(self, c):
        p = self.p; D = self.D
        if c.T != p['entry_t']: return False
        if not regime_ok(D, c.i, p['max_r20'], p['min_datr']): return False
        pc = D.official_close[c.i - 1]; op = D.O[c.i, 0]
        g = op / pc - 1
        if g > -p['gap_min']: return False
        if p['gap_max'] and g < -p['gap_max']: return False
        if p['confirm'] and c.price <= op:  # require the first minutes to trade back above the open
            return False
        return dict(gap=g, pc=pc, op=op)

    def init_stop(self, pos, c):
        s = pos['sig']; gap_abs = s['pc'] - s['op']
        if self.p['stop_daily_atr']:
            dp = self.D.dpos[self.D.dates[c.i]]
            risk = self.p['stop_daily_atr'] * self.datr[dp - 1]
        else:
            risk = self.p['stop_gap'] * gap_abs
        pos['stop'] = pos['cost_price'] - risk; pos['stop_reason'] = 'initial'
        pos['target'] = s['op'] + self.p['fill'] * gap_abs

    def update_stop(self, pos, c):
        pass

    def exit(self, pos, c):
        if c.price >= pos['target']:
            return 'target'
        if self.p['max_t'] and c.T >= self.p['max_t']:
            return 'time'
        return None


# ------------------------------------------------------------- Family C: multi-day oversold swing
class DailySwing:
    """Daily-bar reversion. Near the close (entry_t), compute daily RSI(rsi_n) with the current price as
    today's close. BUY if RSI < rsi_entry (and optional trend filter). SELL at any later check when the
    current price is above the SMA(exit_sma) of daily closes (current price as today's close), or after
    max_days sessions, or the hard stop fills. Holds overnight."""
    intraday = False

    def __init__(self, rsi_n=2, rsi_entry=10, trend_sma=200, exit_sma=5, max_days=10, stop_pct=0.08,
                 entry_t=370, exit_from_t=0, ibs_max=None, name=None, exit_rsi=None, min_drop=None, max_r20=None, min_datr=None):
        self.p = dict(max_r20=max_r20, min_datr=min_datr, rsi_n=rsi_n, rsi_entry=rsi_entry, trend_sma=trend_sma, exit_sma=exit_sma, max_days=max_days,
                      stop_pct=stop_pct, entry_t=entry_t, exit_from_t=exit_from_t, ibs_max=ibs_max, exit_rsi=exit_rsi,
                      min_drop=min_drop)
        self.name = name or 'C'
        self.extra_checks = (entry_t,)

    def reset(self, D):
        self.D = D; n = self.p['rsi_n']
        c = D.dly_close; d = np.diff(c); g = np.clip(d, 0, None); l = np.clip(-d, 0, None)
        ag = np.full(len(c), np.nan); al = np.full(len(c), np.nan)
        ag[n] = g[:n].mean(); al[n] = l[:n].mean()
        for k in range(n, len(d)):
            ag[k + 1] = (ag[k] * (n - 1) + g[k]) / n; al[k + 1] = (al[k] * (n - 1) + l[k]) / n
        self.ag, self.al = ag, al   # state after daily close k

    def rsi_now(self, p_idx, price):
        n = self.p['rsi_n']; prev = self.D.dly_close[p_idx - 1]
        d = price - prev
        ag = (self.ag[p_idx - 1] * (n - 1) + max(d, 0)) / n; al = (self.al[p_idx - 1] * (n - 1) + max(-d, 0)) / n
        return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)

    def sma_now(self, p_idx, price, n):
        return (self.D.dly_close[p_idx - n + 1:p_idx].sum() + price) / n

    def entry(self, c):
        p = self.p; D = self.D
        if c.T != p['entry_t']: return False
        if not regime_ok(D, c.i, p['max_r20'], p['min_datr']): return False
        pi = D.dpos[D.dates[c.i]]
        r = self.rsi_now(pi, c.price)
        if r >= p['rsi_entry']: return False
        if p['trend_sma'] and c.price < self.sma_now(pi, c.price, p['trend_sma']): return False
        if p['ibs_max'] is not None:
            hi = np.nanmax(D.H[c.i, :c.T]); lo = np.nanmin(D.L[c.i, :c.T])
            if hi > lo and (c.price - lo) / (hi - lo) > p['ibs_max']: return False
        if p['min_drop'] and c.price / D.dly_close[pi - 1] - 1 > -p['min_drop']: return False
        return dict(rsi=r)

    def init_stop(self, pos, c):
        if self.p['stop_pct']:
            pos['stop'] = pos['cost_price'] * (1 - self.p['stop_pct']); pos['stop_reason'] = 'hard'

    def update_stop(self, pos, c):
        pass

    def exit(self, pos, c):
        p = self.p; D = self.D
        if c.i == pos['entry_i']: return None
        if c.T < p['exit_from_t']: return None
        pi = D.dpos[D.dates[c.i]]
        if p['exit_rsi'] is not None:
            if self.rsi_now(pi, c.price) > p['exit_rsi']: return 'rsi_exit'
        elif c.price > self.sma_now(pi, c.price, p['exit_sma']):
            return 'above_sma'
        if p['max_days'] and (c.i - pos['entry_i']) >= p['max_days']:
            return 'time'
        return None
