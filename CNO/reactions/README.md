# Reaction Records

[← Study navigation](../README.md)

Each record holds evaluated reaction data, target-state assumptions, physical screening inputs, network links, and source provenance. The common [cryogenic target architecture](../target-architecture.md) applies unless a record states otherwise. Numerical values explicitly marked *provisional* are working inputs, not validated design values.

## Hot core reactions: energy release and catalyst return

These are target-specific implosion reactions in the staged-CNO energy loop or the return leg of the breeder network.

- [12C(p,γ)13N](c12-p-g-n13.md): shared entry capture and branch point.
- [13N(p,γ)14O](n13-p-g-o14.md): staged-CNO hot branch.
- [14N(p,γ)15O](n14-p-g-o15.md): shared return-loop capture.
- [15N(p,α)12C](n15-p-a-c12.md): alpha/helium release and carbon regeneration.
- [16O(p,γ)17F](o16-p-g-f17.md): breeder return leg.
- [17O(p,α)14N](o17-p-a-n14.md): breeder return leg and alpha/helium release.

## D-T pusher

- [D + T → 4He + n](dt.md): external cryogenic implosion driver, not bulk primary fuel.

## Deuterium breeder

These two dependent records form the dedicated D-breeding branch: a hot neutron-source shot followed by a separate hydrogen capture blanket.

- [13C(α,n)16O](c13-a-n-o16.md): imploded 13C + 4He source target; creates the breeder neutron.
- [n(p,γ)D](n-p-g-d.md): external H2 capture blanket; converts the source neutron into recovered deuterium.
