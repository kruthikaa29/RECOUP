def audit_bill(line_items):
    audit_results = []
    seen_items = {}

    for item in line_items:
        description = item.get("description")
        quantity = item.get("quantity")
        unit_price = item.get("unit_price")
        total = item.get("total")

        if not description:
            continue

        # Duplicate check
        normalized_name = description.strip().lower()

        if normalized_name in seen_items:
            audit_results.append({
                "type": "possible_duplicate",
                "item": description,
                "severity": "medium",
                "message": (
                    f"Possible duplicate charge detected for "
                    f"{description}."
                )
            })
        else:
            seen_items[normalized_name] = True

        # Quantity × price check
        try:
            if (
                quantity is not None
                and unit_price is not None
                and total is not None
            ):
                expected_total = (
                    float(quantity) * float(unit_price)
                )

                actual_total = float(total)

                difference = (
                    actual_total - expected_total
                )

                if abs(difference) > 0.01:
                    audit_results.append({
                        "type": "quantity_price_mismatch",
                        "item": description,
                        "severity": "high",
                        "expected_total": round(
                            expected_total,
                            2
                        ),
                        "billed_total": round(
                            actual_total,
                            2
                        ),
                        "difference": round(
                            difference,
                            2
                        ),
                        "message": (
                            f"Quantity × unit price does not "
                            f"match the billed total for "
                            f"{description}."
                        )
                    })

        except (ValueError, TypeError):
            audit_results.append({
                "type": "invalid_amount",
                "item": description,
                "severity": "medium",
                "message": (
                    f"Could not verify the amount for "
                    f"{description}."
                )
            })

    if not audit_results:
        return {
            "status": "no_obvious_errors",
            "total_issues": 0,
            "issues": []
        }

    return {
        "status": "issues_found",
        "total_issues": len(audit_results),
        "issues": audit_results
    }