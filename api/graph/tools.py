from langchain_core.tools import tool

@tool
def get_bias_definitions() -> str:
    """Retrieve industry standard definitions and guidelines for demographic biases, including hiring guidelines."""
    return """
    Here are industry standards for spotting and mitigating bias:
    1. Gender Bias: Prefer gender-neutral language. Watch out for coded terms (e.g., 'aggressive', 'bossy' vs 'assertive', 'leader').
    2. Age Bias: Avoid terms like 'digital native', 'energetic', 'gravitas', or 'mature'. Focus on specific skills.
    3. Racial/Ethnic Bias: Focus purely on objective criteria and merit. Avoid unnecessary mentions of names, cultural backgrounds, or accents.
    4. Religious Bias: Avoid calendar conflicts for interviews, and guarantee accommodation policies.
    5. Disability Bias: Focus on essential job functions with or without reasonable accommodations.
    """

@tool
def get_common_biased_phrases() -> dict:
    """Get common biased phrases in professional documents and their neutral alternatives."""
    return {
        "he/she": "they",
        "chairman": "chairperson / chair",
        "manpower": "workforce / personnel",
        "digital native": "proficient in modern technology",
        "young and hungry": "highly motivated and career-driven",
        "cultural fit": "values alignment / culture add",
        "native English speaker": "excellent written and verbal communication skills",
    }

# Export the tools
ATHENA_TOOLS = [get_bias_definitions, get_common_biased_phrases]
