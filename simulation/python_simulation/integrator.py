"""
Compiled Dormand-Prince 5(4) integrator, modelled on MATLAB's ode45.

Instead of storing the whole trajectory, it tracks only what the KE ratio
needs: the largest kinetic energy of the last mass at the output times.

How it works, in short:
  * Each step tries a step size h, computes 7 slope evaluations ("stages"),
    and combines them into a 5th-order estimate of the new state plus an
    error estimate (difference from the embedded 4th-order estimate).
  * If the error is too big, the step is retried with a smaller h; if it is
    comfortably small, the next h grows. The rules (initial step, error norm,
    growth/shrink factors, max step) follow ode45.m.
  * Output times that fall inside an accepted step are filled in with the
    method's built-in 4th-order interpolation (ode45's ntrp45), evaluated only
    for the last mass's velocity.
"""

import numpy as np
from numba import njit

from .equations_of_motion import rhs_into

# Dormand-Prince tableau in ode45's layout: stage j uses y + h * sum_i B[i, j-1] * f_i
_A = np.array([1 / 5, 3 / 10, 4 / 5, 8 / 9, 1.0, 1.0])
_B = np.array([
    [1 / 5, 3 / 40, 44 / 45, 19372 / 6561, 9017 / 3168, 35 / 384],
    [0, 9 / 40, -56 / 15, -25360 / 2187, -355 / 33, 0],
    [0, 0, 32 / 9, 64448 / 6561, 46732 / 5247, 500 / 1113],
    [0, 0, 0, -212 / 729, 49 / 176, 125 / 192],
    [0, 0, 0, 0, -5103 / 18656, -2187 / 6784],
    [0, 0, 0, 0, 0, 11 / 84],
    [0, 0, 0, 0, 0, 0],
])
# Error weights: 5th-order minus 4th-order solution
_E = np.array([71 / 57600, 0, -71 / 16695, 71 / 1920, -17253 / 339200, 22 / 525, -1 / 40])
# ntrp45 interpolation: y(t + s*h) = y + h * sum_i f_i * (BI[i,0] s + BI[i,1] s^2 + BI[i,2] s^3 + BI[i,3] s^4)
_BI = np.array([
    [1, -183 / 64, 37 / 12, -145 / 128],
    [0, 0, 0, 0],
    [0, 1500 / 371, -1000 / 159, 1000 / 371],
    [0, -125 / 32, 125 / 12, -375 / 64],
    [0, 9477 / 3392, -729 / 106, 25515 / 6784],
    [0, -11 / 7, 11 / 3, -55 / 28],
    [0, 3 / 2, -4, 5 / 2],
])


@njit(cache=True)
def _max_last_ke(y0, t_out, c1, c2, c3, m, m_impact, C_impact, zeta, rtol, atol,
                 A, B, E, BI):
    neq = y0.shape[0]
    iv = neq - 1                       # index of the last mass's velocity
    t0 = t_out[0]
    tfinal = t_out[-1]
    pow_ = 1.0 / 5.0
    threshold = atol / rtol
    hmax = 0.1 * abs(tfinal - t0)

    y = y0.copy()
    ynew = np.empty(neq)
    ytmp = np.empty(neq)
    f = np.empty((7, neq))
    rhs_into(y, c1, c2, c3, m, m_impact, C_impact, zeta, f[0])
    nfevals = 1

    max_ke = 0.5 * y[iv] ** 2          # output point t_out[0]
    nxt = 1

    # Initial step size (ode45.m)
    t = t0
    absh = min(hmax, abs(tfinal - t0))
    rh = 0.0
    for i in range(neq):
        v = abs(f[0, i]) / max(abs(y[i]), threshold)
        if v > rh:
            rh = v
    rh = rh / (0.8 * rtol ** pow_)
    if absh * rh > 1.0:
        absh = 1.0 / rh

    nsteps = 0
    nfailed = 0
    done = False
    while not done:
        hmin = 16.0 * np.spacing(t)
        absh = min(hmax, max(hmin, absh))
        h = absh
        if 1.1 * absh >= abs(tfinal - t):  # stretch the last step to land on tfinal
            h = tfinal - t
            absh = abs(h)
            done = True

        nofailed = True
        while True:
            # Stages 2..7
            for j in range(6):
                for i in range(neq):
                    acc = 0.0
                    for s in range(j + 1):
                        acc += f[s, i] * B[s, j]
                    ytmp[i] = y[i] + h * acc
                if j < 5:
                    rhs_into(ytmp, c1, c2, c3, m, m_impact, C_impact, zeta, f[j + 1])
                else:
                    for i in range(neq):
                        ynew[i] = ytmp[i]
            tnew = t + h
            if done:
                tnew = tfinal
            h = tnew - t
            rhs_into(ynew, c1, c2, c3, m, m_impact, C_impact, zeta, f[6])
            nfevals += 6

            # Error estimate (ode45, NormControl off): infinity norm of scaled error
            err = 0.0
            for i in range(neq):
                fe = 0.0
                for s in range(7):
                    fe += f[s, i] * E[s]
                scale = max(max(abs(y[i]), abs(ynew[i])), threshold)
                v = abs(fe) / scale
                if v > err:
                    err = v
            err = absh * err

            if err > rtol:  # step rejected: shrink and retry
                nfailed += 1
                if absh <= hmin:
                    raise RuntimeError("step size fell below the minimum allowed")
                if nofailed:
                    nofailed = False
                    absh = max(hmin, absh * max(0.1, 0.8 * (rtol / err) ** pow_))
                else:
                    absh = max(hmin, 0.5 * absh)
                h = absh
                done = False
            else:
                break
        nsteps += 1

        # Output times in (t, tnew]: interpolate the last mass's velocity
        while nxt < t_out.shape[0] and t_out[nxt] <= tnew:
            if t_out[nxt] == tnew:
                v_out = ynew[iv]
            else:
                sfrac = (t_out[nxt] - t) / h
                acc = 0.0
                for s in range(7):
                    poly = sfrac * (BI[s, 0] + sfrac * (BI[s, 1] + sfrac * (BI[s, 2] + sfrac * BI[s, 3])))
                    acc += f[s, iv] * poly
                v_out = y[iv] + h * acc
            ke = 0.5 * v_out * v_out
            if ke > max_ke:
                max_ke = ke
            nxt += 1

        # Next step size: grow only if this step had no failures (ode45.m)
        if nofailed:
            temp = 1.25 * (err / rtol) ** pow_
            if temp > 0.2:
                absh = absh / temp
            else:
                absh = 5.0 * absh

        t = tnew
        for i in range(neq):
            y[i] = ynew[i]
            f[0, i] = f[6, i]          # first-same-as-last: reuse the final slope

    return max_ke, nsteps, nfailed, nfevals


def max_last_ke(y0, t_out, c1, c2, c3, m, m_impact, C_impact, zeta, rtol, atol):
    """Integrate from t_out[0] to t_out[-1] and return
    (max over t_out of 0.5 * v_last^2, {"steps", "failed", "fevals"})."""
    ke, nsteps, nfailed, nfevals = _max_last_ke(
        np.asarray(y0, float), np.asarray(t_out, float),
        np.asarray(c1, float), np.asarray(c2, float), np.asarray(c3, float),
        float(m), float(m_impact), float(C_impact), float(zeta), float(rtol), float(atol),
        _A, _B, _E, _BI)
    return ke, {"steps": nsteps, "failed": nfailed, "fevals": nfevals}
