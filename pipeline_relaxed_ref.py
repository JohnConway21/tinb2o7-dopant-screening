# Corrected polaron protocol (2026-11-22). Problem found: the 90-atom starting geometry (30-atom neutral
# relaxed cell tiled 3x, relaxed with the old 2x2x2 mesh) is NOT at equilibrium with the supercell settings:
# forces up to 0.05 Ry/Bohr on atoms far from any defect (identical in all 3 copies), and in the pristine
# seeded relaxation atoms 6-9 A from the polaron moved up to 0.12 A, more than the polaron site itself.
# So E(deloc at unrelaxed geometry) - E(loc relaxed) also counts relaxation of the starting structure.
#
# Fix, same definition (frozen = charged at NEUTRAL EQUILIBRIUM geometry, minus charged relaxed), same
# cutoffs/U/k-mesh/smearing/pseudopotentials. Steps, one pw.x at a time, each checked before the next:
#   1 relax_pristine_neutral_sc      neutral, nspin=1, relax atoms in the supercell (QE default thresholds)
#   2 scf_pristine_e_sc_spin_rlx     charged delocalized reference at geometry 1 (copy of the gate input)
#   3 relax_Ta9_neutral_sc           geometry 1 with Ta on atom 9, neutral relax
#   4 scf_Ta9_e_sc_spin_rlx          charged delocalized reference at geometry 3
#   5 relax_Ta9_e_sc_seed9_rlx       seeded polaron relax. Changed 2026-11-24 to save ~2 days per site:
#                                    starts from the converged PRISTINE polaron geometry with Ta swapped in
#                                    (pristine_polaron_final_positions.txt); same settings and stop rule.
#   6-8 same for Ta5 (Ta on atom 5)
# The pristine localized endpoint (relax_pristine_e_sc_seed9_r3, E = -10293.77969580 Ry) is reused.
# Usage: python pipeline_relaxed_ref.py   (normally via run_pipeline_launchd.sh). Log: pipeline.log
import re, itertools, subprocess, os, sys, datetime
import numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))
LOG = "pipeline.log"
TA_SPEC = "  Ta  180.9479 Ta.pbe-spn-kjpaw_psl.1.0.0.UPF\n"
def log(m):
    open(LOG, "a").write(f"{datetime.datetime.now():%a %b %d %H:%M:%S} {m}\n")

def split_pos(s):
    head, rest = s.split("ATOMIC_POSITIONS crystal\n"); pos, tail = rest.split("K_POINTS", 1)
    at = [l.split() for l in pos.strip("\n").split("\n")]; assert len(at) == 90
    return head, at, "K_POINTS" + tail
def join_pos(head, labels, f, tail):
    return head + "ATOMIC_POSITIONS crystal\n" + "".join(f"  {a} {x:.10f} {y:.10f} {z:.10f}\n" for a, (x, y, z) in zip(labels, f)) + tail
def cell_of(s):
    return np.array([[float(x) for x in l.split()] for l in s.split("CELL_PARAMETERS angstrom\n")[1].strip().splitlines()[:3]])

def cur(name):
    # latest restart of a step: NAME, NAME_r2, NAME_r3 ... (made by make_restart_from_last.py after a power loss)
    k = 2
    while os.path.exists(f"{name}_r{k}.in"): k += 1
    return name if k == 2 else f"{name}_r{k-1}"

def final_positions(name):
    name = cur(name)
    t = open(name + ".out", errors="ignore").read()
    assert "bfgs converged" in t, name
    blk = t.split("Begin final coordinates")[1].split("End final coordinates")[0]
    lines = blk.split("ATOMIC_POSITIONS (crystal)\n")[1].strip().splitlines()[:90]
    return [l.split()[0] for l in lines], np.array([[float(x) for x in l.split()[1:4]] for l in lines])

def with_positions(template, f, check_species=None):
    # keep the template's labels, replace coordinates
    s = open(template).read(); head, at, tail = split_pos(s)
    return join_pos(head, [a[0] for a in at], f, tail)

def seed_push(s, f, site=9, shift=0.10, rcut=2.5):
    cell = cell_of(s); f = f.copy(); c0 = f[site - 1] @ cell; head, at, tail = split_pos(s); moved = 0
    for j, a in enumerate(at):
        if a[0] != "O": continue
        near = [(np.linalg.norm((f[j] + np.array(t)) @ cell - c0), np.array(t)) for t in itertools.product([-1, 0, 1], repeat=3)]
        near = [x for x in near if x[0] < rcut]
        if not near: continue
        assert len(near) == 1
        d, t = near[0]; r = (f[j] + t) @ cell
        f[j] = (r + shift * (r - c0) / d) @ np.linalg.inv(cell) - t; moved += 1
    assert moved == 6, moved
    return f

