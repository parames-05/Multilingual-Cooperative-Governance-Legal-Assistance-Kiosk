import re


# ============================================================
# CONFIGURATION
# ============================================================

# Sarvam Bulbul TTS character limit per request.
# Set high to get maximum coverage; Bulbul will
# truncate if it exceeds its own internal limit.
MAX_TTS_CHARS = 3000


# ============================================================
# CLEAN FOR SPEECH
# ============================================================

def clean_for_speech(text):
    """
    Remove markdown, extra whitespace, and anything
    that would sound unnatural when spoken aloud.
    """

    if not text:
        return ""

    # Remove markdown bold / italic markers
    text = re.sub(r"[*_]{1,3}", "", text)

    # Remove markdown headers
    text = re.sub(r"#+\s*", "", text)

    # Remove markdown bullet points
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.MULTILINE)

    # Remove numbered list prefixes like "1. " or "1) "
    text = re.sub(r"^\s*\d+[.)]\s*", "", text, flags=re.MULTILINE)

    # Collapse newlines into spaces
    text = re.sub(r"[\r\n]+", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# FORMAT LLM RESULT TO SPEECH TEXT
# ============================================================

def format_for_speech(llm_result):
    """
    Takes the dictionary returned by scheme_logic.process_scheme_query()
    and produces a single continuous sentence for TTS.

    Expected input keys:
        - response   (str) : The LLM plain-text answer
        - schemes    (list): Structured scheme data from RAG
        - source     (str) : Source document name

    Returns:
        A single clean string ready for Sarvam Bulbul TTS.
    """

    parts = []

    # ----------------------------------------------------------
    # 1. Main LLM answer (highest priority)
    # ----------------------------------------------------------

    answer = clean_for_speech(
        llm_result.get("response", "")
    )

    if answer:
        parts.append(answer)

    # ----------------------------------------------------------
    # 2. Scheme details from structured RAG extraction
    #    Only add if the LLM answer is too short or empty.
    # ----------------------------------------------------------

    schemes = llm_result.get("schemes", [])

    if schemes:

        for scheme in schemes[:2]:

            name = scheme.get("name")

            if name:
                parts.append(
                    f"The scheme is called {name}."
                )

            benefit = scheme.get("benefit")

            if benefit:
                parts.append(
                    f"The benefit is {clean_for_speech(benefit)}."
                )

            eligibility = scheme.get("eligibility", [])

            if eligibility:
                eligibility_text = clean_for_speech(
                    eligibility[0]
                    if isinstance(eligibility, list)
                    else str(eligibility)
                )

                if eligibility_text:
                    parts.append(
                        f"Eligibility: {eligibility_text}."
                    )

            application = scheme.get("application")

            if application:
                parts.append(
                    f"To apply: {clean_for_speech(application)}."
                )

    # ----------------------------------------------------------
    # 3. Fallback if nothing was produced
    # ----------------------------------------------------------

    if not parts:
        return (
            "I could not find relevant government "
            "scheme information for your question."
        )

    # ----------------------------------------------------------
    # 4. Join and truncate
    # ----------------------------------------------------------

    full_text = " ".join(parts)

    # Remove double periods
    full_text = full_text.replace("..", ".")

    # Truncate at the last full sentence within the limit
    if len(full_text) > MAX_TTS_CHARS:

        truncated = full_text[:MAX_TTS_CHARS]

        last_period = truncated.rfind(".")

        if last_period > 50:
            full_text = truncated[:last_period + 1]
        else:
            full_text = truncated.rstrip() + "."

    return full_text
