# 13N Branch Control: Energy Loop or Deuterium Breeder

[← Fuel cycle](README.md) · [12C(p,γ)13N record](../reactions/c12-p-g-n13.md)

This is the first major physical fork in the fuel cycle. The shared first capture is

$$
{}^{12}C+p\rightarrow{}^{13}N+\gamma.
$$

After that, a single primary target can yield both paths. Its hot product split is set by proton inventory and integrated burn exposure; the expanding products are later recovered and sorted:

| Desired output | Next action | Physical requirement |
| --- | --- | --- |
| Hot-CNO energy route | $^{13}N+p\rightarrow{}^{14}O+\gamma$ | A fraction of $^{13}N$ receives a second proton during the primary implosion. |
| D-breeder feed | $^{13}N\rightarrow{}^{13}C+e^++\nu_e$ | The remaining $^{13}N$ disassembles with the target, is recovered, and later decays. |

## This is not “low burn versus high burn”

Low total burn fraction mostly leaves unreacted $^{12}C$ and protons; it does not automatically make useful $^{13}C$. The breeder target wants **high first-capture conversion** to $^{13}N$ and **low second-capture conversion** to $^{14}O$.

For a one-zone hot pulse, define the proton-capture exposures

$$
\Phi_{12}=\int n_p\langle\sigma v\rangle_{{}^{12}C+p}\,dt,
\qquad
\Phi_{13}=\int n_p\langle\sigma v\rangle_{{}^{13}N+p}\,dt.
$$

The desired breeder regime is qualitatively $\Phi_{12}\gtrsim1$ while $\Phi_{13}\ll1$. The desired hot-CNO regime is $\Phi_{12}\gtrsim1$ and $\Phi_{13}\gtrsim1$. Whether either separation is possible at an inertial target’s density, temperature, and dwell time must be calculated from evaluated rates; it cannot be inferred from the arrow diagram.

The $^{13}N$ beta-plus half-life is about 9.96 min, vastly longer than an implosion pulse. Beta decay during the hot pulse is therefore negligible. The target’s ordinary hydrodynamic disassembly ends hot exposure; recovery and cold storage then let the surviving $^{13}N$ decay to $^{13}C$.

Likewise, $^{14}O$ beta-plus decays to $^{14}N$ with a half-life of about 70.6 s. Therefore, if separation occurs after the decay waits, the elemental separation is **carbon ($^{13}C$) from nitrogen ($^{14}N$)**, not carbon from oxygen. That is the relevant industrial sorting question.

## The two primary-shot reference cases

The sweep has two explicit initial-inventory reference cases:

- **$^{12}$C+$p$ case:** [one initial proton per $^{12}$C](../analysis/data/targets/c12-one-proton-primary.json). This is the $^{13}$N/$^{13}$C-leaning reference.
- **$^{12}$C+$2p$ case:** [two initial protons per $^{12}$C](../analysis/data/targets/c12-two-proton-primary.json). This is the $^{14}$O/$^{14}$N-leaning reference.

Stoichiometry alone is not a selector. Any unreacted proton can capture on either $^{12}C$ or newly made $^{13}N$. Both cases must calculate the complete $^{12}C$, $^{13}N$, and $^{14}O$ output, then use the result as the algebraic lever for later D-heavy cycle choices.

## Practical target concepts to compare

1. **$^{12}$C+$p$ mixed-path target:** load one initial proton per carbon nucleus, accept its calculated split, recover products after disassembly, wait for decay, and separate $^{13}C$ from $^{14}N$.
2. **$^{12}$C+$2p$ mixed-path target:** use two initial protons per carbon nucleus and make the same complete product ledger.

They are controls of the same broad target/chamber architecture, not distinct reactor types. Intermediate and D-heavy inventories remain later continuous variables.

## What decides the fork

The numerical model must map product fractions $f_{12C}$, $f_{13N}$, and $f_{14O}$ as functions of $R_0$, $C$, $T_i$, dwell/expansion history, and initial $n_p/n_{12C}$. It should report the contamination ratio

$$
\frac{N_{14O}}{N_{13N}+N_{14O}}
$$

for the breeder-production target, and its complement for the energy target. Only then can the pathway be called physically separable.

## Sources

- [Physical Review C: $^{13}N(p,\gamma){}^{14}O$ triggers hot CNO when capture overtakes beta decay](https://journals.aps.org/prc/abstract/10.1103/PhysRevC.69.055807)
- [Physical Review C: hot-CNO conversion rate analysis](https://journals.aps.org/prc/abstract/10.1103/PhysRevC.102.045805)
- [NNDC: evaluated $^{13}N$ beta-plus decay](https://www.nndc.bnl.gov/ensnds/13/C/ec_decay.pdf)
