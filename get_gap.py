import re

with open("scf_pristine.out") as f:
    text = f.read()

# Find all k-point blocks with bands and occupation numbers
blocks = re.findall(
    r"bands \(ev\):\n\n(.*?)\n\n     occupation numbers\s*\n(.*?)\n\n",
    text, re.DOTALL
)

vbm = -1e9
cbm = 1e9

for bands_str, occ_str in blocks:
    bands = [float(x) for x in bands_str.split()]
    occs = [float(x) for x in occ_str.split()]
    for b, o in zip(bands, occs):
        if o > 0.5:
            vbm = max(vbm, b)
        else:
            cbm = min(cbm, b)

print(f"Valence band maximum (VBM): {vbm:.4f} eV")
print(f"Conduction band minimum (CBM): {cbm:.4f} eV")
print(f"Band gap: {cbm - vbm:.4f} eV")
