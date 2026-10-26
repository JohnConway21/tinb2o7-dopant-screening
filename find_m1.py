from pymatgen.core import Structure
import numpy as np

structure = Structure.from_file("TiNb2O7.cif")

ti_indices = [i for i, site in enumerate(structure) if site.specie.symbol == "Ti"]
nb_indices = [i for i, site in enumerate(structure) if site.specie.symbol == "Nb"]

print("Distance from each Nb site to its NEAREST Ti neighbor (periodic boundary aware):\n")

results = []
for nb_i in nb_indices:
    min_dist = min(structure.get_distance(nb_i, ti_i) for ti_i in ti_indices)
    results.append((nb_i, min_dist))
    print(f"Nb site {nb_i}: nearest Ti is {min_dist:.3f} Å away")

results.sort(key=lambda x: -x[1])
print(f"\nLikely M1 candidate (farthest Nb from any Ti): Nb site {results[0][0]}")
