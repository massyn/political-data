"""AU Rent Inflation (quarterly, annual % change) - ABS CPI via the ABS Data API.

Dataflow CPI 2.0.0, Rents (index 30014), original, weighted average of eight
capital cities, quarterly index. The annual change is computed from the index
four quarters apart, so the whole history (1973 onwards) uses one method.
Run directly: python -m collectors.au_rent_cpi
"""

from collectors.abs_api import annual_change, fetch


def collect() -> list[tuple]:
    index = fetch("CPI,2.0.0", "1.30014.10.50.Q")
    return [(d, round(v, 1)) for d, v in annual_change(index, 4).items()]


if __name__ == "__main__":
    rows = collect()
    print(f"{len(rows)} rows, {rows[0][0]} to {rows[-1][0]}")
    for row in rows[-6:]:
        print("\t".join(str(c) for c in row))
