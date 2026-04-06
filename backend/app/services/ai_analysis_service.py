"""
AI Analysis Service using OpenAI GPT for on-demand cost sheet analysis.
Called when user clicks "Generate AI Analysis" button.
"""
import json
from app.config import get_settings


def get_ai_analysis(result_summary: dict, line_items: list, recommendations: list,
                    product_name: str, currency: str = "INR") -> dict | None:
    """
    Generate AI-powered analysis of a cost sheet using OpenAI.
    Returns structured analysis or None if API key not configured.
    """
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    except ImportError:
        return None

    # Build context for the prompt
    summary_text = json.dumps(result_summary, indent=2)
    line_items_text = json.dumps(line_items[:20], indent=2)  # Limit to avoid token overflow
    recs_text = json.dumps(recommendations[:10], indent=2)

    prompt = f"""You are an expert procurement engineer and should-cost analyst. Analyze this cost model and provide actionable insights.

## Product: {product_name}
## Currency: {currency}

## Cost Summary:
{summary_text}

## Line Items (top 20):
{line_items_text}

## Rule-Based Recommendations:
{recs_text}

Provide your analysis in this JSON structure:
{{
  "executive_summary": "2-3 sentence summary of the cost model and key findings",
  "narrative": "Detailed narrative analysis of the cost structure, identifying patterns and anomalies",
  "talking_points": ["List of 5-7 key talking points for supplier negotiation"],
  "risk_areas": ["List of 3-5 risk areas or concerns about the cost model"],
  "cost_reduction_opportunities": [
    {{"area": "name", "description": "details", "estimated_impact_pct": 0.0, "timeline": "short/medium/long"}}
  ],
  "benchmarking_notes": "How this cost structure compares to industry benchmarks",
  "next_steps": ["List of 3-5 recommended next steps"]
}}

Return ONLY valid JSON, no markdown formatting."""

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a procurement cost analysis expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        return {"error": str(e), "executive_summary": "AI analysis failed. Please check your API key and try again."}
