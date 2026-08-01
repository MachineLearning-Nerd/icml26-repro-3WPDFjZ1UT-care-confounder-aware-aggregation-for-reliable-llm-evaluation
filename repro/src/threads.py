"""Pin BLAS/OpenMP thread pools to the container's real CPU quota.

Must be imported before numpy/scipy/torch: those libraries read the *_NUM_THREADS
environment variables at import time. Inside a cgroup-limited container
os.cpu_count() reports the host's core count, so the default pools oversubscribe
the few vCPUs actually granted and spin-wait dominates the runtime.
"""

from __future__ import annotations

import os


def cpu_quota() -> int:
    """Cores actually usable by this process."""
    try:
        with open("/sys/fs/cgroup/cpu.max") as fh:
            quota, period = fh.read().split()
        if quota != "max":
            return max(1, int(int(quota) / int(period)))
    except OSError:
        pass
    try:
        with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us") as fh:
            quota = int(fh.read())
        with open("/sys/fs/cgroup/cpu/cpu.cfs_period_us") as fh:
            period = int(fh.read())
        if quota > 0:
            return max(1, quota // period)
    except OSError:
        pass
    try:
        return max(1, len(os.sched_getaffinity(0)))
    except AttributeError:
        return max(1, os.cpu_count() or 1)


def pin(n: int | None = None) -> int:
    n = n or cpu_quota()
    for var in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ[var] = str(n)
    return n


NUM_THREADS = pin()
