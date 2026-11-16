# Build relax_pristine_e_sc_seed9.in: charged (-1) spin-polarized relaxation of the 90-atom pristine
# supercell, starting from a localized guess on supercell atom 9 (first copy of 30-atom site 9):
#  - atom 9 relabeled Nb9 (same pseudopotential, same U) so it can carry the starting moment
#  - its O neighbours (< 2.5 A) pushed outward by 0.1 A along the Nb9-O bond
#  - nspin = 2, tot_magnetization = 1, starting_magnetization 0.5 on Nb9 only
# Everything else as scf_pristine_neutral_sc.in (60/240 Ry, smearing 0.01 Ry, 2x1x2 mesh, same U).
import re, itertools
import numpy as np
SITE, SHIFT, RCUT = 9, 0.10, 2.5
s = open("scf_pristine_neutral_sc.in").read()
cell = np.array([[float(x) for x in l.split()] for l in s.split("CELL_PARAMETERS angstrom\n")[1].strip().splitlines()[:3]])
at = [l.split() for l in s.split("ATOMIC_POSITIONS crystal\n")[1].split("K_POINTS")[0].strip().splitlines()]
assert len(at) == 90 and at[SITE - 1][0] == "Nb"
f = np.array([[float(x) for x in a[1:4]] for a in at])
c0 = f[SITE - 1] @ cell
moved = []
for j, a in enumerate(at):
    if a[0] != "O": continue
    imgs = [(np.linalg.norm((f[j] + np.array(t)) @ cell - c0), np.array(t)) for t in itertools.product([-1, 0, 1], repeat=3)]
    near = [(d, t) for d, t in imgs if d < RCUT]
    if not near: continue
    assert len(near) == 1, f"O{j+1} bonds site {SITE} through {len(near)} images"
    d, t = near[0]
    r = (f[j] + t) @ cell
    f[j] = (r + SHIFT * (r - c0) / d) @ np.linalg.inv(cell) - t
    moved.append((j + 1, round(d, 3), round(d + SHIFT, 3)))
assert len(moved) == 6, moved
at[SITE - 1][0] = "Nb9"
s = re.sub(r"ATOMIC_POSITIONS crystal\n.*?(?=K_POINTS)", "ATOMIC_POSITIONS crystal\n" + "".join(f"  {a[0]} {x:.10f} {y:.10f} {z:.10f}\n" for a, (x, y, z) in zip(at, f)), s, flags=re.S)
s = s.replace("calculation = 'scf'", "calculation = 'relax'")
s = s.replace("prefix = 'pristine_neutral_sc'", "prefix = 'pristine_e_sc_seed9'")
s = s.replace("ntyp = 3,", "ntyp = 4,\n  nspin = 2,\n  starting_magnetization(4) = 0.5,\n  tot_magnetization = 1,\n  tot_charge = -1,")
s = s.replace("  Ti  47.8670 Ti.pbe-spn-kjpaw_psl.1.0.0.UPF\n", "  Ti  47.8670 Ti.pbe-spn-kjpaw_psl.1.0.0.UPF\n  Nb9 92.9064 Nb.pbe-spn-kjpaw_psl.1.0.0.UPF\n")
s = s.replace("U Nb-4d 5.2\n", "U Nb-4d 5.2\nU Nb9-4d 5.2\n")
s = re.sub(r"&IONS\n", "&IONS\n  ion_dynamics = \"bfgs\",\n", s)
open("relax_pristine_e_sc_seed9.in", "w").write(s)
print("O moved (atom, old, new Nb9-O distance in A):", moved)
