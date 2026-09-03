# First-Pass Compression Temperature Closure

[← Analysis plan](README.md) · [Primary sweep input](data/sweeps/primary-reference.json)

## Current rule

The primary sweep has only two geometric axes: uncompressed radius $R_0$ and
compressed radius $R_c$. Assembly temperature is fixed at $T_0=20\ \mathrm K$.
The compressed one-zone ion/electron temperature is derived, not scanned:

$$
C_\rho=\left(\frac{R_0}{R_c}\right)^3,
\qquad
T_{c,\mathrm{cold}}=T_0C_\rho^{\gamma-1},
\qquad
T_c=1.30\,T_{c,\mathrm{cold}},
$$

with $\gamma=5/3$. The factor $1.30$ means “30% more thermal energy than the
cold isentrope,” which is also a 30% temperature multiplier for the ideal
monatomic one-zone closure.

This gives an intentionally simple lower-bound-plus-correction model. It is
not a claim that X-ray heating is a uniform 30% effect.

## Return after the first geometry answers

Replace the constant multiplier with a coupled pusher/radiation model. In
particular, calculate X-ray production, opacity and deposition, pusher/core
areal densities, and the size-dependent transition from volumetric heating to
short X-ray path lengths and surface-shock propagation. Those effects can make
the thermal trajectory strongly fuel-ball-size dependent.

Only that later model can map a desired $R_c$ and derived thermal state to a
D-T pusher mass, shell thickness, implosion velocity, and coupling cost.
