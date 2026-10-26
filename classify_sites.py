from pymatgen.core import Structure
from pymatgen.analysis.local_env import CrystalNN

structure = Structure.from_file("TiNb2O7.cif")
cnn = CrystalNN()

metal_indices = [i for i, site in enumerate(structure) if site.specie.symbol in ("Nb", "Ti")]

print(f"Found {len(metal_indices)} metal sites (Nb/Ti)\n")

metal_oxygens = {}
for i in metal_indices:
    neighbors = cnn.get_nn_info(structure, i)
    o_indices = set(n["site_index"] for n in neighbors if structure[n["site_index"]].specie.symbol == "O")
    metal_oxygens[i] = o_indices

for i in metal_indices:
    max_shared = 0
    for j in metal_indices:
        if i == j:
            continue
        shared = len(metal_oxygens[i] & metal_oxygens[j])
        max_shared = max(max_shared, shared)

    if max_shared >= 2:
        site_type = "M5 (edge-sharing, boundary)"
    elif max_shared == 1:
        site_type = "M1 (corner-sharing, interior)"
    else:
        site_type = "ISOLATED (unexpected)"

    symbol = structure[i].specie.symbol
    print(f"Site {i} ({symbol}): max shared oxygens with any neighbor = {max_shared} -> {site_type}")
