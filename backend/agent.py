from pathlib import Path
import json
import re

from strands import Agent
from strands.models import BedrockModel

from benchmark import benchmark_item
from coding_audit import audit_bill
from negotiation import generate_negotiation_letter


bedrock_model = BedrockModel(
    model_id="au.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="ap-southeast-2",
    temperature=0.2,
)


recoup_agent = Agent(
    model=bedrock_model,
    system_prompt="""
You are Recoup, an AI medical bill advocate.

Analyze the uploaded bill image.

Return ONLY valid JSON.

Use exactly this structure:

{
  "extracted_information": {
    "provider_name": "",
    "patient_name": "",
    "bill_number": "",
    "bill_date": "",
    "bill_time": "",
    "line_items": [],
    "subtotal": "",
    "taxes": "",
    "grand_total": "",
    "insurance_payment": "",
    "patient_responsibility": "",
    "payment_method": "",
    "provider_address": ""
  },
  "analysis": {
    "bill_summary": "",
    "possible_duplicate_charges": "",
    "suspicious_charges": [],
    "unusual_findings": [],
    "unreadable_information": ""
  }
}

Rules:
- Extract only visible information.
- Never invent information.
- If something is not visible, write "Not visible".
- line_items must contain:
  description, quantity, unit_price, total
- suspicious_charges must be an array.
- unusual_findings must be an array.
- Return JSON only.
"""
)


def analyze_bill_image(image_path: str):

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Bill image not found: {path}"
        )

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
Analyze this bill image and return the JSON structure
defined in your system instructions.

Extract all visible bill information.

Also provide:
- bill summary
- possible duplicate charges
- suspicious charges
- unusual findings
- unreadable information

Do not guess.
Return JSON only.
"""
                    }
                ]
            }
        ]
    )

    print(
        "\n========== RAW AI RESPONSE ==========\n"
    )

    print(response)

    print(
        "\n========== END RAW AI RESPONSE ==========\n"
    )

    if response is None:
        raise ValueError(
            "AI returned no response."
        )

    response_text = str(response)

    # Find JSON object
    start = response_text.find("{")
    end = response_text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "AI response did not contain valid JSON."
        )

    json_text = response_text[
        start:end + 1
    ]

    try:

        bill_data = json.loads(
            json_text
        )

    except json.JSONDecodeError as e:

        print(
            "\n========== JSON ERROR ==========\n"
        )

        print(e)

        print(
            "\n========== AI TEXT ==========\n"
        )

        print(response_text)

        raise ValueError(
            "Could not parse AI response as JSON."
        )

    extracted = bill_data.get(
        "extracted_information",
        {}
    )

    analysis = bill_data.get(
        "analysis",
        {}
    )

    if not isinstance(
        extracted,
        dict
    ):
        extracted = {}

    if not isinstance(
        analysis,
        dict
    ):
        analysis = {}

    line_items = extracted.get(
        "line_items",
        []
    )

    if not isinstance(
        line_items,
        list
    ):
        line_items = []

    print(
        "\n========== EXTRACTED INFORMATION ==========\n"
    )

    print(
        json.dumps(
            extracted,
            indent=2,
            ensure_ascii=False
        )
    )

    print(
        "\n========== ANALYSIS DATA ==========\n"
    )

    print(
        json.dumps(
            analysis,
            indent=2,
            ensure_ascii=False
        )
    )

    # PRICE BENCHMARK
    benchmark_results = []

    print(
        "\n========== PRICE BENCHMARK ==========\n"
    )

    for item in line_items:

        if not isinstance(
            item,
            dict
        ):
            continue

        description = item.get(
            "description"
        )

        unit_price = item.get(
            "unit_price"
        )

        if not description:
            continue

        if unit_price is None:
            continue

        try:

            result = benchmark_item(
                description,
                float(unit_price)
            )

            benchmark_results.append(
                result
            )

            print(result)

        except (
            ValueError,
            TypeError
        ):

            print(
                f"Could not benchmark: {description}"
            )

    # CODING AUDIT
    print(
        "\n========== CODING AUDIT ==========\n"
    )

    audit_results = audit_bill(
        line_items
    )

    print(
        json.dumps(
            audit_results,
            indent=2,
            ensure_ascii=False
        )
    )

    # NEGOTIATION LETTER
    print(
        "\n========== NEGOTIATION LETTER ==========\n"
    )

    negotiation_letter = (
        generate_negotiation_letter(
            bill_data,
            benchmark_results,
            audit_results
        )
    )

    print(
        negotiation_letter
    )

    # FINAL RESPONSE
    final_result = {
        "bill_analysis": {
            "extracted_information": extracted,
            "analysis": analysis
        },
        "benchmark_results": benchmark_results,
        "coding_audit": audit_results,
        "negotiation_letter": negotiation_letter
    }

    print(
        "\n========== FINAL RESULT ==========\n"
    )

    print(
        json.dumps(
            final_result,
            indent=2,
            ensure_ascii=False,
            default=str
        )
    )

    return final_result
