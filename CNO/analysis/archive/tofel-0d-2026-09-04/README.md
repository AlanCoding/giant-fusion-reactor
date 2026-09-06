# Archived TOFEL-0D Result

This directory freezes the conclusion of the D-T-pushed **Three-Oven
Finite-EOS Ledger (TOFEL-0D)** before development of the p+N15 secondary
pusher began.

The complete source, inputs, generated tables, tests, and narrative at the
archive boundary are preserved by Git commit:

```text
817fc3b Some finishing touches
```

The principal reports in that snapshot are:

- `analysis/results/eos-grouping-ledger-audit-2026-09-04.md`
- `analysis/results/neutron-recovery-and-deposition-audit-2026-09-04.md`
- `analysis/results/deuterium-loop-audit-2026-09-04.md`

To inspect or rerun the exact archived tree without disturbing current work:

```bash
git worktree add /tmp/cno-tofel-0d 817fc3b
```

The machine-readable headline values are in `result-summary.json`. Later
p+N15 work must not silently replace these assumptions or relabel its results
as TOFEL-0D.

## Archived conclusion

The original six-independent-implosion architecture failed badly. Correcting
the electron EOS and grouping prompt reactions into three beta-separated hot
events reduced the ideal support cost substantially. At the conservative
charged-products/recoil deposition point, pusher expenditure was
$P=0.3153395207$ D-T pairs per completed cycle and $G_D=0.794237$ under the old
neutron assumptions. Transport-estimated local deposition reduced the fixed
point to $P=0.2229009102$; a separate D-D source with nearly complete
neutron-to-D recovery then gave $G_D=1.097308$.

That favorable result was conditional on unit pusher coupling, complete D-T
burn, extremely large compressed targets, recoverable carryover inventories,
and no time-resolved pusher burn front. It was a screening milestone, not a
reactor closure claim.

