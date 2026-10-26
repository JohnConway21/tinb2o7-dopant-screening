from pymatgen.core import Structure

structure = Structure.from_file("doped_structures/TiNb2O7_Mo_at_M1.cif")

species_block = """ATOMIC_SPECIES
  Mo  95.9500 Mo.pbe-spn-kjpaw_psl.1.0.0.UPF
  Nb  92.9064 Nb.pbe-spn-kjpaw_psl.1.0.0.UPF
  O   15.9994 O.pbe-n-kjpaw_psl.1.0.0.UPF
  Ti  47.8670 Ti.pbe-spn-kjpaw_psl.1.0.0.UPF
"""

hubbard_block = """HUBBARD (ortho-atomic)
U Ti-3d 5.2
U Nb-4d 5.2
U Mo-4d 4.38
"""

positions_lines = ["ATOMIC_POSITIONS crystal"]
for site in structure:
    positions_lines.append(f"  {site.specie.symbol} {site.frac_coords[0]:.6f} {site.frac_coords[1]:.6f} {site.frac_coords[2]:.6f}")
positions_block = "\n".join(positions_lines) + "\n"

cell = structure.lattice.matrix
cell_block = "CELL_PARAMETERS angstrom\n"
for row in cell:
    cell_block += f"  {row[0]:.6f} {row[1]:.6f} {row[2]:.6f}\n"

kpoints_block = "K_POINTS automatic\n  2 2 2 0 0 0\n"

# count species present
symbols = set(site.specie.symbol for site in structure)
ntyp = len(symbols)

input_text = f"""&CONTROL
  calculation = 'scf',
  prefix = 'TiNb2O7_Mo_electron',
  pseudo_dir = './pseudo',
  outdir = './tmp',
  verbosity = 'high',
/
&SYSTEM
  ibrav = 0,
  nat = {len(structure)},
  ntyp = {ntyp},
  ecutwfc = 60,
  ecutrho = 240,
  occupations = 'smearing',
  smearing = 'gaussian',
  degauss = 0.01,
  tot_charge = -1,
/
&ELECTRONS
  conv_thr = 1.0d-8,
  mixing_beta = 0.3,
/
&IONS
/
&CELL
/
{species_block}{hubbard_block}{positions_block}{kpoints_block}{cell_block}"""

with open("scf_Mo_electron.in", "w") as f:
    f.write(input_text)

print("Wrote scf_Mo_electron.in")
print(f"Species present: {symbols}")
