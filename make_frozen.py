import re

inp = open("relax_Ta9_neutral.in").read()
atoms = [l for l in open("ta9_final_coords.txt") if re.match(r"\s*(Ti|Nb|Ta|O)\s", l)]
assert len(atoms) == 30, f"found {len(atoms)} atoms"

block = "ATOMIC_POSITIONS crystal\n" + "".join("  " + " ".join(a.split()) + "\n" for a in atoms)
inp = re.sub(r"ATOMIC_POSITIONS crystal\n.*?(?=K_POINTS)", block, inp, flags=re.S)
inp = inp.replace("calculation = 'relax',", "calculation = 'scf',")
inp = re.sub(r'\s*ion_dynamics = "bfgs",', "", inp)
inp = re.sub(r"prefix = '.*?'", "prefix = 'Ta9_frozen_electron'", inp)
inp = inp.replace("&SYSTEM\n", "&SYSTEM\n  tot_charge = -1,\n", 1)

open("frozen_Ta9_electron.in", "w").write(inp)
print("Wrote frozen_Ta9_electron.in")
