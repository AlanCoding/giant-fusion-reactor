# Central-Ignitor Burn-Front Screen

[← Analysis plan](README.md) · [Seeded 0-D model](seeded-burn-model.md) · [$^{14}$N benchmark](../reactions/n14-p-g-o15.md)

## Why the uniform-seed result is not an ignition requirement

The current seeded one-zone calculation gives its stated seed energy to the
entire compressed sphere. That is useful only as a conservative mixing
reference. It is **not** the architecture under discussion: a compact D-T
ignitor can create a central hot region while most of the CNO fuel begins cold
and dense.

The relevant reduced question is therefore not “can the entire sphere be
raised to fusion temperature?” It is:

> Can a central hot spot replace its losses with locally deposited reaction
> energy, then deliver enough heat to ignite successive cold shells before the
> assembly disassembles?

This is the inertial-fusion hot-spot/burn-wave distinction. In D-T targets the
analogous wave is driven largely by locally stopping charged alpha particles,
not by requiring uniform initial heating of all fuel. [LLNL's ignition overview](https://lasers.llnl.gov/science/achieving-fusion-ignition) describes the same hot-spot-to-dense-fuel sequence.

## Next reduced model: concentric hot spot plus cold shell

This remains low dimensional: spherical symmetry with a small number of
radial zones, not a full hydrodynamics calculation. At peak compression define

$$
R_c,quad \rho_c,quad r_h,quad T_h,quad T_{\rm shell},
\quad \Delta t_{\rm drive},
$$

where $r_h$ and $T_h$ come from the D-T ignitor coupling rather than from a
uniform $E_{\rm seed}$.

For each zone the model will calculate:

1. reaction power $P_{\rm fus}=n_a n_b\langle\sigma v\rangle QV$;
2. a deposition kernel $f_{\rm dep}(r\leftarrow r')$, separately for charged
   products, gammas, and neutrons;
3. local thermal-energy change from deposition, radiation escape, conduction,
   and prescribed expansion; and
4. the outward location at which the next cold zone crosses a specified
   reaction-rate threshold.

That gives a front position $r_f(t)$ and a burn fraction without pretending
that the front is spatially uniform.

## Three pass/fail conditions

The first screen should report all three quantities, rather than collapse them
into one “ignition energy.”

| Condition | Reduced-model test | What failure means |
| --- | --- | --- |
| Hot-spot self-heating | $P_{\rm dep,h}>P_{\rm rad,h}+P_{\rm cond,h}+P_{\rm exp,h}$ | The central seed cools; no sustained source exists. |
| Shell ignition | Deposited energy into the next shell exceeds its energy-to-threshold before the hot spot decays | A hot spot exists but cannot light new fuel. |
| Front outruns disassembly | $r_f(t)$ reaches a useful fraction of $R_c$ before the chosen expansion time | Burning remains localized even if it is self-heating. |

The energy needed to lift a shell is an EOS quantity, approximately

$$
E_{\rm threshold,shell}=\int_{V_{\rm shell}}
\left[u(\rho,T_{\rm threshold})-u(\rho,T_{\rm shell})\right]dV.
$$

It cannot be replaced by the whole-core thermal energy. Conversely, the
deposition fraction cannot be set to one merely because the *entire* sphere is
optically thick: it must be local on the scale of the hot spot and the next
shell.

## Crucial reaction-specific distinction

For D-T, charged 3.5-MeV alphas make the familiar local self-heating channel.
For $^{14}$N$(p,\gamma){}^{15}$O, the prompt reaction energy is gamma energy.
Its potential front is therefore a radiation-heated front, governed by an
energy-dependent gamma attenuation/deposition kernel, not an alpha-stopping
length. The present gray opacity is enough to explore bookkeeping but is not
enough to establish propagation.

The same framework applies to every implosion reaction, but each must supply
its own product energy partition and stopping/transport data. Reactions with
charged products are the best early candidates for an actual burn-front
screen; capture-only reactions remain important but demand better radiation
transport.

## Ordered next steps

1. Keep $^{14}$N as the time-domain **code benchmark** and do not treat it as
   a conclusion about the primary D-producing branch.
2. Add a generic two-zone/finite-shell energy ledger and test it first against
   D-T, where the charged-product deposition channel is defined.
3. Enter product energy partitions and rate data for the primary
   $^{12}$C+$p$ / $^{12}$C+$2p$ mixed-path shot, then run the same geometry
   cards and burn-front screen for its products.
4. Continue the reaction-record completeness work: each implosion reaction
   needs its target card, rate fit/range, product partition, competing paths,
   and transport assumptions before it receives a numerical result.
5. Only after these screens identify promising regions should a D-T
   inventory/coupling calculation map $(r_h,T_h,\Delta t_{\rm drive})$ to a
   pusher mass and geometry.

This ordering keeps the key free variables where they belong: $R_0$ and $R_c$
for the overall target; then the ignitor's hot-spot size, temperature, and
coupling as driver outputs. It does not make compressed temperature or
whole-core uniform seed energy independent design inputs.
