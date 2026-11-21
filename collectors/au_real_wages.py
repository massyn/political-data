"""AU Real Wage Growth (quarterly, annual %) - ABS WPI and CPI via the ABS Data API.

Real growth = (1 + WPI annual growth) / (1 + CPI annual growth) - 1, with both
annual changes computed from the quarterly index four quarters apart:
  WPI 1.2.0  total hourly rates of pay excluding bonuses, private and public, original
  CPI 2.0.0  all groups, original, weighted average of eight capital cities
Run directly: python -m collectors.au_real_wages
"""

from collectors.abs_api import annual_change, fetch


def collect() -> list[tuple]:
    wages = annual_change(fetch("WPI,1.2.0", "1.THRPEB.7.TOT.10.AUS.Q"), 4)
    prices = annual_change(fetch("CPI,2.0.0", "1.10001.10.50.Q"), 4)
    return [
        (d, round(((1 + w / 100) / (1 + prices[d] / 100) - 1) * 100, 1))
        for d, w in wages.items()
        if d in prices
    ]


if __name__ == "__main__":
    rows = collect()
    print(f"{len(rows)} rows, {rows[0][0]} to {rows[-1][0]}")
    for row in rows[-6:]:
        print("\t".join(str(c) for c in row))
