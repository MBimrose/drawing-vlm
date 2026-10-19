"""In-dist pipeline (2026-10-14): after the full S1 starts (starts_rl2s60_r{1,2,3}.json from the merged consistency file),
check that they equal the part-A/B starts on those keys, and write blocks rl2s60_c{c}.z.bNN (24 sorted keys) for the
remaining keys.   python make_z_blocks.py"""
import json, os
P = os.path.dirname(os.path.abspath(__file__))
for c in (1, 2, 3):
    full = json.load(open(f"{P}/starts_rl2s60_r{c}.json"))
    a = {**json.load(open(f"{P}/partial/starts_rl2s60_a_r{c}.json")), **json.load(open(f"{P}/partial/starts_rl2s60_b_r{c}.json"))}
    assert len(full) == 1027 and all(full[k] == a[k] for k in a), f"part-A starts differ from full starts (c{c})"
    rest = sorted(k for k in full if k not in a)
    for i in range(0, len(rest), 24):
        f = f"{P}/blocks/rl2s60_c{c}.z.b{i // 24:02d}.json"; json.dump({k: full[k] for k in rest[i:i + 24]}, open(f + ".tmp", "w")); os.replace(f + ".tmp", f)
    print(f"c{c}: part-A starts identical on {len(a)} keys; {len(rest)} remaining keys -> {(len(rest) + 23) // 24} z blocks")
