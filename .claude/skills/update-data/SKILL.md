---
name: update-data
description: Refresh the political-data indicators - run the collectors, sanity-check every new value against its official source, hand-fill whatever the collectors missed or got wrong, validate, commit on a working branch and update the Citadel project row. Use whenever the user asks to refresh, update, or check the freshness of the data, or says the dashboard is stale.
---

# Update the data

Australia and World indicators are live in `data/`. SA and US material lives under `archive/` and in `reference.md`. Manual indicators (no `collector:`) have step-by-step instructions in `reference.md`; whenever a metric cannot be given a collector, record how to update it there.

## 1. Sync and branch

Follow `massyn:devops`. Never run git on main. Reuse the open working branch if its PR is unmerged; otherwise `git pull --ff-only` on main and `git switch -c data-refresh-<yyyy-mm>`.

## 2. Run the collectors

```bash
python update.py
```

Read the lists it prints:

- **Updated** - a collector wrote rows. These are not trusted yet (step 3).
- **Errors** - collector failed or returned nothing. Look the value up by hand (step 4).
- **Manual update required** - no collector (`au_prime_minister`, `au_emergency_department_wait_times`). Check whether the source has published something new since `last_updated`; if not, no change.

- **Missing periods** - the series skips an expected month or quarter (collectors only append the newest rows). Fill these by hand in step 4.

Anything not mentioned and "already up to date" still gets the freshness check in step 5.

## 3. Verify every written value

A collector writing one bad number is this project's recurring failure. Run `git diff -U0 data/` and, for each added row, check the right period, right magnitude and right sign against the source. Collectors have previously written basis-point changes as rates and a $315bn stock value as a mean price.

| Indicator | Verify with | Notes |
|---|---|---|
| Unemployment, CPI, WPI, GDP, house price | `WebFetch` the *specific* ABS release page, e.g. `.../labour-force-australia/oct-2026`, `.../consumer-price-index-australia/sep-2026`, `.../wage-price-index-australia/sep-2026`, `.../total-value-dwellings/jun-quarter-2026` | Never `/latest-release`. ABS URL slugs vary by release (quarterly Total Value of Dwellings uses `jun-quarter-2026`; on a 404 try the other form, or fall back to WebSearch). |
| RBA cash rate | `WebSearch` "RBA cash rate <month> <year>" | `rba.gov.au` returns 403 to WebFetch. Rows use the day *after* the decision (the RBA table's date). |
| ED wait times | `WebFetch` AIHW | Annual, usually no change. |

If a value is wrong: do not keep it. Correct the YAML, then fix the collector so `python update.py --force <id>` is a clean no-op, and record the date and change in `reference.md`.

## 4. Fill gaps by hand

Collectors only append the newest rows and have skipped periods before (unemployment once jumped Jul to Oct). `update.py` lists these under "Missing periods" (month-end series only; irregular series such as the RBA rate are skipped). Add any missing `YYYY-MM-DD: value` keys under `graph[].data` in chronological position. Date rules: quarter-end is Mar 31 / Jun 30 / Sep 30 / Dec 31, month-end is the real last day, RBA is the table date.

CPI: add the YoY rate only. The index series (base 2011-12=100) stays frozen pending a rebasing decision - ask before resuming it.

## 5. Freshness and validation

1. For every indicator compare `last_updated` against today and `frequency` using the staleness limits in CLAUDE.md. Anything stale that the source has published must be updated; if the source has not published yet, say so in the summary.
2. `last_updated` must equal the newest date in the file.
3. `python build.py` must exit 0 with no traceback.

## 6. Line endings and commit

Repo is LF (`.gitattributes`). Check `git ls-files --eol data` for `w/crlf` and convert with `sed -i 's/\r$//'`. Stage data files by path only. Commit message names the periods, e.g. `Refresh AU data through Nov 2026`, with revisions noted in the body. No AI attribution. Push the branch; open a PR only if asked.

## 7. Update the Citadel row

Follow `citadel-project-register`: refresh the political-data row's Updated date in entry 301 (projects room).

## 8. Report

One short table: indicator, new value, how it was verified (source), plus anything collected-but-unverified, anything hand-filled, anything still stale, and any collector that needs fixing.

Collector details, SA/US notes, known technical limits and fix history are in `reference.md`.
