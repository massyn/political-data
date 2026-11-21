"""AU Underemployment Rate (monthly, %) - ABS Labour Force via the ABS Data API.

Dataflow LF_UNDER, item M23 (underemployment rate, proportion of labour force),
persons, all ages, seasonally adjusted, Australia. Returns the full history.
Run directly: python -m collectors.au_underemployment
"""

from collectors.abs_api import fetch


def collect() -> list[tuple]:
    return [(d, round(v, 1)) for d, v in fetch("LF_UNDER,1.0.1", "M23.3.1599.20.AUS.M")]


if __name__ == "__main__":
    rows = collect()
    print(f"{len(rows)} rows, {rows[0][0]} to {rows[-1][0]}")
    for row in rows[-6:]:
        print("\t".join(str(c) for c in row))
