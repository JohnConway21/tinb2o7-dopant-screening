# TiNb2O7 Dopant Screening for Fast-Charging Batteries

## Project Goal
TiNb2O7 is a promising fast-charging battery material, but electron conduction is
limited by polaron trapping at the M1 crystallographic site. This project screens
candidate dopants (Mo, W, Cr, Ta, V, Zr) substituted at the M1 site to find one that
reduces the electron trap depth, using DFT+U calculations in Quantum ESPRESSO.

## Status
- [x] Pristine structure validated (band gap ~2.6 eV with U=5.2 eV on Ti/Nb)
- [x] M1 site identified (Nb site index 6, pymatgen 0-indexed)
- [x] Pristine trap depth baseline: 0.216 eV
- [x] Mo tested: trap depth 0.471 eV (deepens trap — likely not a good candidate)
- [ ] W, Cr, Ta, V, Zr: NOT YET TESTED — help wanted here!

## How to help
Each remaining dopant (W, Cr, Ta, V, Zr) needs the same two-step calculation Mo
already went through:
1. Frozen-structure SCF with one extra electron added (`tot_charge = -1`)
2. Full ionic relaxation with the extra electron (lets the lattice distort)
Then compute: trap_depth = E(frozen) - E(relaxed), in eV.

See `make_qe_input_Mo.py` as the template — copy it, swap the dopant name,
find/verify a literature Hubbard U value for that element's d-orbital, and
run the same pipeline.

## Setup
Requires Quantum ESPRESSO 7.5+, pymatgen, ASE. On Apple Silicon Macs, QE
must run via Rosetta (osx-64 build) — see project history for details.
Pseudopotentials (UPF files) are NOT included in this repo (too large);
download from https://pseudopotentials.quantum-espresso.org for each element.

Set your own Materials Project API key as an environment variable before
running get_structure.py:
    export MP_API_KEY="your_key_here"

## Key files
- `TiNb2O7.cif` — pristine structure (Materials Project mp-1216971)
- `doped_structures/` — pre-built CIFs with each dopant substituted at M1
- `scf_pristine.in`, `scf_electron.in`, `relax_electron.in` — pristine baseline calcs
- `scf_Mo_electron.in`, `relax_Mo_electron.in` — completed Mo calculation (reference template)
- `make_qe_input_Mo.py` — script that generated Mo's input files; copy and adapt for other dopants
