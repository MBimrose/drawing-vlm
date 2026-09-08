"""Execute one build123d script and keep only its STEP (no meshing).

    python rerender_exec.py <code.py> <out.step>

The lighter sibling of train_v14/geom/exec_harness.py used by rerender_tars.py:
the script runs in a temp cwd with OUTPUT_PATH="output.step", the STEP is
copied to <out.step> (absolute path). Exit codes: 0 ok, 2 exec error, 3 no /
empty STEP.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import traceback


def main() -> int:
    code_path, out_step = sys.argv[1], os.path.abspath(sys.argv[2])
    with open(code_path, encoding="utf-8", errors="replace") as f:
        code = f.read()
    with tempfile.TemporaryDirectory(prefix="b3dexec_") as td:
        os.chdir(td)
        g: dict = {"__name__": "__main__", "OUTPUT_PATH": "output.step"}
        try:
            exec(compile(code, "<generated>", "exec"), g)  # noqa: S102
        except SystemExit:
            pass
        except Exception:
            traceback.print_exc()
            return 2
        step = os.path.join(td, "output.step")
        if not os.path.exists(step) or os.path.getsize(step) == 0:
            print("no output.step produced", file=sys.stderr)
            return 3
        shutil.copyfile(step, out_step)
    return 0


if __name__ == "__main__":
    sys.exit(main())
