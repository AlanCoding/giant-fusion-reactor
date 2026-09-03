# Phase-1 Input Status

[← Analysis plan](README.md) · [Data contract](data/README.md) · [Reaction records](../reactions/README.md)

This is the entry checklist for the common $R_0\rightarrow R_c$ static sweep.
Every row uses the same geometry, compression, burn-time, and output ledger;
only the reaction, target recipe, rate entries, branches, and EOS inputs vary.

| Hot reaction | Target card | Desired-rate entry | Competing-rate entries | Mixture / $\rho_0$ | Sound-speed model | Ready? |
| --- | --- | --- | --- | --- | --- | --- |
| [D-T pusher](../reactions/dt.md) | Stubbed | Missing | Missing | Provisional $\rho_0$; shell geometry unselected | Missing | No |
| [$^{12}$C$(p,\gamma)^{13}$N](../reactions/c12-p-g-n13.md) | [$^{12}$C+$p$](data/targets/c12-one-proton-primary.json) and [$^{12}$C+$2p$](data/targets/c12-two-proton-primary.json) inventory cards | [Pinned REACLIB screening entry](data/rate-libraries/primary-reaclib-default-2026-06-09.json) | Not yet | Fixed from component densities | Provisional ideal model | **Screening run only** |
| [$^{13}$N$(p,\gamma)^{14}$O](../reactions/n13-p-g-o14.md) | Same two primary-shot cards | [Pinned REACLIB screening entry](data/rate-libraries/primary-reaclib-default-2026-06-09.json) | Not yet | Fixed from component densities | Provisional ideal model | **Screening run only** |
| [$^{14}$N$(p,\gamma)^{15}$O](../reactions/n14-p-g-o15.md) | Missing | Missing | Missing | Missing | Missing | No |
| [$^{15}$N$(p,\alpha)^{12}$C](../reactions/n15-p-a-c12.md) | Missing | Missing | $^{15}$N$(p,\gamma)^{16}$O | Missing | Missing | No |
| [$^{16}$O$(p,\gamma)^{17}$F](../reactions/o16-p-g-f17.md) | Missing | Missing | Missing | Missing | Missing | No |
| [$^{17}$O$(p,\alpha)^{14}$N](../reactions/o17-p-a-n14.md) | Missing | Missing | $^{17}$O$(p,\gamma)^{18}$F | Missing | Missing | No |
| [$^{13}$C$(\alpha,n)^{16}$O](../reactions/c13-a-n-o16.md) | Intentionally stubbed | Missing | $^{13}$C$(\alpha,\gamma)^{17}$O | Deferred with its reaction record | Deferred | No |

The $n(p,\gamma)D$ capture is a breeder-blanket transport/recovery problem,
not a hot spherical fuel-ball entry in this sweep. Its inputs enter a later
neutron-transport/blanket calculation.

## Exact minimum for a `ready` row

1. A target card stating isotope mass fractions, physical phase/layering,
   selected ambient density, and the reaction zone it represents.
2. A pinned desired-channel rate entry and all material competing channels,
   with the allowed temperature range.
3. An EOS or explicitly labeled approximation that supplies $c_s(\rho_c,T_i,T_e,\mathrm{composition})$.
4. Product/Q ledger and any identical-reactant factor.

The first three are genuine data choices. They cannot be filled by extrapolating
the existing prose without choosing an unapproved target recipe or a
high-temperature model.

## Implementation order

1. Pin the rate-library snapshot and build its small adapter.
2. Select an EOS approximation common enough for the first screen, then state
   its applicability limits.
3. Add target cards, beginning with D-T and the primary $^{12}$C$+p$ mixed-path
   fuel ball.
4. Add cards for the remaining implosion reactions and enable the sweep only
   for rows whose audit is clean.
