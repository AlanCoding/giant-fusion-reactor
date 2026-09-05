# Three-Oven Neutron Recovery and Energy-Deposition Audit

[← Analysis](../README.md) · [Finite-EOS and grouping audit](eos-grouping-ledger-audit-2026-09-04.md)

## Executive result

At the fixed conservative three-oven point, with

$$
P=0.3153395206574428
$$

burned pusher D-T pairs per completed cycle, the exact simple-ledger result is

$$
\boxed{G_D(\eta_{DT,n},\eta_{DD,n})
=\frac{1+P(\eta_{DT,n}+\eta_{DD,n})}{5P}
=0.6342370268+0.2(\eta_{DT,n}+\eta_{DD,n}).}
$$

The parity contour is

$$
\boxed{\eta_{DT,n}+\eta_{DD,n}
=5-\frac{1}{P}=1.8288148662.}
$$

Thus the requested approximation $\eta_{DT,n}+\eta_{DD,n}\simeq1.83$ is
correct. At exactly 1.83, $G_D=1.00023703$. The physical part of the contour
inside the unit square is the short segment from
$(0.828814866,1)$ to $(1,0.828814866)$.

The neutron calculation does **not** establish that the conservative point
crosses this contour:

- A separate D-D plant embedded in a sufficiently thick ordinary-H blanket
  can approach $\eta_{DD,n}=1$ in the present ideal geometry.
- The frozen fuel-cycle model does not specify the time-dependent D-T pusher
  burn needed to determine $\eta_{DT,n}$. A static unburned shell gives only
  $\eta_{DT,n}=1.81\times10^{-4}$; an instantaneous, already-all-He-4 shell
  gives the ideal ceiling 0.96771. Only the latter crosses parity when added
  to the separate-source D-D result.
- In the static uniform-mixture calculation, parity with
  $\eta_{DD,n}=1$ requires a residual D-T fraction below
  $6.57\times10^{-9}$, or more than 99.999999343% shell burn. A propagating
  front initially exposes roughly half of its neutrons to ash on the outward
  side, giving an outward-only estimate near $\eta_{DT,n}=0.5$ and
  $G_D=0.93424$. Recovery of enough of the inward-going half to exceed
  0.8288 requires a coupled burn-wave/transport calculation absent from the
  zero-D model.

Consequently $\eta_{DT,n}+\eta_{DD,n}>1.83$ exists as an ideal all-ash limit,
but it is **not yet a physically demonstrated value** for this pusher. Any
inert ablator, less-than-unit pusher burn, or co-located He-3 makes recovery
worse.

The separate energy-deposition audit gives a more favorable answer for a
different reason. The fixed cores are so optically thick that the
charged-product/recoil-only and all-Q-local brackets collapse almost to the
all-Q side. Without reoptimizing any core state, the three-oven pusher cost
falls to $P=0.2229009102$. The corresponding parity sum is only 0.513701586.
With a separate D-D source in H, $\eta_{DD,n}\simeq1$ alone then gives
$G_D=1.09731$, even while the D-T material recovery is held at its static
unburned value. This is still an idealized zero-D result, but it identifies
local product-energy deposition—not D-T neutron breeding—as the mechanism
that changes the sign.

## 1. Exact ledger and parity contour

For every pusher D-T burn, the support economy consumes:

1. one D in the pusher;
2. four D in statistically equal D-D branches to make the replacement T;
3. and produces one D-D companion neutron as well as one D-T neutron.

The desired C13(alpha,n) neutron contributes the fixed leading one breeder D.
Therefore

$$
D_{\rm gross}=1+P\eta_{DT,n}+P\eta_{DD,n},
\qquad D_{\rm consumed}=P+4P=5P.
$$

Some useful checks at the conservative $P$ are:

| $\eta_{DT,n}$ | $\eta_{DD,n}$ | $D_{\rm gross}$ | $D_{\rm consumed}$ | $G_D$ |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 1.000000 | 1.576698 | 0.634237 |
| 0 | 0.8 (old assumption) | 1.252272 | 1.576698 | 0.794237 |
| 1 | 0 | 1.315340 | 1.576698 | 0.834237 |
| 0 | 1 | 1.315340 | 1.576698 | 0.834237 |
| 1 | 1 | 1.630679 | 1.576698 | 1.034237 |

