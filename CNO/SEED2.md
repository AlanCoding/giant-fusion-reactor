You are building a reproducible computational model of an inertial-fusion fuel cycle. This is a physics/numerical-analysis task, not primarily a prose task.

I will provide diagrams/data describing a modified CNO cycle whose objective is to consume ordinary hydrogen while producing a surplus of deuterium/neutrons usable to sustain the fusion processes required by the cycle.

Your job is to:

1. reconstruct the complete deuterium-surplus reaction cycle from the material I provide;
2. obtain defensible nuclear reaction-rate data for every reaction;
3. construct a zero-dimensional/one-zone inertial-burn model for every difficult fusion step;
4. explicitly model the especially difficult \(^{14}N(p,\gamma)^{15}O\) step;
5. include the DT external pusher and distributed DD auxiliary-heating concepts described below;
6. optimize the complete system over size, compression, and temperature/heater fraction;
7. calculate the NET DEUTERIUM ECONOMY of the complete closed cycle;
8. produce plots/tables that reveal whether any physically plausible parameter region has positive deuterium production.

Do not assume that conclusions or numerical estimates in this prompt are correct. Verify them.

## Central figure of merit

The primary quantity is NOT fusion energy gain.

The primary quantity is:

$$
F_D =
\frac{\text{deuterium consumed to operate the cycle}}
     {\text{desired completed fuel-cycle reactions / deuterium produced}}
$$

More fundamentally, maintain an explicit material ledger containing:

* protons consumed;
* deuterons consumed;
* tritons consumed;
* neutrons produced;
* neutrons consumed;
* deuterons produced through neutron capture on hydrogen;
* tritium bred/produced;
* catalytic C/N/O nuclei;
* all relevant side products.

From that ledger calculate both:

$$
D_{\rm net}=D_{\rm produced}-D_{\rm consumed}
$$

and appropriate ratios such as deuterons consumed per completed CNO-surplus cycle.

Do not hide DT consumption by accounting only for tritium. A DT reaction consumes one D as well as one T. Track where the T originated.

If neutrons are converted to deuterium using

$$
p+n\rightarrow D+\gamma,
$$

include the actual neutron-capture efficiency as an explicit parameter rather than silently assuming 100%.

Report both ideal \(100\%\) capture and parameterized realistic capture cases.

## Physical architecture

The baseline target is spherical.

There is an inner CNO/proton fuel payload.

An external cryogenic DT layer is ignited and undergoes self-propagating burn. Treat it as a nuclear exploding pusher rather than as a source of photon radiation pressure.

The intended sequence is:

DT ignition
→ DT burn
→ hot expanding pusher plasma / ablation
→ inward hydrodynamic acceleration
→ low-entropy compression of inner fuel
→ late heating
→ CNO-related fusion burn
→ disassembly.

Do NOT model direct photon momentum as the principal compression mechanism.

Radiation transport, neutron transport and charged-particle stopping can matter for preheat and energy deposition, but compression is hydrodynamic.

## Three principal optimization variables

The central optimization space is:

$$
(R_0,C,T)
$$

where

* \(R_0\) = initial CNO-fuel radius;
* \(C=\rho_f/\rho_0\) = density compression ratio;
* \(T\) = relevant burn ion temperature.

Initially explore broad logarithmic ranges. At minimum consider approximately:

$$
R_0=0.1\text{--}1000\ {\rm m}
$$

and

$$
C=10^2\text{--}10^7.
$$

Choose a defensible temperature range from the actual reaction-rate data.

Do not assume that 10 m or \(C=1000\) is optimal.

At fixed mass compression,

$$
R_f=R_0 C^{-1/3}.
$$

Use this relation consistently.

## Basic inertial burn model

For each reaction \(i+j\), obtain or calculate

$$
\langle\sigma v\rangle_{ij}(T).
$$

Prefer evaluated/tabulated nuclear data or established reaction-rate libraries over hand-fitted guesses.

Calculate characteristic reaction time:

$$
\tau_{ij}\sim\frac{1}{n_j\langle\sigma v\rangle_{ij}}.
$$

Construct a defensible estimate of hydrodynamic confinement/disassembly time, beginning with something like

$$
\tau_{\rm dis}\sim k\frac{R_f}{c_s},
$$

where \(k\) is exposed as a model parameter rather than silently fixed.

Then calculate a burn parameter such as

$$
B=n\langle\sigma v\rangle\tau_{\rm dis}
$$

and corresponding depletion/burn fraction by actually integrating the zero-D rate equations. Do not rely solely on

$$
f=1-e^{-B}
$$

when reactant depletion, unequal stoichiometry, sequential reactions, self-heating or changing temperature matter.

The useful scaling to verify is approximately

$$
B\propto R_0 C^{2/3}
\frac{\langle\sigma v\rangle(T)}{c_s(T)}
$$

under simple assumptions.

Test this numerically.

## The \(^{14}N+p\) bottleneck

Treat

$$
^{14}N(p,\gamma)^{15}O
$$

