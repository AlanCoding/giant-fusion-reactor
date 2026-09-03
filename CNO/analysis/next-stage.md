# Next Stage: Close Inputs, Then Run the First Screens

[← Analysis plan](README.md) · [Input status](input-status.md) · [Blanket first pass](hydrogen-blanket-first-pass.md)

## Objective

Produce the first comparable static-screen results for the two primary-shot
reference cases—$^{12}$C+$p$ and $^{12}$C+$2p$—without pretending that either
case yields a pure isotope product. Their complete $^{12}$C/$^{13}$N/$^{14}$O
product vectors become the algebraic control inputs for later D-heavy-cycle
optimization.

## Work packages and gates

| Order | Work package | Deliverable | Gate before proceeding |
| --- | --- | --- | --- |
| 1 | Rate ingestion | Pinned evaluated-rate snapshot, manifest, and tested adapter returning SI $\langle\sigma v\rangle(T_i)$ | Each selected entry has a source and stated use range. |
| 2 | Common first-pass plasma closure | An explicitly provisional EOS/sound-speed function, with applicability limits | It accepts $(\rho_c,T_i,T_e,\mathrm{composition})$ and reports $c_s$. |
| 3 | Primary target definitions | Fixed 20 K liquid-$H_2$/solid-carbon additive-volume $\rho_0$ values attached to the two inventory cards | Return later to actual microstructure, void fraction, and pressure support. |
| 4 | Minimal coupled primary network | $^{12}$C$(p,\gamma)^{13}$N and $^{13}$N$(p,\gamma)^{14}$O compete during one hydrodynamic dwell | Product fractions conserve nuclei and protons. |
| 5 | Static $R_0\rightarrow R_c$ sweep | Reproducible rows over $R_0$, $R_c$, $T_i$ for both cards | Rows contain $t_{\rm hydro}$, rates, yields, product vector, and flags. |
| 6 | Ignition/burn surfaces | Contours/tables of desired burn, total burn, and $^{13}$N:$^{14}$O split over $(R_0,R_c)$ | The desired threshold is not on a grid boundary. |
| 7 | Radiation/energy filter | Generated, deposited, and escaped energy for every candidate row | No geometry is called ignited from Q generation alone. |

The D-T pusher uses the same rate/EOS infrastructure, but its coupling and
mass cost stay separate until a core size/compression region survives step 7.

## Parallel but separate breeder-blanket track

The blanket has a bounded first geometry: sweep clean condensed-$H_2$ radial
thicknesses of $0.25$, $0.5$, $1$, and $2\ \mathrm{m}$, beginning with the
conservative $1\ \mathrm{m}$ case. The next calculation is one-dimensional,
energy-dependent neutron transport from the $^{13}$C$(\alpha,n)^{16}$O source,
including core and D-T-shell areal densities. Its output is
$\eta_{n\rightarrow D}$, not merely a capture length.

This track should not block the primary-shot screen, because it has different
physics and inputs. It must converge before any cycle-closure claim is made.

## After the first primary-screen results

1. Convert product vectors and blanket efficiency into a D inventory ledger:
   D produced, D consumed by pusher/ignition, and unrecovered inventory.
2. Add pusher mass/coupling to every surviving core point.
3. Replace the static dwell estimate with a one-zone time evolution.
4. Expand from the two reference proton inventories to a continuous
   $n_p/n_{^{12}\mathrm C}$ sweep, searching for the smallest viable target
   under D-balance constraints.

## Current decision needed at the next gate

The two reference cards now have uncompressed bulk densities. The next gate is
not another target-definition decision: it is to inspect the geometry-screen
output, then decide which surviving region warrants a pusher-coupling model.
