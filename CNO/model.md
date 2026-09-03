# One-Zone Model

[← Study navigation](README.md)

The first model is intentionally a uniform, evolving spherical target rather than a radiation-hydrodynamics simulation. It begins from a condensed target of radius $R_0$, selects a compressed radius $R_c$ and composition, derives temperature from the stated compression closure, and asks whether appreciable burn occurs before disassembly.

Early state variables include radius, density, ion and electron temperatures, photon energy, and isotope abundances. The first comparisons are nuclear reaction time, hydrodynamic time, photon diffusion time, and radiation-field buildup time.

Compression is an initial condition in the first pass. The current temperature rule is a cold isentrope plus a 30% thermal-energy addition for first-pass X-ray/shock heating; see the [temperature closure](analysis/temperature-closure.md). Its energy cost is recorded separately so that fuel-cycle closure cannot hide a proportional D-T compression expense.

See the [analysis plan](analysis/README.md) for the implementation sequence.
