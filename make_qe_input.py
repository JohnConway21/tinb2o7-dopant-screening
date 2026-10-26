from pymatgen.core import Structure
from pymatgen.io.pwscf import PWInput

structure = Structure.from_file("TiNb2O7.cif")

pseudo = {
    "Ti": "Ti.pbe-spn-kjpaw_psl.1.0.0.UPF",
    "Nb": "Nb.pbe-spn-kjpaw_psl.1.0.0.UPF",
    "O": "O.pbe-n-kjpaw_psl.1.0.0.UPF",
}

control = {
    "calculation": "scf",
    "prefix": "TiNb2O7_pristine",
    "pseudo_dir": "./pseudo",
    "outdir": "./tmp",
    "verbosity": "high",
}

system = {
    "ecutwfc": 60,
    "ecutrho": 240,
    "occupations": "smearing",
    "smearing": "gaussian",
    "degauss": 0.01,
    "lda_plus_u": True,
    "Hubbard_U(1)": 5.2,  # Ti
    "Hubbard_U(2)": 5.2,  # Nb
}

electrons = {
    "conv_thr": 1.0e-8,
    "mixing_beta": 0.3,
}

pw_input = PWInput(
    structure=structure,
    pseudo=pseudo,
    control=control,
    system=system,
    electrons=electrons,
    kpoints_grid=(2, 2, 2),
)

pw_input.write_file("scf_pristine.in")
print("Wrote scf_pristine.in")