as a special case.

Do NOT assume a 20–50% burn fraction at \(C=1000\). Calculate it.

Obtain defensible \(S(E)\), resonance and/or evaluated thermonuclear-rate data over the temperature range relevant to this artificial fusion environment. Do not blindly extrapolate an astrophysical low-temperature fit into hundreds-of-keV or MeV conditions if that fit is invalid there.

Calculate:

* \(\langle\sigma v\rangle(T)\);
* reaction time;
* hydrodynamic time;
* burn fraction;
* gamma energy deposition assumptions;
* sensitivity to \(R_0,C,T\).

Plot burn-fraction contours in the \((R_0,C)\) plane for several temperatures.

Specifically locate contours corresponding approximately to:

* 1%;
* 10%;
* 20%;
* 50%;
* 90%.

## Cold compression energetics

Do not assume compression requires heating the payload to burn temperature.

Separate:

1. reversible/cold compression work;
2. implosion bulk kinetic energy;
3. shock/entropy generation;
4. deliberate burn heating.

Build an EOS adequate to determine when the simplistic ideal-gas treatment fails.

At high compression, include at least:

* electron degeneracy;
* Coulomb/nonideal plasma corrections when important;
* radiation pressure when important;
* relativistic-electron corrections if reached.

Determine where increasing \(C\) stops being energetically cheap.

Explicitly calculate compression work per original fuel nucleus/pair as a function of \(C\).

## DT pusher

DT releases approximately 17.6 MeV per fusion reaction.

Do NOT assume all of this becomes useful implosion energy.

Define a pusher coupling efficiency

$$
\eta_p=
\frac{E_{\rm useful\,implosion}}
     {E_{\rm DT\,fusion}}.
$$

Initially sweep \(\eta_p\) over a broad range rather than selecting one favorable value.

For each desired \((R_0,C,T)\), calculate the minimum useful implosion energy and therefore:

$$
N_{\rm DT,pusher}
=
\frac{E_{\rm required}}
     {\eta_p Q_{\rm DT}}.
$$

Translate this into:

* DT mass;
* DT-shell thickness for the specified target radius;
* DT reactions per initial CNO fuel nucleus;
* DT reactions per successfully completed desired reaction.

Distinguish the theoretical energetic lower bound from an engineering/hydrodynamic estimate.

## Distributed auxiliary fusion heater

Investigate a SMALL, spatially distributed auxiliary DD fuel component.

The intended concept is NOT necessarily atomically premixed DD.

Conceptually it may consist of many macroscopic or mesoscopic inclusions distributed throughout the CNO/proton fuel, potentially with separate tampers or thermodynamic trajectories.

Its purpose is:

* remain relatively inactive during low-entropy compression;
* ignite comparatively late;
* provide spatially distributed fusion heating;
* raise CNO/proton ion temperatures near stagnation;
* improve the slow \(^{14}N+p\) burn rate.

Parameterize the auxiliary fuel fraction:

$$
x_{\rm DD}.
$$

Do not assume maximum fusion reactivity is desirable. Premature auxiliary burning is harmful because it raises the fuel adiabat.

The desired auxiliary reaction therefore has:

* low early burn;
* steep late burn;
* high useful deposited energy;
* favorable deuterium/neutron economy.

Model DD branches and subsequent reactions explicitly enough to account for:

$$
D+D\rightarrow T+p
$$

$$
D+D\rightarrow{}^3He+n
$$

and subsequent DT burning where applicable.

Track every deuteron and neutron.

Calculate the auxiliary DD expenditure required to raise the payload from its post-compression state to the desired burn state.

Where possible distinguish ion heating from electron heating and estimate ion-electron equilibration times. Do not automatically assume instantaneous \(T_i=T_e\) if the burn/disassembly timescale is shorter.

## Timing constraint for auxiliary heating

Construct a simple compression trajectory \(C(t)\) or \(\rho(t)\).

Integrate DD reaction rates along it.

For each candidate \(x_{\rm DD}\), determine what fraction of the auxiliary fuel burns:

* too early;
* near desired stagnation;
* after useful confinement is effectively over.

This is essential.

A heater that releases sufficient energy but burns during early compression is not a viable solution.

## Other reactions in the deuterium-surplus CNO cycle

Apply the same general machinery to EVERY fusion/nuclear step in the supplied cycle.

Do not assume that \(^{14}N+p\) is the only bottleneck merely because I expect it to be.

For each step report:

* reaction;
* Q-value;
* products;
* neutron production/consumption;
* D/T production/consumption;
* \(\langle\sigma v\rangle(T)\);
* characteristic burn time;
* required \(R_0,C,T\);
* achievable burn fraction;
* required external pusher/heater expenditure;
* dominant loss or difficulty.

Identify which reactions can plausibly self-heat and which require external/auxiliary heating.

If some steps are vastly easier, demonstrate that quantitatively rather than spending equal computational effort on them.

## Complete cycle closure

After individual reaction models work, assemble them into a complete material-flow model.

