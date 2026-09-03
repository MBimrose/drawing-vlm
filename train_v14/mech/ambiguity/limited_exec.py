"""Cap the address space of every build123d execution subprocess (a runaway
candidate script OOM-killed a 160 GB scoring job).  Import before any
exec_to_stl call, or use run_limited.py to wrap an existing script."""
import resource, subprocess
LIMIT = 24 << 30   # 24 GB per candidate process
_run = subprocess.run
def _limited_run(*a, **kw):
    kw.setdefault("preexec_fn", lambda: resource.setrlimit(resource.RLIMIT_AS, (LIMIT, LIMIT)))
    return _run(*a, **kw)
subprocess.run = _limited_run
