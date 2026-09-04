# Reaction Rates

[← Sources](README.md)

## Baseline library: JINA REACLIB

The starting rate source for the common Phase-1 framework will be a pinned
snapshot of the [JINA REACLIB database](https://reaclib.jinaweb.org/index.php).
It provides recommended reaction rates and downloadable, versioned libraries;
its documented seven-coefficient form represents the temperature-dependent
rate as a function of $T_9$. See the [format guide](https://reaclib.jinaweb.org/docs/reaclibFormat.pdf).

This is a **screening baseline**, not a validation of any imploding target.
REACLIB is intended for astrophysical model calculations, and each selected
fit must be checked for its stated/evidenced range before using a temperature
point in the sweep. This is particularly important for reactions involving
short-lived nuclei and for the upper end of the proposed temperature grid.

## Pinning rule

Before any numerical output is treated as a result, place the downloaded
library in `analysis/data/rate-libraries/` with a manifest recording:

- source URL and retrieval date;
- snapshot/library name and upstream modification date;
- file name and SHA-256;
- selected rate entry or entries for each reaction;
- the conversion from source units to the sweep's SI
  $\langle\sigma v\rangle$;
- the accepted temperature interval and the source that supports it.

The rate entry itself belongs in the library file, rather than being copied
into a reaction page or target card. A reaction card then points to the exact
entry through `library_ref` and `fit_ref`.

## First pinned primary entries

The first sweep uses the selected forward entries in
[`primary-reaclib-default-2026-06-09.json`](../analysis/data/rate-libraries/primary-reaclib-default-2026-06-09.json).
It records the JINA default snapshot date, retrieval date, upstream SHA-256,
and the two REACLIB contributions for each reaction:

| Reaction | REACLIB labels | Source provenance in REACLIB |
| --- | --- | --- |
| $^{12}$C$(p,\gamma)^{13}$N | `ls09n`, `ls09r` | Li, Z. et al., experimental rate evaluation, 2010. |
| $^{13}$N$(p,\gamma)^{14}$O | `lg06n`, `lg06r` | Z. H. Li et al., *Physical Review C* 74, 035801 (2006). |
| $^{14}$N$(p,\gamma)^{15}$O | `im05n`, `im05r` | REACLIB-selected forward contributions; source-label bibliography pending. |

These coefficients permit a real first numerical screen. They do **not** by
themselves establish fitness at every proposed implosion temperature; the
generated rows are visibly marked as screening-only until each rate's
energy/temperature support is reviewed.

## Needed cross-checks

The Phase-1 table needs the desired channel *and* competitive hot channels.
Use reaction-specific evaluated cross sections/rates as a second source where
they exist, especially for D-T/D-D pusher burn and $^{13}\mathrm{N}(p,\gamma)^{14}\mathrm{O}$ branch control. Record disagreements rather than averaging them silently.
