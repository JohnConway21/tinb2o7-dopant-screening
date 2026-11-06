import re, sys

relax_out, atom_no, dopant, new_in, new_prefix = sys.argv[1:6]
atom_no = int(atom_no)
PP = {"Ta": (180.9479, "5d", 3.1, "Ta.pbe-spn-kjpaw_psl.1.0.0.UPF")}
mass, orb, U, pp = PP[dopant]

text = open(relax_out).read()
m = re.search(r"Begin final coordinates.*?ATOMIC_POSITIONS \(crystal\)\n(.*?)End final coordinates", text, re.S)
if not m:
    sys.exit("No final coordinates found; did the relaxation converge?")
final = [l.split() for l in m.group(1).strip().split("\n") if l.strip()]
if len(final) != 30:
    sys.exit(f"Expected 30 atoms, found {len(final)}")
if final[atom_no - 1][0] != "Nb":
    sys.exit(f"Atom {atom_no} is {final[atom_no-1][0]}, not Nb")
final[atom_no - 1][0] = dopant

inp = open("scf_electron.in").read()
block = "ATOMIC_POSITIONS crystal\n" + "\n".join("  " + " ".join(l) for l in final) + "\n"
old = re.search(r"ATOMIC_POSITIONS crystal\n(.*?)K_POINTS", inp, re.S)
inp = inp.replace(old.group(0), block + "K_POINTS")
inp = re.sub(r"\n\s*tot_charge = -1,", "", inp)
inp = inp.replace("calculation = 'scf',", "calculation = 'relax',")
inp = re.sub(r"prefix = '.*?'", f"prefix = '{new_prefix}'", inp)
inp = inp.replace("ntyp = 3,", "ntyp = 4,")
inp = inp.replace("ATOMIC_SPECIES\n", f"ATOMIC_SPECIES\n  {dopant}  {mass} {pp}\n")
inp = inp.replace("U Nb-4d 5.2\n", f"U Nb-4d 5.2\nU {dopant}-{orb} {U}\n")
inp = inp.replace("&IONS\n/", '&IONS\n  ion_dynamics = "bfgs",\n/')
open(new_in, "w").write(inp)
print(f"Wrote {new_in}: atom {atom_no} -> {dopant}")
