# NOT RUN: pushes apical O14 asymmetrically (it bonds Nb5 through two images along the 3.83 A axis). See RESULTS.md.
# Build relax_pristine_e_spin_dist.in: neutral relaxed pristine geometry, O neighbours of atom 5
# pushed outward by 0.1 A along the Nb5-O bond; electronic settings from relax_pristine_e_spin_m1.in.
import re, itertools
import numpy as np
SHIFT, RCUT = 0.10, 2.5
inp = open("relax_pristine_e_spin_m1.in").read()
cell = np.array([[float(x) for x in l.split()] for l in inp.split("CELL_PARAMETERS angstrom\n")[1].strip().splitlines()[:3]])
out = open("relax_pristine_neutral.out", errors="ignore").read()
blk = out[out.rfind("Begin final coordinates"):out.rfind("End final coordinates")]
at = [l.split() for l in blk.splitlines() if re.match(r"\s*(Ti|Nb|O)\s", l)]
assert len(at) == 30 and at[4][0] == "Nb"
at[4][0] = "Nb5"
f = np.array([[float(x) for x in a[1:4]] for a in at])
inv = np.linalg.inv(cell)
c5 = f[4] @ cell
moved = []
for j, a in enumerate(at):
    if a[0] != "O": continue
    best = min(((f[j] + np.array(s)) @ cell for s in itertools.product([-1, 0, 1], repeat=3)), key=lambda r: np.linalg.norm(r - c5))
    d = np.linalg.norm(best - c5)
    if d < RCUT:
        new = best + SHIFT * (best - c5) / d
        f[j] = new @ inv - (best @ inv - f[j])   # keep original periodic image
        moved.append((j + 1, round(d, 3), round(np.linalg.norm(new - c5), 3)))
pos = "ATOMIC_POSITIONS crystal\n" + "".join(f"  {a[0]} {x:.10f} {y:.10f} {z:.10f}\n" for a, (x, y, z) in zip(at, f))
inp = re.sub(r"ATOMIC_POSITIONS crystal\n.*?(?=K_POINTS)", pos, inp, flags=re.S)
inp = inp.replace("prefix = 'pristine_e_spin_m1'", "prefix = 'pristine_e_spin_dist'")
open("relax_pristine_e_spin_dist.in", "w").write(inp)
print("O atoms moved (atom, old Nb5-O, new Nb5-O in A):")
for m in moved: print(" ", m)
