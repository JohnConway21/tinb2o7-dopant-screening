# Build a 90-atom supercell of the relaxed neutral pristine cell, tripled along the short
# lattice translation a-b (3.83 A -> 11.50 A). New lattice: A1 = a, A2 = 3(b-a), A3 = c.
# Writes scf_pristine_neutral_sc.in for a single neutral SCF timing benchmark.
import re
import numpy as np
inp = open("relax_pristine_neutral.in").read()
cell = np.array([[float(x) for x in l.split()] for l in inp.split("CELL_PARAMETERS angstrom\n")[1].strip().splitlines()[:3]])
out = open("relax_pristine_neutral.out", errors="ignore").read()
blk = out[out.rfind("Begin final coordinates"):out.rfind("End final coordinates")]
at = [l.split() for l in blk.splitlines() if re.match(r"\s*(Ti|Nb|O)\s", l)]
assert len(at) == 30
M = np.array([[1, 0, 0], [-3, 3, 0], [0, 0, 1]])      # rows: new vectors in old basis
new = M @ cell
assert abs(np.linalg.det(M) - 3) < 1e-9   # right-handed
inv = np.linalg.inv(new)
atoms = []
for n in range(3):                                      # images along a-b
    for a in at:
        r = (np.array([float(x) for x in a[1:4]]) + n * np.array([1, -1, 0])) @ cell
        fr = (r @ inv) % 1.0
        atoms.append((a[0], fr))
# check no duplicates and correct count
fr = np.array([x[1] for x in atoms])
dmin = min(np.linalg.norm(((fr[i] - fr[j] + 0.5) % 1 - 0.5) @ new) for i in range(90) for j in range(i))
assert dmin > 1.5, dmin
s = inp
s = re.sub(r"calculation = '.*?'", "calculation = 'scf'", s)
s = re.sub(r"prefix = '.*?'", "prefix = 'pristine_neutral_sc'", s)
s = s.replace("nat = 30,", "nat = 90,")
s = re.sub(r"\s*ion_dynamics = \"bfgs\",", "", s)
s = re.sub(r"ATOMIC_POSITIONS crystal\n.*?(?=K_POINTS)",
           "ATOMIC_POSITIONS crystal\n" + "".join(f"  {e} {x:.10f} {y:.10f} {z:.10f}\n" for e, (x, y, z) in atoms), s, flags=re.S)
s = re.sub(r"K_POINTS automatic\n.*?\n", "K_POINTS automatic\n  2 1 2 0 0 0\n", s, flags=re.S)
s = re.sub(r"CELL_PARAMETERS angstrom\n(.*\n){3}", "CELL_PARAMETERS angstrom\n" + "".join("  " + " ".join(f"{x:.6f}" for x in v) + "\n" for v in new), s)
open("scf_pristine_neutral_sc.in", "w").write(s)
print("lengths (A):", [round(np.linalg.norm(v), 3) for v in new], "min interatomic (A):", round(dmin, 3))
