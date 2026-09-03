# Lithium and Tritium Supply

[← Fuel cycle](README.md) · [D-T baseline](../reactions/dt.md)

This page asks whether lithium can support the complete ordinary-hydrogen route: catalytic CNO processing makes deuterium, then D-T fusion turns that deuterium into helium. It is a resource-accounting screen, not yet a blanket design.

## Ideal lithium requirement

The proposed deuterium breeder has approximate bookkeeping:

\[
6p \rightarrow {}^4He + D + 3e^+ + 3\nu_e.
\]

If every produced D is burned once in D-T fusion, each D-T event requires one T. In the idealized lithium cycle, its neutron converts one lithium nucleus into the replacement T:

\[
{}^6Li+n \rightarrow {}^4He+T.
\]

Therefore the irreducible best-case inventory requirement is

\[
\left(\frac{Li}{p}\right)_{\rm minimum}=\frac{1}{6}\approx0.167.
\]

This already assumes perfect neutron capture, zero tritium-decay loss, no blanket leakage or parasitic absorption, and useful access to every lithium nucleus. Any real system requires more lithium; this is a lower bound, not an achievable design value.

If only naturally abundant ${}^6Li$ is used, its 7.5% isotopic fraction raises the ideal *natural-lithium* feed requirement to approximately $1/(6\times0.075)\approx2.2$ Li atoms per proton. Isotope separation changes the logistics, not the total amount of ${}^6Li$ ultimately consumed.

## Cosmological abundance check

For orientation, the Particle Data Group quotes a primordial ${}^7Li/H$ abundance of $(1.6\pm0.3)\times10^{-10}$, while ${}^6Li/{}^7Li$ is at most a few percent in the cited stellar measurements. That primordial baseline is about $10^9$ times below even the ideal all-lithium requirement of $1/6$. It is not legitimate to substitute today’s local, chemically concentrated lithium deposits for this galaxy- or universe-scale inventory question.

So the initial intuition is confirmed very strongly: a lithium-fed D-T finishing step cannot be the dominant universe-scale route for processing hydrogen. It may still be valuable as a scarce ignition technology, a local industrial fuel, or a bridge while a non-lithium tritium cycle is developed.

## Alternative tritium routes to examine

1. **Neutron recycling on deuterium:** $n+D\rightarrow T+\gamma$. A D-T neutron could replace the T consumed by a later D-T event, making T catalytic and avoiding lithium consumption. Its capture probability, competing interactions, gamma handling, and required target geometry need a transport calculation.
2. **D-D production of T:** the $D+D\rightarrow T+p$ branch makes tritium without lithium, but spends additional breeder-made D and competes with the ${}^3He+n$ branch. It is an isotope-economy trade, not free T.
3. **Lithium-7 breeding:** ${}^7Li+n\rightarrow{}^4He+T+n$ is endothermic and requires energetic neutrons. It can broaden usable lithium inventory but still consumes lithium and requires a full neutron-spectrum calculation.
4. **Other neutron-to-tritium conversion media:** candidates such as ${}^3He(n,p)T$ trade the lithium bottleneck for an even scarcer isotope unless a separate production cycle closes their inventory.

The next calculation should compare these routes as *T supplied per breeder-produced D*, including neutron losses and required materials—not merely their reaction bookkeeping.

## Sources to develop

- [Particle Data Group: Big Bang nucleosynthesis review](https://pdg.lbl.gov/2022/reviews/rpp2022-rev-bbang-nucleosynthesis.pdf)
- [IAEA: Fundamentals of Fusion Technology](https://www-pub.iaea.org/MTCD/Publications/PDF/PUB1945_web.pdf)
- [IAEA: tritium-breeding overview](https://nucleus.iaea.org/sites/connect/FUSEpublic/SitePages/Tritium-Breeding.aspx)
