from pathlib import Path
import json
import re

from strands import Agent
from strands.models import BedrockModel

from backend.benchmark import benchmark_item
from backend.coding_audit import audit_bill
from backend.negotiation import generate_negotiation_letter


bedrock_model = BedrockModel(
    model_id="au.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="ap-southeast-2",
    temperature=0.2,
)


recoup_agent = Agent(
    model=bedrock_model,
    system_prompt="""
You are Recoup, an AI medical bill advocate.

Your job is to help users understand their medical bills,
identify possible billing problems, and explain findings clearly.

Always:
- Extract only information visible in the bill.
- Never invent missing information.
- Clearly mark unreadable information.
- Identify line items and amounts.
- Identify the total amount when visible.
- Separate facts from possible billing issues.
- Be clear, simple, and professional.
"""
)


def analyze_bill_image(image_path: str):

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Bill image not found: {path}")

    with path.open("rb") as f:
        image_bytes = f.read()

    image_format = path.suffix.lower().replace(".", "")

    if image_format == "jpg":
        image_format = "jpeg"

    response = recoup_agent(
        [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": image_format,
                            "source": {
                                "bytes": image_bytes
                            }
                        }
                    },
                    {
                        "text": """
Return the extracted bill information as valid JSON.

Analyze this bill image.

Extract if visible:
- Provider name
- Patient name
- Bill number
- Bill date
- Bill time
- Every visible line item
- Quantity
- Unit price
- Total for each item
- Subtotal
- Taxes
- Grand total
- Insurance payment
- Patient responsibility
- Payment method
- Provider address

Then provide:
- Simple bill summary
- Possible duplicate charges
- Suspicious charges
- Unusual findings
- Unreadable information

Do not guess or invent anything.
If something is not visible, say "Not visible".

Return the result in JSON format.
"""
                    }
                ]
            }
        ]
    )

    print("\n========== RECOUP BILL ANALYSIS ==========\n")
    print(response)

    response_text = str(response)

    json_match = re.search(
        r"\{.*\}",
        response_text,
        re.DOTALL
    )

    if not json_match:
        print("\nNo JSON found in AI response.")
        return response

    try:
        bill_data = json.loads(json_match.group())
    except json.JSONDecodeError:
        print("\nAI response JSON could not be parsed.")
        return response

    extracted = (
        bill_data.get("extracted_information")
        or bill_data.get("extracted_bill_information")
        or bill_data.get("bill_information")
        or {}
    )

    line_items = extracted.get(
        "line_items",
        []
    )

    print("\n========== PRICE BENCHMARK ==========\n")

    benchmark_results = []

    for item in line_items:

        description = item.get("description")
        unit_price = item.get("unit_price")

        if description is None or unit_price is None:
            continue

        try:
            benchmark_result = benchmark_item(
                description,
                float(unit_price)
            )

            benchmark_results.append(
                benchmark_result
            )

            print(benchmark_result)

        except (ValueError, TypeError):
            print(
                f"Could not benchmark: {description}"
            )

    print("\n========== CODING AUDIT ==========\n")

    audit_results = audit_bill(line_items)

    print(audit_results)

    print("\n========== NEGOTIATION LETTER ==========\n")

    negotiation_letter = generate_negotiation_letter(
        bill_data,
        benchmark_results,
        audit_results
    )

    print(negotiation_letter)

    return {
        "bill_analysis": bill_data,
        "benchmark_results": benchmark_results,
        "coding_audit": audit_results,
        "negotiation_letter": negotiation_letter
    }


if __name__ == "__main__":

    bill_image = (
        Path(__file__).resolve().parent.parent
        / "uploads"
        / "pro image.jpeg"
    )

    analyze_bill_image(str(bill_image))