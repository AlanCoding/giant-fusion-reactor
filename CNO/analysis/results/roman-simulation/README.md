# Roman Simulation Result Cards

Commit only compact, reviewable JSON/CSV result cards and plots. Full zone
histories, checkpoints, and transport tallies remain external and are named by
checksums in the result manifest.

`scenario0-verification-v0.1.json` is the initial shared-kernel card. Its
overall acceptance flag is false because the first-order material-contact test
is too diffusive, despite passing conservation and shock checks.

`scenario0-verification-v0.2.json` adds the fixed-mass spherical moving-mesh
kernel. Static and ballistic motion preserve shell interfaces exactly, and the
spherical Noh shock converges under 100/200/400-shell refinement. The overall
card remains unqualified because the separate Eulerian contact gate still
fails.

`layered-mechanical-precursor-v0.1.json` is the first nonreacting application
of that mesh to the likely Diocletian fuel/driver/Pb dimensions. It tests
instantaneous energy, finite pressure-rise time, and mesh resolution. It is a
failure-mode screen, not a qualified target card.

`progressive-driver-v0.1.json` separates the prompt DT share from a slower
cylindrical-growth N15 source. It exposes a timing optimum and the strong
penalty from treating too much driver energy as an early coherent flash. N15
front speed is swept, not calculated.

`gapped-pb-flyer-v0.1.json` is the first explicit vacuum-gap/Pb-flyer
mechanical precursor. Its companion figures show the radius history,
species-density profiles, two-temperature profiles, and the initial gap/Pb
allocation sweep. It contains no core burn or radiation transport.

`staged-pb-shells-v0.1.json` tests three Pb shells, two vacuum gaps, and a
prescribed 1:2:8 energy staircase. It records sequential Pb/Pb and Pb/fuel
collisions, mesh convergence, and the largest-pulse timing optimum. Total Pb,
driver mass, and driver energy match the one-flyer comparison. Its 22.98-fold
compression is slightly worse than the 23.75-fold one-flyer result and is
archived as an unsuccessful compression architecture, not a reference design.
