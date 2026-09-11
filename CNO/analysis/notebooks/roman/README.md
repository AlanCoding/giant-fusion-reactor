# Roman Workbook Sequence

The workbooks are intentionally ordered by dependency rather than by how
impressive a final system diagram would look. Each notebook must run from a
fresh kernel and must expose every assumption needed to reproduce its tables.

## Rules

1. One primary physical question per notebook.
2. Use packaged datasets through `cno_sweep`; do not paste cross sections or
   reaction-rate fits into cells.
3. Keep units in column names and use SI internally.
4. Separate input assumptions, calculated values, and acceptance criteria.
5. Do not import variables from another live notebook kernel.
6. A later workbook may read a deliberately exported JSON/CSV result only
   after that result has a stated model version and uncertainty boundary.
7. Clear large transient outputs before committing; preserve small tables that
   are part of human review.

## Planned order

| Workbook | Question |
|---|---|
| `00_data_and_cycle_map.ipynb` | Are the accepted architecture and reusable datasets visible and internally consistent? |
| `10_constantine_burn_escape.ipynb` | Is there a C13 burn / neutron-escape window without central hydrogen? |
| `20_trajan_driver.ipynb` | What pressure impulse can the N15+p mantle provide under explicit burn and tamper assumptions? |
| `30_caesar.ipynb` | Minimum viable C12 proton-capture target |
| `40_aurelian.ipynb` | Minimum viable O16 proton-capture target |
| `50_scipio.ipynb` | Minimum viable O17 proton-alpha target and ash-removal burden |
| `60_diocletian.ipynb` | Minimum viable N14 bottleneck target |
| `70_material_ledger.ipynb` | N15, CNO, D, T, neutron, and recovery closure using accepted chamber results |
| `80_system_reference.ipynb` | Smallest defensible common reference design and sensitivity envelope |

Only workbook 00 exists at this boundary. Creating numerical placeholders for
the later workbooks would make assumptions look more settled than they are.

