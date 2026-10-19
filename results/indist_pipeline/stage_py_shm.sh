#!/bin/bash
# In-dist pipeline (2026-10-14): the c2stage venvs in /dev/shm still take their stdlib from the uv Python homes on
# Lustre / NFS (pyvenv.cfg home = /projects/.../uv-pythons/cpython-3.12..., /u/bimrose2/.local/share/uv/python/cpython-3.11...),
# so every python start stats/reads the stdlib over the network (processes in D state, ptlrpc_set_wait). This makes
# node-RAM copies of the two Python homes and thin venvs that reuse c2stage's site-packages (symlink) with home pointed
# at the copies. Same interpreter builds, same packages. Idempotent.
#   bash stage_py_shm.sh  ->  /dev/shm/bimrose2/ipcode/{venv,dw_venv}/bin/python
set -euo pipefail
D=/dev/shm/bimrose2/ipcode; C2=/dev/shm/bimrose2/c2stage
[ -f $D/PY_READY ] && { echo "python already staged"; exit 0; }
exec 7>/dev/shm/bimrose2/ipcode_py.lock; flock 7
[ -f $D/PY_READY ] && { echo "python already staged"; exit 0; }
mkdir -p $D
mk() {  # mk <name> <c2stage venv> <python home dir> <pyver>
  local n=$1 src=$2 home=$3 pv=$4
  rsync -a $(readlink -f $home)/ $D/home_$n/
  rm -rf $D/$n; mkdir -p $D/$n/bin $D/$n/lib/python$pv
  for x in python$pv python python3; do cp $src/bin/python$pv $D/$n/bin/$x; done   # real files, as in c2stage (a symlinked bin/python loses the venv)
  ln -s $src/lib/python$pv/site-packages $D/$n/lib/python$pv/site-packages
  ln -s lib $D/$n/lib64
  sed "s|^home = .*|home = $D/home_$n/bin|" $src/pyvenv.cfg > $D/$n/pyvenv.cfg
  $D/$n/bin/python -c "import sys; assert sys.base_prefix.startswith('$D'), sys.base_prefix; assert all(p.startswith('$D') or p.startswith('$C2') or not p for p in sys.path), sys.path; print('$n ok', sys.version.split()[0])"
}
mk venv $C2/venv /projects/illinois/eng/ece/wpk/bimrose2/.local/uv-pythons/cpython-3.12-linux-x86_64-gnu 3.12
mk dw_venv $C2/dw_venv /u/bimrose2/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu 3.11
$D/venv/bin/python -c "import build123d, scipy, PIL, trimesh" && $D/dw_venv/bin/python -c "import draftwright, OCP"
touch $D/PY_READY; echo "python staged"
