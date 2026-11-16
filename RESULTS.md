
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

## k-point convergence test (running)
scf_pristine_neutral_k3.in and _k4.in: relaxed neutral pristine 30-atom cell, SCF, K_POINTS 3 3 3
and 4 4 4. Everything else identical to the unfolding check. Run in sequence.
