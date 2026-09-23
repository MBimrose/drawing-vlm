"""Validate one STEP for the family corpus; prints one JSON line.
    python validate_step.py <step>"""
import json, sys
try:
    from build123d import import_step
    s = import_step(sys.argv[1])
    sol = s.solids(); bb = s.bounding_box()
    out = {"solids": len(sol), "faces": len(s.faces()), "edges": len(s.edges()), "volume": float(sum(x.volume for x in sol)),
           "bbox": [bb.size.X, bb.size.Y, bb.size.Z], "valid": bool(s.is_valid() if callable(s.is_valid) else s.is_valid)}
except Exception as e:
    out = {"error": f"{type(e).__name__}: {e}"[:400]}
print(json.dumps(out))
