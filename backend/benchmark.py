import json
from pathlib import Path

BENCHMARK_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "price_benchmarks.json"
)


def load_benchmarks():
    with BENCHMARK_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def benchmark_item(item_name, billed_price):
    benchmarks = load_benchmarks()

    if item_name not in benchmarks:
        return {
            "item": item_name,
            "status": "not_found",
            "billed_price": billed_price,
            "benchmark_price": None,
            "difference": None,
            "source": None,
            "message": "No benchmark available for this item."
        }

    benchmark = benchmarks[item_name]

    benchmark_price = float(
        benchmark["benchmark_price"]
    )

    billed_price = float(billed_price)

    difference = billed_price - benchmark_price

    if difference > 0:
        status = "higher_than_benchmark"
    elif difference < 0:
        status = "lower_than_benchmark"
    else:
        status = "matches_benchmark"

    percentage_difference = 0

    if benchmark_price > 0:
        percentage_difference = (
            difference / benchmark_price
        ) * 100

    return {
        "item": item_name,
        "billed_price": round(billed_price, 2),
        "benchmark_price": round(benchmark_price, 2),
        "difference": round(difference, 2),
        "percentage_difference": round(
            percentage_difference,
            2
        ),
        "status": status,
        "source": benchmark["source"]
    }


def benchmark_bill(line_items):
    results = []

    for item in line_items:

        description = item.get("description")
        unit_price = item.get("unit_price")

        if not description or unit_price is None:
            continue

        try:
            result = benchmark_item(
                description,
                float(unit_price)
            )

            results.append(result)

        except (ValueError, TypeError):
            results.append({
                "item": description,
                "status": "invalid_price",
                "message": "Could not calculate benchmark."
            })

    return results