The result depends only on the sum of the two probabilities. This is why even
perfect recovery of either population by itself cannot close the conservative
point.

## 2. Frozen target and minimum-pusher geometry

No fusion-system parameter was reoptimized. Every core still has initial
radius $R_0=1000$ m, unit pusher coupling, and the compression and seed
temperature from the conservative three-oven audit. The compressed geometry
used for neutron transport is:

| Oven | Compressed core $R_f$ (m) | Core density (kg m$^{-3}$) | Core areal density (kg m$^{-2}$) | Pusher D-T / cycle | Minimum D-T thickness (m) | D-T areal density (kg m$^{-2}$) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 32.18298 | $1.5\times10^7$ | $4.8274\times10^8$ | 0.0222065 | 0.0689958 | $1.03494\times10^6$ |
| 2 | 10.00000 | $5.0\times10^8$ | $5.0000\times10^9$ | 0.2197763 | 0.115363 | $5.76813\times10^7$ |
| 3 | 14.93802 | $1.5\times10^8$ | $2.2407\times10^9$ | 0.0733567 | 0.0844455 | $1.26668\times10^7$ |

This is the most favorable shell consistent with the energy ledger: pure
equimolar D-T, 100% pusher burn, shell density equal to compressed core
density, and no inert ablator. Its mass is inferred from the required number
of burned D-T pairs, not from an arbitrary thickness. The small radial
thickness is deceptive; the compressed areal column is enormous. A real
ablator/pusher material was not specified, so none was invented. Adding one
would introduce more scattering and parasitic channels.

## 3. Neutron-transport model

