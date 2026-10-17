# 0001 — Pin ASAP7 to lambdapdk v0.2.17

Status: accepted (issue #2). Date: 2026-10-17.

## Context

ASAP7 is not in the fleet's `open_pdks` store. No sibling ASAP7 canary has a
committed bring-up (their repos hold scaffolds only as of this date), so there
is nothing to adopt. klayout-tools' own ASAP7 deck, extraction deck and
shipped-cell gate are all defined against lambdapdk `v0.2.17`.

## Decision

Pin the ASAP7 source to the lambdapdk `v0.2.17` release archive, sha256
`ac7e950c4d0394a829658b6e219fea4a4b0c61a998183d5520f8b9e38c6efff2`, fetched
into a scratch directory and never committed. The full pin, tool versions and
per-file checksums are in `spec/bringup.md`. Any bump is a new decision record
that re-runs `verification/bringup/reproduce.sh` and appends its results.

## Consequences

- The deck, DRM text (`asap7_drm_201207a.pdf`) and shipped reference cells all
  come from one archive, so a disagreement between them is attributable.
- Sibling canaries adopt this pin by reference to `spec/bringup.md`.
- Alternatives not taken: upstream ASAP7 repositories directly (the klt deck is
  not validated against them), and an `open_pdks`-style store (does not exist
  for ASAP7 here).
