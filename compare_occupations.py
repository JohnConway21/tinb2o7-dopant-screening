from pymatgen.core import Structure
import re

pristine = Structure.from_file("TiNb2O7.cif")
doped = Structure.from_file("doped_structures/TiNb2O7_Mo_at_M1.cif")

def get_occupations(filename):
    with open(filename) as f:
        text = f.read()
    pattern = r"ATOM\s+(\d+).*?Tr\[ns\(\s*\d+\)\]\s*=\s*([\d.]+)"
    matches = re.findall(pattern, text, re.DOTALL)
    occ = {}
    for atom_num, val in matches:
        occ[int(atom_num)] = float(val)  # last occurrence wins (final iteration)
    return occ

pristine_occ = get_occupations("scf_electron.out")
doped_occ = get_occupations("scf_Mo_electron.out")

print("Pristine structure order:")
for i, site in enumerate(pristine):
    print(f"  QE atom {i+1}: {site.specie.symbol} at {site.frac_coords}")

print("\nDoped structure order:")
for i, site in enumerate(doped):
    print(f"  QE atom {i+1}: {site.specie.symbol} at {site.frac_coords}")
