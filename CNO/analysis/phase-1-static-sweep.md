# Phase 1: Static $R_0 \rightarrow R_c$ Implosion Sweep

[← Analysis plan](README.md) · [One-zone model](../model.md)

## Purpose

Screen every **hot implosion reaction** with one common calculation framework. The initial question is not whether a detailed pusher design works; it is whether a target of collected condensed material can react substantially before hydrodynamic disassembly at any plausible $(R_0,R_c,T_i)$ point.

The D-T pusher is common architecture for all such reactions. Its detailed mass, coupling, and isotope cost are intentionally outside this first screen and will be added only after the size/compression requirements are known.

## Sweep shape

```text
for reaction + target composition:
    for uncompressed radius R0:
        calculate M = (4/3)π R0³ ρ0

        for compressed radius Rc, where 0 < Rc ≤ R0:
            calculate ρc = ρ0 (R0/Rc)³

        derive Ti from the stated compression-temperature closure
        calculate reaction/branch rates
        calculate sound speed and thydro ≈ Rc / cs
        calculate tnuc and static burn estimate
        record the full row
```

$R_0$ is the collection-scale coordinate. $R_c$ is the compression-scale coordinate. Do not scan compression ratio instead of $R_c$; derive it for each row.

Suggested initial values from the handoff:

$$
R_0=0.1,\ 0.3,\ 1,\ 3,\ 10,\ 30,\ 100\ \mathrm{m},
$$

with $R_c$ sampled logarithmically below each selected $R_0$. Extend either range whenever the threshold lies on a boundary. $T_i$ is derived from $R_0$ and $R_c$ through the current [compression-temperature closure](temperature-closure.md); it is not an additional scan axis.

## Minimum inputs required before a reaction can enter the sweep

| Input | Why it is needed | Status now |
| --- | --- | --- |
| Reaction stoichiometry and identical-reactant factor | Converts composition into reaction-rate equations | Recorded qualitatively; formal machine input missing. |
| Reactant composition / number fractions | Gives $n_i$ at each density | Preliminary target recipes only. |
| Condensed starting density $\rho_0$ | Converts $R_0$ into mass and $R_c$ into $\rho_c$ | Missing for most reaction-specific target mixtures. |
| Evaluated $\langle\sigma v\rangle(T_i)$ | Determines $t_{\rm nuc}$ | Missing for every reaction in machine-readable form. |
| Q value and product partition | Gives yield and a first energy ledger | Partial. |
| Branching rates | Determines desired product versus leakage | Qualitative only. |
| EOS or explicit sound-speed approximation | Determines $c_s$ and $t_{\rm hydro}$ | Missing. |

The rate fit, target composition/density, and sound-speed model are the three blockers for a genuine first run.

## Calculations per row

Given $R_0$, $R_c$, $T_i$, $T_e$, composition, and the reaction data:

$$
M=\frac{4\pi}{3}R_0^3\rho_0,
\qquad
n_i=\frac{\rho_cX_i}{m_i},
\qquad
t_{\rm hydro}\approx\frac{R_c}{c_s}.
$$

For a two-body reaction $i+j$:

$$
r_{ij}=\frac{n_in_j}{1+\delta_{ij}}\langle\sigma v\rangle,
$$

then estimate a reactant depletion time and static burn fraction over $t_{\rm hydro}$. For branch networks, calculate all competing rates from the same isotope population and record product fractions rather than treating the desired channel in isolation.

## Required output row

Each generated row must contain at least:

| Geometry / state | Kinetics | Result / ledger |
| --- | --- | --- |
| reaction ID, composition, $R_0$, $R_c$, $C_\rho$, $M$, $\rho_0$, $\rho_c$, $T_i$, $T_e$ | $n_i$, $\langle\sigma v\rangle$, branch rates, $c_s$, $t_{\rm hydro}$, $t_{\rm nuc}$ | desired and total burn fraction, each product fraction, yield, nuclear Q energy **generated**, threshold flags |

Generated results belong in `analysis/results/` and must be reproducible from committed inputs and scripts.

## Required Phase-1 radiation filter

The static reaction calculation is not sufficient to call a row ignited. For
each hot reaction, add a subsequent energy/transport filter that records
charged-particle deposition, gamma/X-ray production and escape, radiation
diffusion, and radiative loss before ranking a geometry as useful. Its output
is retained energy and an energy-loss fraction, not merely nuclear Q generated.
This is especially important for the proton-capture gamma reactions that make
up most of the CNO path.

## Deliberately deferred from Phase 1

- Detailed D-T pusher mass and implosion coupling
- Compression-energy and D/T inventory cost
- Time-dependent expansion, burn feedback, and $PdV$ cooling
- Ion-electron temperature separation
- Radiation buildup, gamma trapping, charged-particle stopping, and neutron transport
- Recovery chemistry and blanket geometry

These do not disappear; they become filters on any candidate region found by the static sweep. They should not prevent the first all-reaction comparison.

## Acceptance criteria

Phase 1 is complete when every hot-reaction record has one reproducible input definition and produces a sweep table/plot over $R_0$, $R_c$, and $T_i$. A reaction may fail the screen; that is a valid result. The framework is incomplete if a reaction cannot be entered because its input fields are ad hoc or missing.
