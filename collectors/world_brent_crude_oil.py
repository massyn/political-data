"""World Brent Crude Oil Price (monthly average, US$ per barrel) - US EIA via FRED.

FRED series MCOILBRENTEU: Crude Oil Prices, Brent - Europe, monthly average of
the EIA daily spot price, from May 1987. Run directly:
    python -m collectors.world_brent_crude_oil
"""

from collectors.fred import monthly


def collect() -> list[tuple]:
    return [(d, round(v, 2)) for d, v in monthly("MCOILBRENTEU")]


if __name__ == "__main__":
    rows = collect()
    print(f"{len(rows)} rows, {rows[0][0]} to {rows[-1][0]}")
    for row in rows[-5:]:
        print("\t".join(str(c) for c in row))
