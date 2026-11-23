"""IRRM backtest engine (conventions v1) for AMZN mean-reversion research.

Time model: each session has minute index m = minutes since 06:30 PT.
A check at time T (minute index) may use 1-minute bars with start <= T-1 and
5-minute bars ending <= T. A decision at T fills at the open of minute bar T.
"""
import math
import numpy as np
import pandas as pd

BASE = '/tmp/claude-0/-home-user-irrm/58f3d338-e66f-5e8a-96e7-9564be3ab107/scratchpad/'
RANGE_START = '2024-11-26'   # first session after >=400 completed 5-min warm-up bars
RANGE_END = '2026-11-20'


# ----------------------------------------------------------------- data
class Data:
    def __init__(self):
        m = pd.read_pickle(BASE + 'data/amzn_1m.pkl')
        dly = pd.read_pickle(BASE + 'data/amzn_daily.pkl').set_index('date')
        self.dates = sorted(m.date.unique())
        nd = len(self.dates)
        self.O = np.full((nd, 390), np.nan); self.H = self.O.copy(); self.L = self.O.copy(); self.C = self.O.copy()
        di = {d: i for i, d in enumerate(self.dates)}
        r = m.date.map(di).values; c = m['mod'].values
        self.O[r, c] = m.o.values; self.H[r, c] = m.h.values; self.L[r, c] = m.l.values; self.C[r, c] = m.c.values
        self.nbars = (~np.isnan(self.O)).sum(1)            # 390 or 211
        self.close_min = np.where(self.nbars == 390, 390, 210)  # session close (minute index)
        self.half = self.nbars != 390
        self.official_close = dly.close.reindex(self.dates).values
        # full daily history (from 2024-01-02) for daily indicators
        self.dly = dly
        self.dly_dates = list(dly.index)
        self.dly_close = dly.close.values
        self.dly_high = dly.high.values; self.dly_low = dly.low.values; self.dly_open = dly.open.values
        self.dpos = {d: self.dly_dates.index(d) for d in self.dates}  # position of session in daily history
        # 5-minute bars (complete groups only), continuous across sessions
        o5, h5, l5, c5, day5, end5 = [], [], [], [], [], []
        self.start5 = np.zeros(nd, int)
        for i in range(nd):
            self.start5[i] = len(c5)
            nb = self.nbars[i]
            for k in range(nb // 5):
                s = slice(5 * k, 5 * k + 5)
                o5.append(self.O[i, 5 * k]); h5.append(np.nanmax(self.H[i, s])); l5.append(np.nanmin(self.L[i, s]))
                c5.append(self.C[i, 5 * k + 4]); day5.append(i); end5.append(5 * k + 5)
        self.o5, self.h5, self.l5, self.c5 = map(np.array, (o5, h5, l5, c5))
        self.day5 = np.array(day5); self.end5 = np.array(end5)
        self.n5 = nd and np.array([self.nbars[i] // 5 for i in range(nd)])
        rf = pd.read_csv(BASE + 'data/tbill3m.csv').set_index('month')['yield'] / 100 / 252
        self.rf = np.array([rf[d[:7]] for d in self.dates])
        self.i0 = self.dates.index(RANGE_START); self.i1 = self.dates.index(RANGE_END)
        self._cache = {}

    def last5(self, i, T):
        """global index of the latest 5-minute bar completed by check T of session i"""
        k = T // 5
        k = min(k, self.n5[i])
        if k >= 1:
            return self.start5[i] + k - 1
        return self.start5[i] - 1  # last bar of previous session

    # ---- 5-minute indicators (cached, computed on the whole continuous series)
    def ema5(self, n):
        key = ('ema', n)
        if key not in self._cache:
            self._cache[key] = ema(self.c5, n)
        return self._cache[key]

    def sma5(self, n):
        key = ('sma', n)
        if key not in self._cache:
            self._cache[key] = pd.Series(self.c5).rolling(n).mean().values
        return self._cache[key]

    def sd5(self, n):
        key = ('sd', n)
        if key not in self._cache:
            self._cache[key] = pd.Series(self.c5).rolling(n).std(ddof=0).values
        return self._cache[key]

    def rsi5(self, n):
        key = ('rsi', n)
        if key not in self._cache:
            self._cache[key] = wilder_rsi(self.c5, n)
        return self._cache[key]

    def atr5(self, n=14):
        key = ('atr', n)
        if key not in self._cache:
            pc = np.r_[np.nan, self.c5[:-1]]
            tr = np.nanmax(np.vstack([self.h5 - self.l5, np.abs(self.h5 - pc), np.abs(self.l5 - pc)]), 0)
            self._cache[key] = pd.Series(tr).rolling(n).mean().values
        return self._cache[key]

    def daily_atr(self, n=14):
        key = ('datr', n)
        if key not in self._cache:
            c = self.dly_close; pc = np.r_[np.nan, c[:-1]]
            tr = np.nanmax(np.vstack([self.dly_high - self.dly_low, np.abs(self.dly_high - pc), np.abs(self.dly_low - pc)]), 0)
            self._cache[key] = pd.Series(tr).rolling(n).mean().values  # atr through day j (inclusive)
        return self._cache[key]


def ema(x, n):
    a = 2 / (n + 1); out = np.empty_like(x); out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def wilder_rsi(x, n):
    d = np.diff(x); g = np.clip(d, 0, None); l = np.clip(-d, 0, None)
    out = np.full(len(x), np.nan)
    if len(d) < n:
        return out
    ag = g[:n].mean(); al = l[:n].mean()
    out[n] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n, len(d)):
        ag = (ag * (n - 1) + g[i]) / n; al = (al * (n - 1) + l[i]) / n
        out[i + 1] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def rsi_last(closes, n):
    """Wilder RSI value at the end of a short close array (seeded over the array)."""
    r = wilder_rsi(np.asarray(closes, float), n)
    return r[-1]


# ----------------------------------------------------------------- simulation
class Ctx:
    """What a strategy may see at check (i, T)."""
    __slots__ = ('D', 'i', 'T', 'j5', 'price', 'eod', 'overnight_ok')


def checks_for(D, i, extra):
    close = D.close_min[i]
    grid = set(range(0, close, 4))
    for t in extra:
        if t < close:
            grid.add(t)
    return sorted(grid)


def floor6(x):
    return math.floor(x * 1e6) / 1e6


def simulate(strat, D, cost=1e-4, start=5.0, cap=100.0, i0=None, i1=None, record=True):
    """Run one strategy. Returns dict with equity (per session in range), trades, minutes in market."""
    i0 = D.i0 if i0 is None else i0; i1 = D.i1 if i1 is None else i1
    bal = start; pos = None; trades = []; equity = []; minutes_in = 0; nights = 0
    extra = getattr(strat, 'extra_checks', ())
    eod_t_full, eod_t_half = 380, 200     # 12:50 PT, and 09:50 PT on half days
    strat.reset(D)
    ctx = Ctx(); ctx.D = D
    for i in range(i0, i1 + 1):
        if pos is not None:
            nights += 1  # held from previous session's close into this session
            pos['scan'] = 0
        eod_t = eod_t_half if D.half[i] else eod_t_full
        cl = D.close_min[i]
        for T in checks_for(D, i, extra + ((eod_t,) if strat.intraday else ())):
            # 1) resting stop fill test on 1-minute bars [scan, T-1]
            if pos is not None and pos['stop'] is not None and T > pos['scan']:
                lo = D.L[i, pos['scan']:T]
                hit = np.nonzero(lo <= pos['stop'])[0]
                if len(hit):
                    m = pos['scan'] + hit[0]
                    px = min(pos['stop'], D.O[i, m])
                    bal = _close(pos, px, cost, i, m, 'stop:' + pos['stop_reason'], trades)
                    minutes_in += m - pos['in_from']; pos = None
                else:
                    pos['scan'] = T
            ctx.i = i; ctx.T = T; ctx.j5 = D.last5(i, T)
            ctx.price = D.C[i, T - 1] if T >= 1 else D.official_close[i - 1]
            fill = D.O[i, T]
            # 2) exits
            if pos is not None:
                if strat.intraday and T >= eod_t:
                    bal = _close(pos, fill, cost, i, T, 'eod', trades); minutes_in += T - pos['in_from']; pos = None
                else:
                    strat.update_stop(pos, ctx)
                    why = strat.exit(pos, ctx)
                    if why:
                        bal = _close(pos, fill, cost, i, T, why, trades); minutes_in += T - pos['in_from']; pos = None
            # 3) entries
            if pos is None and not (strat.intraday and T >= eod_t):
                sig = strat.entry(ctx)
                if sig:
                    amt = min(bal, cap); px = fill * (1 + cost)
                    sh = floor6(amt / px)
                    pos = dict(entry_i=i, entry_T=T, cost_price=px, raw_entry=fill, shares=sh, basis=sh * px,
                               cash_left=bal - sh * px, peak=fill, scan=T, in_from=T, stop=None, stop_reason='',
                               sig=sig if isinstance(sig, dict) else {})
                    strat.init_stop(pos, ctx)
        # resting stop stays live through the remaining bars of the session
        if pos is not None and pos['stop'] is not None and pos['scan'] < cl:
            lo = D.L[i, pos['scan']:cl]
            hit = np.nonzero(lo <= pos['stop'])[0]
            if len(hit):
                m = pos['scan'] + hit[0]
                bal = _close(pos, min(pos['stop'], D.O[i, m]), cost, i, m, 'stop:' + pos['stop_reason'], trades)
                minutes_in += m - pos['in_from']; pos = None
        if pos is not None:
            minutes_in += cl - pos['in_from']; pos['in_from'] = 0
        eq = bal if pos is None else pos['cash_left'] + pos['shares'] * D.official_close[i]
        equity.append(eq)
    open_trade = None
    if pos is not None:
        open_trade = dict(entry_date=D.dates[pos['entry_i']], mark=D.official_close[i1],
                          ret=(pos['shares'] * D.official_close[i1]) / pos['basis'] - 1)
    return dict(equity=np.array(equity), trades=trades, minutes_in=minutes_in, nights=nights, open_trade=open_trade,
                dates=D.dates[i0:i1 + 1], rf=D.rf[i0:i1 + 1])


def _close(pos, raw_px, cost, i, m, why, trades):
    px = raw_px * (1 - cost)
    proceeds = pos['shares'] * px
    trades.append(dict(entry_i=pos['entry_i'], entry_T=pos['entry_T'], exit_i=i, exit_T=m, why=why,
                       ret=proceeds / pos['basis'] - 1, pnl=proceeds - pos['basis'],
                       entry_px=pos['raw_entry'], exit_px=raw_px, **{('sig_' + k): v for k, v in pos['sig'].items()}))
    return pos['cash_left'] + proceeds


class BuyHold:
    intraday = False; extra_checks = ()
    def reset(self, D): self.done = False
    def entry(self, c):
        if self.done: return False
        self.done = True; return True
    def init_stop(self, p, c): pass
    def update_stop(self, p, c): pass
    def exit(self, p, c): return None


# ----------------------------------------------------------------- metrics
def segment_metrics(res, D, bench=None, a=None, b=None, start=5.0):
    """Metrics on sessions [a, b) of the result (indices into res['equity'])."""
    eq = res['equity']; n = len(eq)
    a = 0 if a is None else a; b = n if b is None else b
    prev = start if a == 0 else eq[a - 1]
    seg = eq[a:b]
    r = seg / np.r_[prev, seg[:-1]] - 1
    rf = res['rf'][a:b]; ex = r - rf
    tr = seg[-1] / prev - 1
    days = len(seg)
    sharpe = ex.mean() / ex.std(ddof=1) * math.sqrt(252) if ex.std() > 0 else 0.0
    dd_ = np.sqrt(np.mean(np.minimum(ex, 0) ** 2))
    sortino = ex.mean() / dd_ * math.sqrt(252) if dd_ > 0 else 0.0
    curve = np.r_[prev, seg]; peak = np.maximum.accumulate(curve); ddser = curve / peak - 1
    mdd = ddser.min(); t_idx = ddser.argmin(); p_idx = curve[:t_idx + 1].argmax()
    rec = np.nonzero(curve[t_idx:] >= peak[t_idx])[0]
    dates = ['start'] + list(res['dates'][a:b])
    ann = (1 + tr) ** (252 / days) - 1
    out = dict(total=tr, ann=ann, vol=r.std(ddof=1) * math.sqrt(252), sharpe=sharpe, sortino=sortino,
               mdd=mdd, mdd_peak=dates[p_idx], mdd_trough=dates[t_idx],
               mdd_recovered=(dates[t_idx + rec[0]] if len(rec) and mdd < 0 else ('n/a' if mdd == 0 else 'not recovered')),
               calmar=(ann / -mdd if mdd < 0 else np.nan), worst_day=r.min(), days=days)
    if bench is not None:
        beq = bench['equity']; bprev = start if a == 0 else beq[a - 1]; bseg = beq[a:b]
        rb = bseg / np.r_[bprev, bseg[:-1]] - 1; exb = rb - rf
        beta = np.cov(ex, exb)[0, 1] / exb.var(ddof=1)
        out.update(beta=beta, alpha=(ex.mean() - beta * exb.mean()) * 252, corr=np.corrcoef(r, rb)[0, 1],
                   ir=((r - rb).mean() / (r - rb).std(ddof=1) * math.sqrt(252)), bench_total=bseg[-1] / bprev - 1)
    # trades exiting in the segment
    d0 = D.i0 + a; d1 = D.i0 + b
    t = [x for x in res['trades'] if d0 <= x['exit_i'] < d1]
    rets = np.array([x['ret'] for x in t])
    out['n'] = len(t)
    if len(t):
        w = rets[rets > 0]; l = rets[rets <= 0]
        out.update(hit=len(w) / len(t), avg_win=w.mean() if len(w) else 0, avg_loss=l.mean() if len(l) else 0,
                   pf=(w.sum() / -l.sum() if len(l) and l.sum() < 0 else np.inf), worst_trade=rets.min(),
                   mean_trade=rets.mean(), t=(rets.mean() / (rets.std(ddof=1) / math.sqrt(len(t))) if len(t) > 1 and rets.std() > 0 else 0))
    else:
        out.update(hit=np.nan, avg_win=np.nan, avg_loss=np.nan, pf=np.nan, worst_trade=np.nan, mean_trade=np.nan, t=np.nan)
    return out


def split_index(D):
    """Out-of-sample = most recent 30% of sessions in the range (>= 6 months)."""
    n = D.i1 - D.i0 + 1
    k = n - int(round(0.3 * n))
    return k  # sessions [0,k) in-sample, [k,n) out-of-sample
