from strands import Agent
from strands.models import BedrockModel


bedrock_model = BedrockModel(
    model_id="au.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="ap-southeast-2",
    temperature=0.2,
)


negotiation_agent = Agent(
    model=bedrock_model,
    system_prompt="""
You are Recoup's Medical Bill Negotiation Agent.

Your job is to create a professional, polite, evidence-based
medical bill review and negotiation letter.

Rules:
- Use ONLY the information provided.
- Never invent patient details, prices, laws, medical facts,
  addresses, phone numbers, emails, or dates.
- Clearly distinguish verified facts from concerns.
- Do not make accusations.
- Ask the provider to review questionable charges.
- Mention benchmark differences when available.
- Mention duplicate or calculation issues when actually found.
- Keep the tone professional and respectful.
- Make the letter ready to send to a billing department.
- If an address is not provided, DO NOT create or guess one.
"""
)


def generate_negotiation_letter(
    bill_analysis,
    benchmark_results,
    coding_audit
):

    # Remove provider address before sending the information
    # to the negotiation agent so that an address cannot be
    # accidentally invented in the letter.
    if isinstance(bill_analysis, dict):

        extracted = bill_analysis.get(
            "extracted_information"
        )

        if isinstance(extracted, dict):
            extracted.pop(
                "provider_address",
                None
            )

    prompt = f"""
Create a professional medical bill negotiation letter.

BILL INFORMATION:
{bill_analysis}

PRICE BENCHMARK RESULTS:
{benchmark_results}

CODING AUDIT:
{coding_audit}

The letter should contain:

1. Subject
2. Polite introduction
3. Bill details
4. Charges that need review
5. Price benchmark concerns
6. Coding/audit findings
7. Clear request for itemized review
8. Request for correction or adjustment if appropriate
9. Request for written response
10. Professional closing

Important:
- Do not claim that a charge is fraudulent.
- Do not claim that a benchmark proves overbilling.
- Say that the benchmark is a reference point and the charge
  should be reviewed.
- If there are no audit issues, say so.
- Use the provider name and bill number when available.
- Do not invent an address, phone number, email, or date.
- Do not include any provider address unless it was explicitly
  provided in the BILL INFORMATION.
- If contact information is not provided, simply omit it.
"""

    response = negotiation_agent(prompt)

    return str(response)