The compact cross-section card is extracted from the official
[ENDF/B-VIII.0 neutron sublibrary](https://www.nndc.bnl.gov/endf-b8.0/download.html),
whose published archive MD5 is checked before extraction. It retains MF=3
total, elastic, and radiative-capture tables for H-1, D, T, He-3, He-4, C-12,
C-13, N-14, N-15, O-16, and O-17. The archive does not contain neutron
evaluations for the short-lived N-13, O-15, or F-17 daughters. Pusher neutrons
are generated before or during the core burn, so the initial core inventory is
used; all evaluated stable reactants and products relevant at that time are
included.

For each 14.1-MeV or 2.45-MeV source population, the calculation uses:

- evaluated elastic slowing and energy-dependent nonelastic removal;
- ordinary condensed H at 70.8 kg m$^{-3}$ outside the target;
- a bound-H elastic cross section of 82.03 b below 1 eV;
- age/diffusion transport at the 0.0253-eV cutoff;
- H-1(n,gamma)D as the only successful material-recovery score;
- all nonelastic reactions on C/N/O/D/T/He as loss of the source neutron.

Treating every nonelastic event as source-neutron loss is conservative for
neutron count because it does not follow secondary neutrons from (n,2n) or
inelastic reactions. Conversely, the static compressed-shell calculation
does not model expansion, a D-T burn wave, or time-dependent isotope
replacement. It must therefore be interpreted as a composition bracket, not
a final Monte Carlo target prediction.

The H-only source is followed by analog spherical histories until it reaches
the thermal diffusion regime. The target calculation uses continuous slowing
and spherical diffusion because its shell columns are tens of thousands of
thermal diffusion lengths thick. At 0.0253 eV, the condensed-H diffusion
length in this closure is 0.02587 m.

## 4. H-blanket sweep

Two D-D placements are shown because the fuel-cycle ledger never specified
where tritium makeup occurs:

- **co-located** injects the D-D neutron into the minimum pure D-T pusher. It
  is optimistic because it omits the extra D-D fuel and strongly absorbing
  He-3 ash that a real co-located makeup system would contain;
- **separate source** starts the D-D neutron at the center of its own H
  blanket, representing an external tritium plant that ships T to the pusher.

| H thickness (m) | H areal density (kg m$^{-2}$) | $\eta_{DT,n}$, static unburned pusher | $\eta_{DD,n}$, co-located | $\eta_{DD,n}$, separate H source |
| ---: | ---: | ---: | ---: | ---: |
| 0.10 | 7.08 | 0.000177 | 0.000196 | 0.04444 |
| 0.25 | 17.7 | 0.000181 | 0.000200 | 0.53165 |
| 0.50 | 35.4 | 0.000181 | 0.000200 | 0.93544 |
| 1.00 | 70.8 | 0.000181 | 0.000200 | 0.99978 |
| 2.00 | 141.6 | 0.000181 | 0.000200 | 1.00000 |
| 5--50 | 354--3540 | 0.000181 | 0.000200 | 1.00000 |

The separate-source numbers use 5,000 histories at each thickness; the exact
last digits are therefore not meaningful, but the asymptotic conclusion is
clear. The target result saturates after about 0.5 m because neutrons are lost
in the D-T shell, not by escaping the outer H boundary.

At 50 m the static-unburned per-oven recovery is:

| Oven | $\eta_{DT,n}$ | $\eta_{DD,n}$ | Dominant failure |
| --- | ---: | ---: | --- |
| 1 | 0.0018240 | 0.0020176 | D(n,gamma)T in pusher |
| 2 | 0.00003265 | 0.00003611 | D(n,gamma)T in pusher |
| 3 | 0.00012776 | 0.00014132 | D(n,gamma)T plus core parasitics |
| Pusher-weighted | **0.00018092** | **0.00020013** | pusher absorption |

## 5. The D-T burn-state disconnect

The following sweep assigns one uniform, static composition to the entire
pusher while holding its loaded mass fixed. It is a sensitivity test, not a
burn-wave model.

| Uniform shell burn | Residual D-T | $\eta_{DT,n}$ | $\eta_{DD,n}$ if co-located |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 0.000181 | 0.000200 |
| 0.90 | $10^{-1}$ | 0.001248 | 0.001273 |
| 0.99 | $10^{-2}$ | 0.004894 | 0.004905 |
| 0.999 | $10^{-3}$ | 0.016042 | 0.016045 |
| 0.9999 | $10^{-4}$ | 0.049620 | 0.049621 |
| 0.99999 | $10^{-5}$ | 0.109867 | 0.109867 |
| 1 (all He-4 ash) | 0 | **0.967707** | **0.967707** |

The discontinuity is physical to this frozen static geometry: even a tiny
residual D inventory remains optically thick across $10^6$--$10^8$ kg m$^{-2}$.
At zero burn the thermal absorption times are approximately 4.97, 0.149, and
0.497 microseconds in ovens 1--3, comparable to or shorter than their hot
dwells. At exactly complete burn, He-4 has no evaluated thermal absorption and
the neutron eventually reaches either H in the core or the external blanket.

The old scalar `pusher_burn_fraction=1` fixes loaded fuel cost but does not
say whether the neutron sees unburned fuel, ash, or a moving interface. That
missing temporal specification, rather than outer-H thickness, now controls
the conservative-point parity claim.

## 6. Product-energy deposition

This calculation is separate from the preceding material ledger. It does not
credit neutron heat while evaluating $\eta_n$.

Capture-gamma opacity uses the Klein-Nishina Compton cross section, which is a
deliberately minimal subset of the processes tabulated by
[NIST XCOM](https://www.nist.gov/pml/xcom-photon-cross-sections-database).
Charged products use a deliberately loose 1 kg m$^{-2}$ upper bound on range;
the relevant reference tools are NIST [PSTAR](https://physics.nist.gov/PhysRefData/Star/Text/PSTAR.html)
and [ASTAR](https://physics.nist.gov/PhysRefData/Star/Text/ASTAR.html). Even
these conservative treatments give essentially complete deposition because
the core columns are $4.8\times10^8$--$5.0\times10^9$ kg m$^{-2}$.

| Oven | Capture gamma (MeV) | Gamma deposition | Charged-product deposition lower bound | C13(alpha,n) neutron deposition |
| --- | ---: | ---: | ---: | ---: |
| 1 | 1.94300 | 0.9999996725 | 0.9999999984 | -- |
| 2 | 0.60027 | 0.9999999814 | 0.9999999999 | 0.9999999507 |
| 3 | 7.29680 | 0.9999998348 | 0.9999999997 | -- |

For neutrons born in the D-T shell, elastic recoil alone deposits at least
0.92865 of 14.1-MeV energy and 0.999998 of 2.45-MeV energy before an evaluated
nonelastic removal or the thermal cutoff. If the removal products and gammas
are also contained, the upper bounds are respectively 0.9999999982 and
0.9999999897. These pusher/support-neutron energies are **not** added to core
self-heating: unit pusher coupling already credits the full D-T Q as useful,
so adding them again would double-count energy.

Replacing the two earlier artificial core-deposition limits by the calculated
fractions, with every core radius, compression, seed temperature, dwell, and
coupling unchanged, gives:

| Oven | Completion | Peak T (keV) | Pusher D-T / completion |
| --- | ---: | ---: | ---: |
| 1 | 0.987491 | 319.891 | 0.0221919 |
| 2 | 0.951047 | 242.738 | 0.132522 |
| 3 | 0.950467 | 363.084 | 0.0681874 |
| **Cycle** | -- | -- | **0.222900910** |

The resulting material ledgers are:

| Neutron-recovery interpretation | $\eta_{DT,n}$ | $\eta_{DD,n}$ | $G_D$ |
| --- | ---: | ---: | ---: |
| Both neutron populations co-located in static unburned pusher | 0.000240 | 0.000266 | 0.897361 |
| Static-unburned D-T pusher; separate D-D source in H | 0.000240 | 1.000000 | **1.097308** |
| Burn-front outward-only estimate; separate D-D source | 0.500000 | 1.000000 | **1.197260** |

The physical shell on each shot is unchanged: deposited Q improves the number
of completed second-step reactions per initial target, so the cost *per
completion* falls even though seed energy per initial catalyst does not. The
aggregate neutron efficiencies are reweighted by the new per-completion oven
costs. The first row does not close. The separate-source rows do, because at
$P=0.222900910$ their D-D recovery alone exceeds the new parity requirement
0.513702. This is a fixed-point transport correction, not a new fusion
optimization.

## 7. Boundaries and next required model

The largest remaining uncertainty is no longer blanket thickness. It is the
coupled time sequence of pusher burn, neutron birth, slowing, capture, and
shell disassembly. A physically decisive next model needs radial D/T/He-4
burn fractions versus time and must transport neutrons across that moving
composition. It should also follow secondary neutrons from nonelastic
channels and include whatever real ablator or structural material the target
requires.

The present result is appropriately read as:

- external H can recover essentially all neutrons from a geometrically
  separate D-D plant;
- the minimum compressed D-T pusher can prevent external recovery unless it
  turns into ash early enough;
- conservative-point parity is possible only at the all-ash edge of the
  current bracket, not demonstrated in the middle;
- calculated local deposition at the enormous fixed core columns reduces the
  pusher cost enough that a separate D-D plant closes the ledger even without
  useful D-T-neutron recovery.

## Reproduction

After downloading the official neutron archive to `/tmp`:

```bash
.env/bin/python analysis/scripts/extract_light_neutron_cross_sections.py \
  --archive /tmp/ENDF-B-VIII.0_neutrons.zip \
  --output analysis/data/neutron-transport/endfb-viii0-light-mf3.json

.env/bin/python analysis/scripts/audit_neutron_recovery.py \
  --cross-sections analysis/data/neutron-transport/endfb-viii0-light-mf3.json \
  --sweep-output analysis/results/neutron-recovery-sweep.csv \
  --burn-state-output analysis/results/neutron-pusher-state-sweep.csv \
  --deposition-output analysis/results/three-oven-deposition.csv \
  --histories 5000
```

Generated CSVs are intentionally ignored by Git; this document records their
material conclusions.
