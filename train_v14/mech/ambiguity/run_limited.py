"""python run_limited.py <script.py> [args...] — run a script with the subprocess memory cap of limited_exec."""
import os, runpy, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import limited_exec  # noqa: F401,E402
script = sys.argv[1]; sys.argv = sys.argv[1:]
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
runpy.run_path(script, run_name="__main__")
