"""Multi-view method of moments + robust tensor power method.

This is the algorithm named by Assumption D.8(A4) of the paper: the CP recovery
of Anandkumar et al. (2014), applied to the three conditionally independent judge
groups of the CARE-Tensor path. Implemented directly rather than substituted by a
nearby method, so that Theorem 4.3 is tested on its own estimator.
"""

from __future__ import annotations

import numpy as np


def sample_mixture(rng, pi, mus, sigma, n):
    """Draw n i.i.d. samples of (X1, X2, X3) from Assumption D.8's model.

    pi   : (4,) mixture proportions over (Q, C) in {0,1}^2
    mus  : list of 3 arrays, mus[l] has shape (p_l, 4) -- component means per view
    sigma: scalar; within-component covariance is sigma^2 I, so sigma_max = sigma
    """
    r = rng.choice(len(pi), size=n, p=pi)
    views = []
    for l in range(3):
        p_l = mus[l].shape[0]
        views.append(mus[l][:, r].T + sigma * rng.standard_normal((n, p_l)))
    return views, r


def _symmetrize_views(X1, X2, X3):
    """Map views 1 and 2 into view 3's space (Anandkumar et al., multi-view trick).

    x~1 = E[X3 X2^T] E[X1 X2^T]^+ X1 and x~2 = E[X3 X1^T] E[X2 X1^T]^+ X2 have the
    same conditional means as X3, so E[x~1 (x) x~2] and E[x~1 (x) x~2 (x) X3]
    are symmetric in the component factors c_r.
    """
    n = X1.shape[0]
    M32 = X3.T @ X2 / n
    M12 = X1.T @ X2 / n
    M31 = X3.T @ X1 / n
    M21 = X2.T @ X1 / n
    A1 = M32 @ np.linalg.pinv(M12)
    A2 = M31 @ np.linalg.pinv(M21)
    return X1 @ A1.T, X2 @ A2.T


def empirical_moments(X1, X2, X3):
    """Return the symmetrised second and third moments in view-3 coordinates."""
    t1, t2 = _symmetrize_views(X1, X2, X3)
    n = X1.shape[0]
    M2 = (t1.T @ t2) / n
    M2 = 0.5 * (M2 + M2.T)
    M3 = np.einsum("ni,nj,nk->ijk", t1, t2, X3, optimize=True) / n
    M3 = (M3 + M3.transpose(0, 2, 1) + M3.transpose(1, 0, 2)
          + M3.transpose(1, 2, 0) + M3.transpose(2, 0, 1) + M3.transpose(2, 1, 0)) / 6.0
    return M2, M3


def _ttv(T, u, modes):
    out = T
    for m in sorted(modes, reverse=True):
        out = np.tensordot(out, u, axes=([m], [0]))
    return out


def robust_tensor_power(T, k, rng, n_restarts=30, n_iters=60, n_deflate_iters=30):
    """Anandkumar et al. (2014) Algorithm 1: robust tensor power method with deflation."""
    T = T.copy()
    lams, vecs = [], []
    for _ in range(k):
        best_lam, best_v = -np.inf, None
        for _ in range(n_restarts):
            v = rng.standard_normal(T.shape[0])
            v /= np.linalg.norm(v)
            for _ in range(n_iters):
                w = _ttv(T, v, [1, 2])
                nw = np.linalg.norm(w)
                if nw < 1e-300:
                    break
                v = w / nw
            lam = float(_ttv(T, v, [0, 1, 2]))
            if lam > best_lam:
                best_lam, best_v = lam, v
        v = best_v
        for _ in range(n_deflate_iters):
            w = _ttv(T, v, [1, 2])
            nw = np.linalg.norm(w)
            if nw < 1e-300:
                break
            v = w / nw
        lam = float(_ttv(T, v, [0, 1, 2]))
        lams.append(lam)
        vecs.append(v)
        T = T - lam * np.einsum("i,j,k->ijk", v, v, v)
    return np.array(lams), np.array(vecs).T


def recover_weights(M2, M3, k, rng, floor_ratio=1e-6, n_restarts=30):
    """Whiten, run the tensor power method, and return the recovered mixture weights.

    The population M2 is PSD of rank k, but its finite-sample estimate need not be,
    so the top-k eigenvalues are floored at `floor_ratio` times the largest before
    whitening. Returning None instead would silently drop the noisiest settings and
    bias the sigma sweep towards the easy end.
    """
    s, U = np.linalg.eigh(M2)
    idx = np.argsort(s)[::-1][:k]
    s, U = s[idx], U[:, idx]
    if s[0] <= 0 or not np.all(np.isfinite(s)):
        return None
    s = np.maximum(s, floor_ratio * s[0])
    W = U @ np.diag(s ** -0.5)
    Tw = np.einsum("ijk,ia,jb,kc->abc", M3, W, W, W, optimize=True)
    lams, _ = robust_tensor_power(Tw, k, rng, n_restarts=n_restarts)
    with np.errstate(divide="ignore"):
        w_hat = 1.0 / np.maximum(lams, 1e-12) ** 2
    total = w_hat.sum()
    if not np.isfinite(total) or total <= 0:
        return None
    return np.sort(w_hat / total)[::-1]
