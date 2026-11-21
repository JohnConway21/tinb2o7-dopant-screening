# Build the Ta-doped 90-atom supercell inputs with EXACTLY the pristine polaron protocol.
# One Nb -> Ta per supercell (90 atoms). Two placements:
#   Ta9: supercell atom 9 (the site where the pristine polaron forms) becomes Ta.
#   Ta5: supercell atom 5 (the site-5 copy nearest atom 9, 3.89 A away) becomes Ta.
# For each placement, two inputs:
#   scf_TaX_e_sc_spin.in       delocalized reference (copy of scf_pristine_e_sc_spin.in, the gate),
#                              starting_magnetization 0.1 on every transition-metal species, forces printed
#   relax_TaX_e_sc_seed9.in    seeded relaxation (copy of relax_pristine_e_sc_seed9.in: same 0.1 A push of
#                              atom 9's six O, starting_magnetization 0.5 on atom 9's species)
# Same cutoffs, smearing, k-mesh, U values (Ta-5d 3.1 eV as in all earlier Ta runs), pseudopotentials.
# Relax stop rule (approved by Dev 2026-11-21, matches where the pristine run was stopped):
#   forc_conv_thr = 3.0d-3 Ry/Bohr, etot_conv_thr = 3.0d-4 Ry. Pristine stopped at max force 0.0026, dE 1.2e-4.
import re
TA_SPEC = "  Ta  180.9479 Ta.pbe-spn-kjpaw_psl.1.0.0.UPF\n"
def sub_atom(s, idx, new):
    head, rest = s.split("ATOMIC_POSITIONS crystal\n"); pos, tail = rest.split("K_POINTS", 1)
    lines = pos.strip("\n").split("\n"); assert len(lines) == 90
    p = lines[idx - 1].split(); old = p[0]; p[0] = new
    lines[idx - 1] = "  " + " ".join(p)
    return head + "ATOMIC_POSITIONS crystal\n" + "\n".join(lines) + "\nK_POINTS" + tail, old
STOP = "&IONS\n  ion_dynamics = \"bfgs\",\n/"
STOP_NEW = "&IONS\n  ion_dynamics = \"bfgs\",\n/"
for X, idx in (("Ta9", 9), ("Ta5", 5)):
    # reference
    s = open("scf_pristine_e_sc_spin.in").read()
    s, old = sub_atom(s, idx, "Ta"); assert old == "Nb"
    s = s.replace("prefix = 'pristine_e_sc_spin'", f"prefix = '{X}_e_sc_spin'")
    s = s.replace("verbosity = 'high',", "verbosity = 'high',\n  tprnfor = .true.,")
    s = s.replace("ntyp = 3,", "ntyp = 4,").replace("starting_magnetization(3) = 0.1,", "starting_magnetization(3) = 0.1,\n  starting_magnetization(4) = 0.1,")
    s = s.replace("  Ti  47.8670 Ti.pbe-spn-kjpaw_psl.1.0.0.UPF\n", "  Ti  47.8670 Ti.pbe-spn-kjpaw_psl.1.0.0.UPF\n" + TA_SPEC)
    s = s.replace("U Nb-4d 5.2\n", "U Nb-4d 5.2\nU Ta-5d 3.1\n")
    assert s.count("Ta") >= 4; open(f"scf_{X}_e_sc_spin.in", "w").write(s)
    # seeded relax
    s = open("relax_pristine_e_sc_seed9.in").read()
    s = s.replace("prefix = 'pristine_e_sc_seed9'", f"prefix = '{X}_e_sc_seed9'")
    s = s.replace("calculation = 'relax',", "calculation = 'relax',\n  forc_conv_thr = 3.0d-3,\n  etot_conv_thr = 3.0d-4,")
    if X == "Ta9":   # atom 9 itself becomes Ta: species 4 (carrying the 0.5 seed moment) becomes Ta
        s, old = sub_atom(s, 9, "Ta"); assert old == "Nb9"
        s = s.replace("  Nb9 92.9064 Nb.pbe-spn-kjpaw_psl.1.0.0.UPF\n", TA_SPEC).replace("U Nb9-4d 5.2\n", "U Ta-5d 3.1\n")
    else:            # atom 5 becomes Ta (new species 5); atom 9 stays the seeded Nb9
        s, old = sub_atom(s, 5, "Ta"); assert old == "Nb"
        s = s.replace("ntyp = 4,", "ntyp = 5,")
        s = s.replace("  Nb9 92.9064 Nb.pbe-spn-kjpaw_psl.1.0.0.UPF\n", "  Nb9 92.9064 Nb.pbe-spn-kjpaw_psl.1.0.0.UPF\n" + TA_SPEC)
        s = s.replace("U Nb9-4d 5.2\n", "U Nb9-4d 5.2\nU Ta-5d 3.1\n")
    assert "Nb9" not in s.split("ATOMIC_POSITIONS")[1] or X == "Ta5"
    open(f"relax_{X}_e_sc_seed9.in", "w").write(s)
    print("wrote", f"scf_{X}_e_sc_spin.in", f"relax_{X}_e_sc_seed9.in")
