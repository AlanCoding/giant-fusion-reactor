# Reactions Required for Steady Deuterium Production

[← Fuel cycle](README.md) · [D–T / deuterium economy](dt-deuterium-economy.md) · [N14 steady-cycle tradeoff](../codex-gpt-5/results/n14-steady-cycle-tradeoff-2026-09-04.md)

A single 13C(alpha,n)16O event can make one breeder neutron. That is not enough
for sustained deuterium production: every catalyst unit must return to 12C so
it can make another 13N and another breeder neutron. This is the reaction
catalog whose pusher cost and completion fraction must be optimized.

| Stage | Reaction or process | Direct role in D production | Needs D–T pusher? |
| --- | --- | --- | --- |
| 1 | ¹²C(p,gamma)¹³N | Creates breeder-feed parent | Yes |
| 2 | ¹³N beta-plus decay | Makes ¹³C | No; recovery wait |
| 3 | ¹³C(alpha,n)¹⁶O | Makes the one breeder neutron | Yes |
| 4 | neutron moderation and n+p→D | Converts neutron to D | No; H2 blanket |
| 5 | ¹⁶O(p,gamma)¹⁷F | Begins catalyst return | Yes |
| 6 | ¹⁷F beta-plus decay | Makes ¹⁷O | No; recovery wait |
| 7 | ¹⁷O(p,alpha)¹⁴N | Returns N14 and alpha inventory | Yes |
| 8 | ¹⁴N(p,gamma)¹⁵O | Required return leg; likely throughput bottleneck | Yes |
| 9 | ¹⁵O beta-plus decay | Makes ¹⁵N | No; recovery wait |
| 10 | ¹⁵N(p,alpha)¹²C | Regenerates ¹²C and alpha | Yes |

A complete catalytic D event produces at most one D only when all ten stages
are supplied with their required recovery, blanket, and implosion services.
The numerical program must optimize D recovered per D–T burned across this
whole catalog, not maximize burn fraction in any isolated reaction.
