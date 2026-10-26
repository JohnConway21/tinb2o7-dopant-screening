from pymatgen.core import Structure
import os

structure = Structure.from_file("TiNb2O7.cif")

M1_INDEX = 6

dopants = ["Mo", "W", "Cr", "Ta", "V", "Zr"]

os.makedirs("doped_structures", exist_ok=True)

print(f"Original site {M1_INDEX}: {structure[M1_INDEX].specie.symbol} at {structure[M1_INDEX].frac_coords}")

for dopant in dopants:
    doped = structure.copy()
    doped.replace(M1_INDEX, dopant)
    filename = f"doped_structures/TiNb2O7_{dopant}_at_M1.cif"
    doped.to(filename=filename)
    print(f"Wrote {filename}")
