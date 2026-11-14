
## Pseudopotentials
- Source: Quantum ESPRESSO pseudopotential library (pslibrary 1.0.0, PBE, PAW), https://pseudopotentials.quantum-espresso.org
- Not tracked in git (pseudo/*.UPF is gitignored). Download each file separately.
- Ta.pbe-spn-kjpaw_psl.1.0.0.UPF, MD5 70e26a4a8c1f0430003df9f0e8af0a92 (verified on both machines)

## Polaron energy results (total energies in Ry; E_polaron = E_frozen - E_relaxed, tot_charge = -1, 13.6057 eV/Ry)

| System | Neutral relax | Frozen electron | Relaxed electron | Polaron energy (eV) |
|---|---|---|---|---|
| Pristine | -3431.53114476 | -3430.84455676 | -3430.85150622 | 0.0946 |
| Ta9 | -3824.63158809 (10 BFGS steps) | -3823.94061440 (29 iter) | -3823.94748794 (20 BFGS steps) | 0.0935 |
| Ta5 | -3824.62518831 (8 BFGS steps) | -3823.93400701 (29 iter) | -3823.94064044 (12 BFGS steps) | 0.0903 |

- Neutral cell: Ta9 is 0.087 eV lower than Ta5 (stability result, not a trapping result).
- Ta5 frozen and relaxed runs: 241.00 electrons, convergence achieved, JOB DONE.
- A first attempt at the Ta5 relaxed run was killed mid-SCF (machine sleep, no QE error); its partial output is kept as relax_Ta5_electron.out.killed. The reported result is from the full rerun with identical input.
- Differences from pristine: Ta9 -1.0 meV, Ta5 -4.3 meV. No trapping conclusion has been drawn yet; whether these are outside numerical noise is still to be discussed.
