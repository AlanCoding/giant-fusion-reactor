# Reference D-Breeder Target Card

[← Implosion physics](README.md) · [D–T pusher ledger](dt-pusher.md) · [D–T / deuterium economy](../fuel-cycle/dt-deuterium-economy.md)

This is a reusable geometry-and-isotope reference card for the fully
D-directed path. It is a first-pass accounting target, not an optimized design.

## Shared core

| Quantity | Reference value |
| --- | ---: |
| N14/H core radius before compression | 10.0 m |
| N14/H no-void starting density | 0.4718 g/cm³ |
| Core mass | 1.98×10⁶ kg |
| Peak core radius | 0.779 m |
| Peak core density | 998 g/cm³ |
| Density compression ratio | 2.12×10³ |
| Catalytic N14/H pairs in one complete core inventory | 7.95×10³¹ |

The D-directed route uses this inventory first as ¹²C/H to make ¹³N, then as
recovered ¹³C/alpha to make one breeder neutron per initial catalyst unit. The
geometric core is a reference mass scale; the reaction-specific chemistry is
loaded in separate shots.

## D–T density convention

| Quantity | Reference value |
| --- | ---: |
| D–T shell density before compression | 0.25 g/cm³ |
| D–T shell density at peak compression | 250 g/cm³ |
| Provisional D–T density compression ratio | 1.00×10³ |

The core and pusher use different compression ratios in this card. Their
relative radius and pressure histories are not solved yet.

## Two D-producing implosion shots

The isotope screen assumes 10% useful driver energy per reaction and 10%
D–T-fusion-to-useful-drive coupling. That requires 0.110 D–T pairs per core
catalyst unit for the ¹²C+p primary shot, and 0.126 pairs for the
¹³C+alpha neutron-source shot.

If each D–T shell burns thoroughly enough to supply only that required D–T
energy, its geometry is:

| Shot | D–T mass burned | Compressed D–T thickness | Peak shell outer radius | Uncompressed shell thickness | Initial shell outer radius |
| --- | ---: | ---: | ---: | ---: | ---: |
| ¹²C+p → ¹³N | 72.9 t | 3.65 cm | 0.816 m | 22.7 cm | 10.227 m |
| ¹³C+alpha → ¹⁶O+n | 83.1 t | 4.14 cm | 0.820 m | 25.8 cm | 10.258 m |

These are two separate target shots, so the masses are not two layers on one
simultaneous target. Together they burn 156 t of D–T per full-core maximal
breeder event.

## The 10-cm pusher reference

For comparison, a 10-cm D–T shell at peak compression around the same core has
mass 216 t and outer radius 0.879 m. At uncompressed D–T density, it begins
as a 64.6-cm shell with outer radius 10.646 m.

Thus, under the 10%-driver and 10%-coupling assumption, a 10-cm shell is more
than the D–T energy required for either individual D-breeder shot. It could
work if its D–T burn fraction is roughly 34% for the ¹²C+p shot or 38% for the
¹³C+alpha shot. If the pusher instead burns nearly completely, its excess
energy must be charged to a stronger drive, a different coupling assumption,
or a smaller shell.

## Isotope closure on this card

Use 90% recovery of each pusher neutron into lithium-bred T. For the combined
two-shot breeder event, burned D–T pairs are 0.236 per D produced. Only 0.0236
of the breeder neutron needs diversion to replenish the remaining T deficit.

Resulting first-pass balance per one breeder neutron:

| Item | Atoms or equivalent pairs |
| --- | ---: |
| D produced in hydrogen blanket | 0.9764 |
| D consumed in pushers | 0.2360 |
| D surplus | 0.7404 |
| T consumed in pushers | 0.2360 |
| T recovered from pusher neutrons | 0.2124 |
| T made from breeder neutron via lithium | 0.0236 |
| T surplus | 0 |

The first-pass economic statement is therefore precise: this geometry closes
only if the two pusher shells achieve the assumed useful-drive coupling and
the pusher-neutron-to-T recovery is close to 90%. It leaves 0.740 surplus D
per maximally D-directed catalyst event before real transport and recovery
losses are applied.

## What changes this card

The following values must become scan axes, not hidden constants: core radius,
core compression, D–T compressed density, D–T burn fraction, useful drive
coupling, pusher-neutron T recovery, breeder-neutron D recovery, and
reaction-specific driver fraction. This card is the current zero-order point
from which those scans can be measured.

