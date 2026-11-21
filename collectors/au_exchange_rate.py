"""AU Exchange Rate (monthly average, US$ per A$1) - Federal Reserve H.10 via FRED.

FRED series EXUSAL: U.S. dollars to one Australian dollar, monthly average of
daily noon buying rates in New York, from January 1971. Run directly:
    python -m collectors.au_exchange_rate
"""

from collectors.fred import monthly


def collect() -> list[tuple]:
    return [(d, round(v, 4)) for d, v in monthly("EXUSAL")]


if __name__ == "__main__":
    rows = collect()
    print(f"{len(rows)} rows, {rows[0][0]} to {rows[-1][0]}")
    for row in rows[-5:]:
        print("\t".join(str(c) for c in row))
