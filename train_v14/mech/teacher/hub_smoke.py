"""Smoke test: send one rendered sheet to a model on the lab hub router
(Anthropic Messages API) and report whether it returns a build123d script.

    python hub_smoke.py <png> [model]
Key: $ANTHROPIC_API_KEY, else ~/.claude-hub/my.key, else /srv/scratch/claude-hub/lab.key.
"""
import base64
import json
import os
import sys
import time
import urllib.request

ROUTER = os.environ.get("CLAUDE_HUB_ROUTER", "http://wpk-serv-07.mechse.illinois.edu:3456")
SYSTEM = ("You are an expert mechanical/CAD engineer. You read multi-view engineering drawings "
          "(orthographic views, dimensions, diameter/radius callouts, hole leaders) and reconstruct the part "
          "as a complete, runnable build123d Python script.\n\nRequirements for your answer:\n"
          "- Interpret every dimension and annotation in the drawing.\n"
          "- Output a single self-contained ```python code block.\n"
          "- The script must import everything it needs and export the final solid with "
          "`export_step(part, \"output.step\")`.\n"
          "- Use named variables for the key dimensions so the model is parametric.")
USER = "Reproduce the geometry as accurately as possible from the drawing."


def hub_key():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    for f in (os.path.expanduser("~/.claude-hub/my.key"), "/srv/scratch/claude-hub/lab.key"):
        if os.path.isfile(f):
            return open(f).read().strip()
    return "not-needed"


def ask(png, model, max_tokens=6000, timeout=600):
    img = base64.b64encode(open(png, "rb").read()).decode()
    body = {"model": model, "max_tokens": max_tokens, "system": SYSTEM,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
                {"type": "text", "text": USER}]}]}
    req = urllib.request.Request(f"{ROUTER}/v1/messages", data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json", "x-api-key": hub_key(),
                                          "anthropic-version": "2023-06-01", "x-hub-user": os.environ.get("USER", "bimrose2")})
    t = time.time()
    r = json.load(urllib.request.urlopen(req, timeout=timeout))
    txt = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
    return txt, r.get("usage"), r.get("stop_reason"), time.time() - t


if __name__ == "__main__":
    png = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "claude-moonshotai/Kimi-K3[1m]"
    try:
        txt, usage, stop, dt = ask(png, model)
        print(f"ok in {dt:.0f}s; usage={usage}; stop={stop}; chars={len(txt)}; has_code={'```python' in txt}")
        print(txt[:1500])
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode()[:600])
    except Exception as e:  # noqa: BLE001
        print("ERROR", repr(e)[:400])