For one normalized completed surplus-CNO cycle, construct a table:

reaction | multiplicity | p | D | T | n | He | C/N/O isotope changes | energy

Then sum every column.

The nuclear bookkeeping MUST close.

Any catalytic C/N/O species should return to the required cycle state except where the modified surplus cycle intentionally changes the catalyst path.

Report discrepancies as bugs rather than silently normalizing them away.

Then add the fusion fuels consumed by:

* DT pusher;
* auxiliary DD heater;
* any other ignition/heating process represented in the model.

The final result should state:

$$
D_{\rm gross\,produced}
$$

$$
D_{\rm pusher\,consumed}
$$

$$
D_{\rm heater\,consumed}
$$

$$
D_{\rm other\,consumed}
$$

and

$$
\boxed{
D_{\rm net}
=
D_{\rm gross\,produced}
-
D_{\rm total\,consumed}.
}
$$

Also report a dimensionless surplus factor such as

$$
G_D=
\frac{D_{\rm gross\,produced}}
     {D_{\rm total\,consumed}}.
$$

The cycle closes economically only for

$$
G_D>1.
$$

Do not confuse energetic gain with deuterium gain.

## Optimization

The final optimization should include at least

$$
(R_0,C,T,x_{\rm DD},\eta_p)
$$

plus any genuinely important variables discovered during the work.

For each point calculate:

* desired-reaction burn fractions;
* gross neutron production;
* gross D production;
* DT-pusher D consumption;
* auxiliary-heater D consumption;
* net D;
* \(G_D\);
* total fusion energy;
* characteristic timescales.

Find regions maximizing deuterium surplus rather than energy output.

Produce contour plots showing where:

$$
G_D<1,\quad G_D=1,\quad G_D>1.
$$

Identify the smallest target size at which a positive-surplus solution exists.

Also determine whether increasing \(R_0\) eventually produces diminishing returns and explain which dimensionless quantities have entered their asymptotic regimes.

## Uncertainty and sensitivity

This is extremely speculative physics. Do not report spurious precision.

For important uncertain parameters, perform sensitivity sweeps.

At minimum include:

* pusher coupling efficiency;
* confinement-time coefficient;
* compression ratio;
* reaction-rate uncertainty where material;
* neutron-capture efficiency;
* auxiliary-heater deposition efficiency;
* electron-ion equilibration assumptions.

Report which uncertainty actually controls the sign of \(D_{\rm net}\).

## Code requirements

Build this as a small understandable scientific Python project.

Prefer:

* numpy;
* scipy;
* pandas;
* matplotlib;
* pytest.

Avoid heavyweight frameworks unless genuinely needed.

Organize nuclear data separately from physics/model code.

Every nuclear reaction should be represented as structured data rather than scattered constants.

Include units explicitly. Prefer scipy.constants and/or a unit library if doing so reduces unit mistakes.

Write tests for:

* mass-number conservation;
* charge conservation;
* cycle material closure;
* known limiting cases;
* geometric compression relation;
* energy bookkeeping;
* zero-fuel / zero-coupling cases.

Make plots reproducibly from scripts.

Save intermediate numerical data to CSV/Parquet so results do not exist only as figures.

## Required outputs

Produce at least:

1. `README.md`

   * assumptions;
   * equations;
   * data sources;
   * limitations;
   * instructions.

2. structured reaction database.

3. reaction-rate plots for every relevant reaction.

4. \(^{14}N+p\) burn-fraction contour plots versus \(R_0,C,T\).

5. compression-energy curves versus \(C\).

6. auxiliary-DD timing/heating results.

7. DT-pusher consumption results.

8. complete cycle material ledger.

9. deuterium-surplus contour plots.

10. sensitivity analysis.

11. a concise final `RESULTS.md` stating:

* whether positive deuterium closure was found;
* best parameter region;
* D produced per D consumed;
* dominant physical bottleneck;
* minimum viable scale found;
* assumptions capable of reversing the conclusion.

## Working method

Do not attempt to write the whole model in one pass.

Work iteratively:

A. Parse and verify the reaction network.
B. Implement nuclear bookkeeping and tests.
C. Obtain/validate reaction-rate data.
D. Implement single-reaction zero-D burn.
E. Reproduce hand-calculable limiting cases.
F. Implement compression/disassembly scaling.
G. Implement pusher accounting.
H. Implement auxiliary-DD heating.
I. Assemble complete cycle.
J. Optimize.
K. Perform sensitivity analysis.
L. Audit results.

RUN THE CODE after every major stage.

Inspect numerical output rather than assuming code that executes is physically correct.

When an intermediate result is surprising, stop and perform an independent order-of-magnitude calculation before continuing.

Do not silently invent missing nuclear data. If a value cannot be sourced or derived defensibly, flag it and parameterize it.

Do not optimize before verifying that the underlying reaction network and individual reaction models are correct.

Most importantly: actively try to falsify the design. The objective is not to produce a positive result. The objective is to determine whether the complete deuterium economy closes under any defensible parameter regime.
