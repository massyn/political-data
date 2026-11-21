"""AU Net Overseas Migration (quarterly, persons in the year to quarter end) - ABS.

Dataflow ERP_COMP_Q measure 9 (net overseas migration), Australia, quarterly,
published in thousands. The value is the sum of the latest four quarters, the
"year ending" figure the ABS headlines. Run directly:
    python -m collectors.au_net_overseas_migration
"""

from collectors.abs_api import fetch


def collect() -> list[tuple]:
    quarters = fetch("ERP_COMP_Q,1.0.0", "9.AUS.Q")
    return [
        (quarters[i][0], round(sum(v for _, v in quarters[i - 3 : i + 1]) * 1000))
        for i in range(3, len(quarters))
    ]


if __name__ == "__main__":
    rows = collect()
    print(f"{len(rows)} rows, {rows[0][0]} to {rows[-1][0]}")
    for row in rows[-6:]:
        print("\t".join(str(c) for c in row))
