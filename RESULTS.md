
## Pseudopotentials
- Source: Quantum ESPRESSO pseudopotential library (pslibrary 1.0.0, PBE, PAW), https://pseudopotentials.quantum-espresso.org
- Not tracked in git (pseudo/*.UPF is gitignored). Download each file separately.
- Ta.pbe-spn-kjpaw_psl.1.0.0.UPF, MD5 70e26a4a8c1f0430003df9f0e8af0a92 (verified on both machines)

## 30-atom polaron values: NOT VALIDATED, not project results (decision by Dev, 2026-11-15)
Kept as a record only. Do not report these as trapping energies. Reasons:
1. The extra electron is delocalized over all nine metal sites (largest single-site d-occupation
   gain ~0.17 e; a small polaron would be ~1 e). See "Caveat found 2026-11-14" below.
2. The runs are not spin-polarized (no nspin = 2).
3. The 30-atom cell repeats every 3.83 A along a-b, so a localized electron would sit 3.83 A from
   its own images. See "Cell-size problem" below.
4. The 2x2x2 k-mesh is 0.80 eV off in total energy compared with 3x3x3. See "k-point convergence test" below.

### 30-atom values, not validated (total energies in Ry; E_frozen - E_relaxed, tot_charge = -1, 13.6057 eV/Ry)

| System | Neutral relax | Frozen electron | Relaxed electron | Polaron energy (eV) |
|---|---|---|---|---|
| Pristine | -3431.53114476 | -3430.84455676 | -3430.85150622 | 0.0946 |
| Ta9 | -3824.63158809 (10 BFGS steps) | -3823.94061440 (29 iter) | -3823.94748794 (20 BFGS steps) | 0.0935 |
| Ta5 | -3824.62518831 (8 BFGS steps) | -3823.93400701 (29 iter) | -3823.94064044 (12 BFGS steps) | 0.0903 |

- Neutral cell: Ta9 is 0.087 eV lower than Ta5 (stability result, not a trapping result).
- Ta5 frozen and relaxed runs: 241.00 electrons, convergence achieved, JOB DONE.
- A first attempt at the Ta5 relaxed run was killed mid-SCF (machine sleep, no QE error); its partial output is kept as relax_Ta5_electron.out.killed. The reported result is from the full rerun with identical input.
- Differences from pristine: Ta9 -1.0 meV, Ta5 -4.3 meV. No trapping conclusion has been drawn yet; whether these are outside numerical noise is still to be discussed.

## Caveat found 2026-11-14: extra electron is delocalized in all charged runs above

All charged runs above are non-spin-polarized (no nspin = 2). Comparing Hubbard d-occupations
(Tr[ns], final step) with the neutral runs, the extra electron spreads over all nine Ti/Nb/Ta sites:

| Run | Largest single-site gain | Site |
|---|---|---|
| Pristine relaxed electron | +0.165 | M5 (Nb) |
| Ta5 relaxed electron | +0.117 | Ti2 |

A small polaron would put roughly 0.8-1 electron on one site. So the 0.09 eV values above are the
lattice relaxation of a mostly delocalized electron, not small-polaron trapping energies, and the
pristine/Ta9/Ta5 differences (1-4 meV) do not yet answer the trapping question.

### Spin-polarized test 1: relax_pristine_e_spin.in (finished 2026-11-15)
nspin = 2, starting magnetization 0.5 on atom 5 (relabeled Nb5, same pseudopotential and U), started
from the relaxed pristine electron geometry. Same cutoff, k-points, smearing and U values.
- bfgs converged in 15 scf cycles and 14 bfgs steps, JOB DONE, 241 electrons.
- Final energy -3430.87545762 Ry (0.33 eV below the nspin = 1 relaxed electron, -3430.85150622 Ry).
- Not a single polaron: total magnetization 0.00, with opposite moments on two sites
  (Tr[ns] up-down: Nb5 +0.536, Ti2 -0.567). d-occupation gain on Nb5 +0.137 vs neutral.

### Spin-polarized test 2: relax_pristine_e_spin_m1.in (finished 2026-11-15)
Test 1 plus tot_magnetization = 1 (121 up, 120 down), started from test 1's final geometry. First
attempt killed 03:15 when the Claude Code session ended (partial output kept as .killed); relaunched
detached at 11:47.
- bfgs converged in 2 scf cycles and 1 bfgs steps, JOB DONE. Final energy -3430.87544497 Ry
  (0.17 meV above test 1, i.e. the same state).
- Total magnetization 1.00. Spin (Tr[ns] up-down) split between two sites 5.43 A apart:
  Ti2 +0.568, Nb5 +0.537. Electron is localized, but on two non-neighboring sites, not one.
- Likely cause: Gaussian smearing (degauss 0.01 Ry) allows a fractional split between two
  near-degenerate localized states.

### Spin-polarized test 3: relax_pristine_e_spin_fixed.in (failed 2026-11-15)
Test 2 with occupations = 'fixed' (smearing and degauss removed), started from test 2's final geometry.
- convergence NOT achieved after 100 iterations. SCF accuracy fell to ~1e-5 Ry by iteration 50, then
  oscillated there (conv_thr 1e-8). Consistent with the electron hopping between two near-degenerate
  localized states. No energy. Output kept.

### Spin-polarized test 3b: relax_pristine_e_spin_fixed2.in (stopped 2026-11-15)
Test 3 with SCF-convergence settings only: mixing_beta 0.3 -> 0.1, mixing_mode = 'local-TF',
electron_maxstep = 300. Physical settings unchanged.
- Same plateau: SCF accuracy flat at ~2e-5 Ry from iteration ~90 to 117. Stopped by hand at 17:33
  (would not reach 1e-8). Output kept.

## Cell-size problem (found 2026-11-15)
The 30-atom primitive cell has a lattice translation (a-b) of only 3.83 A. An electron placed on
one site is 3.83 A from its own periodic images, so the calculation describes a chain of electrons,
not one isolated polaron. Small-polaron calculations normally need >= ~10 A between images. This
likely explains all of the above (delocalized in nspin = 1, two-site split with smearing, no SCF
convergence with fixed occupations).
- Structure itself checked and fine: all 9 metals are 6-coordinated (M-O 1.75-2.40 A) once both
  periodic images of the apical O along the 3.83 A axis are counted.
- make_pristine_distorted.py was written but NOT run (it moves the apical O14 asymmetrically).

### Supercell timing benchmark: scf_pristine_neutral_sc.in (finished 2026-11-15)
90-atom supercell built by make_supercell_1x3.py from the relaxed neutral pristine geometry:
A1 = a, A2 = 3(b-a), A3 = c (10.42 x 11.50 x 12.07 A, volume 1229.16 A^3 = 3 x primitive).
Neutral SCF, all settings as relax_pristine_neutral.in except K_POINTS 2 1 2 (same k-density).
720 electrons, 4 k-points, ~6.7 GB RAM. Purpose: measure cost before deciding on the supercell.
- Converged in 23 iterations, JOB DONE, 2h16m wall (~6 min per SCF iteration).
- E = -10294.41624087 Ry. 3 x primitive neutral (-3431.53114476) = -10294.59343428 Ry, so the
  supercell is 2.41 eV higher. Structure checked: all 27 metals 6-coordinated, O bond count 162 = 27 x 6.
- Suspected cause: the 2x1x2 supercell mesh samples different k-points than the primitive 2x2x2 mesh.

### Unfolding check: scf_pristine_neutral_unfold.in (finished 2026-11-15)
Built by make_unfold_check.py: the 30-atom relaxed neutral cell with exactly the 12 k-points that
the supercell's 4 k-points unfold to.
- Converged in 25 iterations, JOB DONE. E = -3431.47207222 Ry.
- 3 x E = -10294.41621666 Ry vs supercell -10294.41624087 Ry: difference 0.33 meV. The supercell
  is built correctly; the 2.41 eV gap was entirely k-point sampling.
- Same 30-atom structure, different k-points: -3431.47207 (12 unfolded pts) vs -3431.53114 (2x2x2),
  0.80 eV apart. The 2x2x2 mesh is far from converged in total energy. Polaron energies are
  same-mesh differences so much of this should cancel, but it needs a convergence test.

## k-point convergence test (finished 2026-11-15)
scf_pristine_neutral_k3.in and _k4.in: relaxed neutral pristine 30-atom cell, SCF, K_POINTS 3 3 3
and 4 4 4. Everything else identical to the unfolding check. Run in sequence.

| Mesh | k-points | E (Ry) | Change from previous |
|---|---|---|---|
| 2x2x2 | 8 | -3431.53114476 | n/a |
| 3x3x3 | 14 | -3431.47210776 | +0.803 eV |
| 4x4x4 | 36 | -3431.46667798 | +73.9 meV (2.46 meV/atom) |
| 12 unfolded supercell points | 12 | -3431.47207222 | 0.5 meV from 3x3x3 |

Total energy is not yet converged at 4x4x4 (still moving 2.5 meV/atom). The supercell 2x1x2 mesh is
equivalent to about the 3x3x3 level, not better. Not yet tested: convergence of energy DIFFERENCES
(charged vs neutral, frozen vs relaxed), which is what the polaron energy uses.

## Localization gate: scf_pristine_e_sc_spin.in (finished 2026-11-16)
90-atom pristine supercell at the relaxed neutral geometry, tot_charge = -1, nspin = 2,
tot_magnetization = 1, starting_magnetization 0.1 on all Ti and Nb (no site favoured), 2x1x2 mesh.
- 721 electrons (361 up, 360 down). Converged in 40 iterations, JOB DONE, 6h52m wall.
- E = -10293.74265555 Ry. Total magnetization 1.00, absolute 2.14 Bohr mag/cell.
- NOT localized. Spin (Tr[ns] up-down) is spread evenly over the three periodic copies of two sites:
  Ti (30-atom index 2) +0.25 each, Nb (30-atom index 9) +0.17 each; every other site < 0.06.
  No site above 0.5. d-occupation change per site at most +0.06 vs the neutral supercell.
- Per Dev's instruction, stopped here: no Ta or other dopant runs.
- Note: this SCF is at the undistorted (frozen) geometry. A small polaron normally needs the lattice
  to distort around it, so a delocalized result here does not rule out a polaron after relaxation.

## Seeded polaron relaxation: relax_pristine_e_sc_seed9.in (running; restarted 2026-11-16 13:05)
First attempt (started 06:16) died silently at 11:14 during the first SCF (iteration 24, accuracy ~2e-6 Ry),
one minute after the Claude app released its power assertion; no QE error, disk and memory fine.
Partial output kept as relax_pristine_e_sc_seed9.out.killed. Relaunched with run_pw_launchd.sh (launchd
job, independent of the terminal and the Claude app), identical input.
Purpose: test whether a localized electron is stable once the lattice can relax. Built by
make_sc_polaron_seed.py from the 90-atom neutral supercell:
- supercell atom 9 (first copy of 30-atom site 9) relabeled Nb9, same pseudopotential and U
- its 6 O neighbours pushed outward by 0.1 A (initial guess only; BFGS relaxes everything)
- tot_charge = -1, nspin = 2, tot_magnetization = 1, starting_magnetization 0.5 on Nb9 only
- all other settings as scf_pristine_neutral_sc.in. 721 electrons, ~9.4 GB RAM.
Reading the result: if the electron stays on one site (> ~0.5 e) and the final energy is below the
delocalized gate energy (-10293.74265555 Ry), a small polaron is stable and
E_trap = E(gate, delocalized) - E(this, relaxed). If it spreads back out, no stable polaron at site 9.
Expected finish: Nov 19.

- Status 2026-11-17 14:19: still running (first BFGS step: 2 energies done). Battery about to run out; if the Mac dies the run must be restarted (rename the partial output to .killed first).

### Restart after battery shutdown (2026-11-17 16:15)
relax_pristine_e_sc_seed9.out stopped at 14:26 when the Mac lost power. It completed 3 SCF energies
(-10293.71600627, -10293.75316050, -10293.76707906 Ry; forces 0.315 then 0.162 Ry/Bohr), so the
lattice is relaxing and the energy is falling. Already 0.33 eV below the delocalized gate energy
(-10293.74265555 Ry); not a result until the relaxation converges.
Restarted as relax_pristine_e_sc_seed9_r2.in (built by make_restart_from_last.py): same input, positions
from the last ATOMIC_POSITIONS block printed in the old output, new prefix. BFGS history starts fresh.

### Status before second power-down (2026-11-18 12:10)
relax_pristine_e_sc_seed9_r2 progress (forces in Ry/Bohr):

| SCF | Energy (Ry) | Total force | vs gate (eV) |
|---|---|---|---|
| r2 #1 (= old #3 geometry) | -10293.76707905 | 0.0798 | -0.332 |
| r2 #2 | -10293.77144996 | 0.0484 | -0.392 |

Forces keep falling (0.315, 0.162, 0.080, 0.048 across all SCFs). Latest positions copied to
seed9_r2_last_positions.txt. If the run dies, restart with
`python3 make_restart_from_last.py relax_pristine_e_sc_seed9_r2 relax_pristine_e_sc_seed9_r3`
then `./run_pw_launchd.sh relax_pristine_e_sc_seed9_r3`. Not a result until BFGS converges and localization is checked.

### Second power loss and restart (2026-11-19)
Battery guard auto-saved at 4% (11:25, commit 17c80c9); Mac died ~11:46. r2 completed 5 SCFs:
energies -10293.76707905, -10293.77144996, -10293.77498381, -10293.77722711, -10293.77806572 Ry;
forces 0.0798, 0.0484, 0.0403, 0.0288, 0.0210 Ry/Bohr. Last energy is 0.482 eV below the
delocalized gate energy. At SCF #5 the spin is concentrated on atom 9 (site moment 0.35 vs next 0.08).
Restarted 12:58 as relax_pristine_e_sc_seed9_r3 (positions after r2 step 5, built by make_restart_from_last.py).

## Pristine 90-atom polaron result (2026-11-21)
Seeded relaxation stopped by Dev's decision at 09:51 after 14 SCF/BFGS steps (r1 3, r2 5, r3 6):
energy had stopped changing (last 4 steps -0.0034 eV total, last step -1.7 meV) while the max force
component crawled 0.0030 -> 0.0026 Ry/Bohr (QE default stop is 0.001). Output kept as
relax_pristine_e_sc_seed9_r3.out (+ .stopped_final copy); final evaluated geometry in
pristine_polaron_final_positions.txt.

| Quantity | Value |
|---|---|
| E(delocalized, neutral geometry) = gate | -10293.74265555 Ry |
| E(localized, relaxed), last SCF | -10293.77969580 Ry |
| **Trapping energy E_trap = E(deloc) - E(loc)** | **0.504 eV** |
| Max force component at stop | 0.0026 Ry/Bohr (total force 0.0099) |

Localization (last SCF, spin up minus down in the Hubbard d occupation):
atom 9 (Nb, site 9) **0.818**, next Ti2 0.141, Nb5 0.098. Site moment atom 9 0.365 vs next 0.078.
In the delocalized gate the largest single-site value was 0.248 (shared over 3 Ti2 copies and
3 Nb9 copies). So the extra electron forms a **small polaron on Nb site 9**.
E_trap uses the same definition as before (frozen = charged at neutral geometry, minus relaxed).
Caveats: stopped above the default force threshold; 2x1x2 mesh (~3x3x3 primitive level) not converged
in absolute energy, difference convergence untested; reference geometry is the 30-atom neutral relaxed
structure tiled, not re-relaxed in the supercell.

## Ta runs (started 2026-11-21 09:53, Dev: "Go with Ta, now")
Built by make_sc_ta.py, identical protocol to pristine, one Ta per 90 atoms:
- Ta9: Ta on supercell atom 9 (the pristine polaron site), seeded on atom 9.
- Ta5: Ta on supercell atom 5 (site-5 copy nearest atom 9, 3.89 A), seeded on atom 9 (Nb).
Each: delocalized reference SCF (scf_TaX_e_sc_spin, forces printed) then seeded relax
(relax_TaX_e_sc_seed9). Stop rule matching where pristine was stopped: forc_conv_thr 3.0d-3,
etot_conv_thr 3.0d-4. Running in sequence via run_chain_launchd.sh (log chain_ta.log).
Note for interpretation: U(Ta-5d)=3.1 eV vs U(Nb-4d)=5.2 eV (from the original setup), so a smaller
U on Ta by itself disfavours localization on Ta; discuss with mentor.

## PROBLEM FOUND 2026-11-22: reference geometry not at equilibrium -> 0.504 eV is NOT final
scf_Ta9_e_sc_spin (charged delocalized reference, Ta on atom 9) converged in 75 iterations,
E = -10686.84056405 Ry, and printed forces: total 0.20 Ry/Bohr, largest single-atom forces 0.05 Ry/Bohr
on atoms 5-7 A from Ta, identical in all three supercell copies (e.g. atoms 8/68, 55/85). So the forces
come from the starting structure itself (30-atom neutral cell relaxed with the old 2x2x2 mesh, tiled 3x),
not from Ta. Confirmed in the pristine polaron relaxation: atoms 6-9 A from the polaron moved up to
0.12 A, more than the polaron site's own neighbours (mean 0.05 A).
Consequence: E(deloc at unrelaxed geometry) - E(loc relaxed) = 0.504 eV also contains the relaxation
energy of the starting structure. **Treat 0.504 eV as an upper bound, not the trapping energy.**
Fix (same definition, same parameters): relax the neutral supercell first, compute the delocalized
reference there, and seed the Ta polarons from their own relaxed neutral geometries.
pipeline_relaxed_ref.py runs the 8 steps in order (log pipeline.log), started 10:06 via
run_pipeline_launchd.sh. Ta chain stopped 15 min into relax_Ta9_e_sc_seed9 (partial output kept as
relax_Ta9_e_sc_seed9.out.killed). scf_Ta9_e_sc_spin.out kept but superseded.
