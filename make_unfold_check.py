# Consistency check for the 90-atom supercell: run the 30-atom relaxed neutral cell with exactly the
# k-points that the supercell's 2x1x2 mesh unfolds to (4 supercell k-points x 3 = 12). Then
# 3 x E(this run) should equal E(scf_pristine_neutral_sc.out) to within a few meV.
import re, itertools
import numpy as np
prim_in = open("relax_pristine_neutral.in").read()
sc_in = open("scf_pristine_neutral_sc.in").read()
getcell = lambda s: np.array([[float(x) for x in l.split()] for l in s.split("CELL_PARAMETERS angstrom\n")[1].strip().splitlines()[:3]])
P, Sc = getcell(prim_in), getcell(sc_in)
alat = np.linalg.norm(P[0]); assert abs(alat - np.linalg.norm(Sc[0])) < 1e-6
# reciprocal vectors in units of 2pi/alat (rows)
recip = lambda L: alat * np.linalg.inv(L).T
bP, bS = recip(P), recip(Sc)
# supercell k-points as printed by QE (cart, 2pi/alat)
out = open("scf_pristine_neutral_sc.out", errors="ignore").read()
blk = out.split("number of k points=")[1].split("cryst. coord.")[0]
ksc = [np.array([float(x) for x in m]) for m in re.findall(r"k\(\s*\d+\) = \(\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\), wk", blk)]
assert len(ksc) == 4, len(ksc)
in_prim = lambda G: np.allclose(np.round(G @ P.T / alat), G @ P.T / alat, atol=1e-6)   # G.a_i/(2pi) integer?
reps = []
for ijk in itertools.product(range(-3, 4), repeat=3):
    G = np.array(ijk) @ bS
    if not any(in_prim(G - R) for R in reps):
        reps.append(G)
assert len(reps) == 3, len(reps)
ks = [k + G for k in ksc for G in reps]
s = prim_in
s = re.sub(r"calculation = '.*?'", "calculation = 'scf'", s)
s = re.sub(r"prefix = '.*?'", "prefix = 'pristine_neutral_unfold'", s)
s = re.sub(r"\s*ion_dynamics = \"bfgs\",", "", s)
pout = open("relax_pristine_neutral.out", errors="ignore").read()
fb = pout[pout.rfind("Begin final coordinates"):pout.rfind("End final coordinates")]
atoms = [l.split() for l in fb.splitlines() if re.match(r"\s*(Ti|Nb|O)\s", l)]
assert len(atoms) == 30
s = re.sub(r"ATOMIC_POSITIONS crystal\n.*?(?=K_POINTS)", "ATOMIC_POSITIONS crystal\n" + "".join(f"  {a[0]} {a[1]} {a[2]} {a[3]}\n" for a in atoms), s, flags=re.S)
s = re.sub(r"K_POINTS automatic\n.*?\n", "K_POINTS tpiba\n%d\n" % len(ks) + "".join(f"  {k[0]:.10f} {k[1]:.10f} {k[2]:.10f} 1.0\n" for k in ks), s, flags=re.S)
open("scf_pristine_neutral_unfold.in", "w").write(s)
print("wrote scf_pristine_neutral_unfold.in with", len(ks), "k-points")
