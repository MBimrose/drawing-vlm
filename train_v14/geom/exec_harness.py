"""Execute one build123d script in isolation and mesh its STEP output.

Called as a subprocess by the eval worker / GT builder:

    python exec_harness.py <code.py> <out.stl> [<out.step>]

Runs the script in a temp cwd (so `export_step(part, "output.step")` lands
there), then loads output.step with build123d and writes a tessellated STL;
with a third argument the STEP file itself is also copied there (serving).
Exit codes: 0 ok, 2 exec error, 3 no/empty STEP, 4 mesh error.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import traceback


def main() -> int:
    code_path, out_stl = sys.argv[1], sys.argv[2]
    out_step = sys.argv[3] if len(sys.argv) > 3 else None
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
        if out_step:
            shutil.copyfile(step, out_step)
        try:
            from build123d import Mesher, import_step
            shape = import_step(step)
            m = Mesher()
            m.add_shape(shape, angular_deflection=0.5)
            m.write(out_stl)  # Mesher infers format from extension
        except Exception:
            # Fallback: OCP STL writer via export_stl
            try:
                from build123d import export_stl, import_step
                shape = import_step(step)
                export_stl(shape, out_stl)
            except Exception:
                traceback.print_exc()
                return 4
        if not os.path.exists(out_stl) or os.path.getsize(out_stl) == 0:
            return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