def neutral_relax_input(f, prefix, ta_atom=None):
    s = open("scf_pristine_neutral_sc.in").read()
    s = s.replace("calculation = 'scf'", "calculation = 'relax'").replace("prefix = 'pristine_neutral_sc'", f"prefix = '{prefix}'")
    s = s.replace("&IONS\n/", "&IONS\n  ion_dynamics = \"bfgs\",\n/")
    head, at, tail = split_pos(s); labels = [a[0] for a in at]
    if ta_atom:
        assert labels[ta_atom - 1] == "Nb"; labels[ta_atom - 1] = "Ta"
        head = head.replace("ntyp = 3,", "ntyp = 4,").replace("  Ti  47.8670 Ti.pbe-spn-kjpaw_psl.1.0.0.UPF\n", "  Ti  47.8670 Ti.pbe-spn-kjpaw_psl.1.0.0.UPF\n" + TA_SPEC)
        head = head.replace("U Nb-4d 5.2\n", "U Nb-4d 5.2\nU Ta-5d 3.1\n"); assert "Ta-5d" in head and "ntyp = 4" in head
    return join_pos(head, labels, f, tail)

def ok(name):
    p = name + ".out"
    if not os.path.exists(p): return None
    # NAME.accepted: SCF stalled with the energy settled; Dev approved using its last energy (2026-11-27).
    if os.path.exists(name + ".accepted"): return True
    t = open(p, errors="ignore").read()
    if "JOB DONE" not in t: return False
    return ("bfgs converged" in t) if "calculation = 'relax'" in open(name + ".in").read() else ("convergence has been achieved" in t)

def run(name, build):
    if not os.path.exists(name + ".in"):
        open(name + ".in", "w").write(build()); log(f"built {name}.in")
    name = cur(name)
    st = ok(name)
    if st: log(f"skip {name} (done)"); return
    if st is False: log(f"STOP: {name}.out exists unfinished/failed; restart by hand (make_restart_from_last.py {name} <name>_rK)"); sys.exit(1)
    log(f"start {name}")
    with open(name + ".in") as i, open(name + ".out", "w") as o:
        subprocess.run(["mpirun", "-np", "3", "pw.x"], stdin=i, stdout=o, stderr=subprocess.STDOUT)
    if not ok(name): log(f"STOP: {name} failed its check"); sys.exit(1)
    e = [l for l in open(name + ".out", errors="ignore") if l.startswith("!")][-1].strip()
    log(f"done {name}: {e}")

if __name__ == "__main__":
    f0 = split_pos(open("scf_pristine_neutral_sc.in").read())[1]
    f0 = np.array([[float(x) for x in a[1:4]] for a in f0])
    run("relax_pristine_neutral_sc", lambda: neutral_relax_input(f0, "pristine_neutral_sc_rlx"))
    fP = final_positions("relax_pristine_neutral_sc")[1]
    def ref(template, f, prefix_old, prefix_new):
        s = with_positions(template, f).replace(f"prefix = '{prefix_old}'", f"prefix = '{prefix_new}'")
        if "tprnfor" not in s: s = s.replace("verbosity = 'high',", "verbosity = 'high',\n  tprnfor = .true.,")
        assert prefix_new in s; return s
    run("scf_pristine_e_sc_spin_rlx", lambda: ref("scf_pristine_e_sc_spin.in", fP, "pristine_e_sc_spin", "pristine_e_sc_spin_rlx"))
    for X, idx in (("Ta9", 9), ("Ta5", 5)):
        run(f"relax_{X}_neutral_sc", lambda: neutral_relax_input(fP, f"{X}_neutral_sc_rlx", ta_atom=idx))
        fX = final_positions(f"relax_{X}_neutral_sc")[1]
        run(f"scf_{X}_e_sc_spin_rlx", lambda: ref(f"scf_{X}_e_sc_spin.in", fX, f"{X}_e_sc_spin", f"{X}_e_sc_spin_rlx"))
        def seeded():
            L = open("pristine_polaron_final_positions.txt").read().splitlines()[1:91]
            s = with_positions(f"relax_{X}_e_sc_seed9.in", np.array([[float(x) for x in l.split()[1:4]] for l in L]))
            s = s.replace(f"prefix = '{X}_e_sc_seed9'", f"prefix = '{X}_e_sc_seed9_rlx'"); assert "seed9_rlx" in s; return s
        run(f"relax_{X}_e_sc_seed9_rlx", seeded)
    log("PIPELINE COMPLETE")
