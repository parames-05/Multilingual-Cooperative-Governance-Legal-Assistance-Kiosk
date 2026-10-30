import requests
import json
import re


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:1.7b"

MAX_RESULTS = 3
MAX_CHARS_PER_RESULT = 1800

MAX_OUTPUT_TOKENS = 200
REQUEST_TIMEOUT = 180


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing punctuation/space
    text = text.strip(" :-–—\t\n")

    return text.strip()


# ============================================================
# FIND SECTION CONTENT
# ============================================================

def extract_section(text, section_names, max_length=500):

    if not text:
        return None

    # Build patterns such as:
    #
    # Eligibility:
    # Benefits:
    # Application:
    #
    # We require the word to behave like a section heading,
    # instead of matching "benefits" anywhere in a paragraph.

    names = "|".join(
        re.escape(name)
        for name in section_names
    )

    pattern = rf"""
        (?:
            ^|
            [.!?]\s+|
            \n|
            \r
        )
        \s*
        (?:{names})
        \s*
        (?:
            :
            |
            -
            |
            –
            |
            —
        )
        \s*
        (.*?)
        (?=
            \s+(?:Eligibility|Eligible|Benefits?|Benefit|Application|How to Apply|Procedure|Coverage|Features?)
            \s*[:\-–—]
            |
            $
        )
    """

    match = re.search(
        pattern,
        text,
        re.IGNORECASE |
        re.VERBOSE |
        re.DOTALL
    )

    if not match:
        return None

    value = clean_text(
        match.group(1)
    )

    if not value:
        return None

    return value[:max_length]


# ============================================================
# EXTRACT ELIGIBILITY
# ============================================================

def extract_eligibility(text):

    result = extract_section(
        text,
        [
            "Eligibility",
            "Eligible Beneficiaries",
            "Eligible Persons",
            "Eligible Farmers",
            "Beneficiaries Eligible"
        ]
    )

    if result:
        return [result]

    return []


# ============================================================
# EXTRACT BENEFIT
# ============================================================

def extract_benefit(text):

    result = extract_section(
        text,
        [
            "Benefits",
            "Benefit",
            "Financial Assistance",
            "Assistance Provided",
            "Assistance Available"
        ]
    )

    return result


# ============================================================
# EXTRACT APPLICATION
# ============================================================

def extract_application(text):

    result = extract_section(
        text,
        [
            "Application Process",
            "How to Apply",
            "Application Procedure",
            "Procedure",
            "Application"
        ]
    )

    return result


# ============================================================
# EXTRACT SCHEME NAME
# ============================================================

def extract_scheme_name(
    text,
    metadata
):

    # --------------------------------------------------------
    # First preference:
    # category from metadata
    # --------------------------------------------------------

    category = metadata.get(
        "category",
        ""
    )

    if category:

        category_clean = category.replace(
            "_",
            " "
        ).strip()

        # Avoid generic categories becoming fake scheme names
        generic_categories = {

            "agriculture",

            "fisheries",

            "livestock",

            "social welfare",

            "health",

            "education"
        }

        if (
            category_clean.lower()
            not in generic_categories
        ):

            return category_clean.upper()


    # --------------------------------------------------------
    # Try common scheme-name patterns in document text
    # --------------------------------------------------------

    patterns = [

        # Acronym followed by expanded name
        r"\b([A-Z][A-Z0-9\-]{2,})\s*\(",

        # "Scheme Name: XYZ"
        r"(?:Scheme Name|Name of Scheme)\s*[:\-]\s*([^\n.;]{3,100})",

        # "XYZ Scheme"
        r"\b([A-Z][A-Za-z0-9\- ]{2,80}Scheme)\b"
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            name = clean_text(
                match.group(1)
            )

            if name:

                return name


    return None


# ============================================================
# CREATE DESCRIPTION
# ============================================================

def create_description(text):

    text = clean_text(text)

    if not text:
        return None

    # Keep description useful but short.
    return text[:500]


# ============================================================
# EXTRACT STRUCTURED SCHEME DATA
# ============================================================

def extract_scheme_info(
    retrieved_results
):

    schemes = []

    seen = set()


    for result in retrieved_results[:MAX_RESULTS]:

        metadata = result.get(
            "metadata",
            {}
        )

        text = result.get(
            "text",
            ""
        )

        text = clean_text(
            text[:MAX_CHARS_PER_RESULT]
        )

        if not text:
            continue


        # ----------------------------------------------------
        # Scheme name
        # ----------------------------------------------------

        scheme_name = extract_scheme_name(
            text,
            metadata
        )


        # ----------------------------------------------------
        # Description
        # ----------------------------------------------------

        description = create_description(
            text
        )


        # ----------------------------------------------------
        # Eligibility
        # ----------------------------------------------------

        eligibility = extract_eligibility(
            text
        )


        # ----------------------------------------------------
        # Benefit
        # ----------------------------------------------------

        benefit = extract_benefit(
            text
        )


        # ----------------------------------------------------
        # Application
        # ----------------------------------------------------

        application = extract_application(
            text
        )


        # ----------------------------------------------------
        # Source
        # ----------------------------------------------------

        filename = metadata.get(
            "filename",
            "Unknown document"
        )

        page = metadata.get(
            "page",
            "Unknown"
        )


        # ----------------------------------------------------
        # Deduplicate
        # ----------------------------------------------------

        dedup_key = (

            str(scheme_name).lower(),

            str(filename).lower(),

            str(page)
        )


        if dedup_key in seen:

            continue


        seen.add(
            dedup_key
        )


        # ----------------------------------------------------
        # Build scheme
        # ----------------------------------------------------

        scheme = {

            "name":
                scheme_name,

            "description":
                description,

            "eligibility":
                eligibility,

            "benefit":
                benefit,

            "application":
                application,

            "source":
                filename,

            "page":
                page
        }


        schemes.append(
            scheme
        )


    return schemes


# ============================================================
# BUILD LLM PROMPT
# ============================================================

def build_prompt(
    user_query,
    retrieved_results
):

    context_parts = []


    for i, result in enumerate(
        retrieved_results[:MAX_RESULTS],
        start=1
    ):

        metadata = result.get(
            "metadata",
            {}
        )

        filename = metadata.get(
            "filename",
            "Unknown document"
        )

        page = metadata.get(
            "page",
            "Unknown"
        )

        text = result.get(
            "text",
            ""
        )

        text = clean_text(
            text[:MAX_CHARS_PER_RESULT]
        )


        context_parts.append(
            f"""
SOURCE {i}

Document:
{filename}

Page:
{page}

Content:
{text}
"""
        )


    context = "\n".join(
        context_parts
    )


    prompt = f"""
You are a government scheme assistant.

Answer the user's question using ONLY the government
documents provided below.

Do NOT use outside knowledge.

Do NOT invent scheme names, benefits, eligibility,
amounts, dates, or application procedures.

If the documents do not contain enough information,
say so clearly.

Keep the answer short, simple and useful.

Do not explain your reasoning.

Do not produce JSON.

User question:

{user_query}


Government documents:

{context}


Give only the final answer.
"""


    return prompt


# ============================================================
# CALL OLLAMA
# ============================================================

def ask_llm(
    user_query,
    retrieved_results,
    language_code="en-IN"
):

    print("\n")
    print("=" * 60)
    print("                    LLM")
    print("=" * 60)


    print(
        "\nModel:",
        MODEL_NAME
    )


    print(
        "RAG chunks:",
        len(retrieved_results)
    )


    print(
        "Maximum output tokens:",
        MAX_OUTPUT_TOKENS
    )


    # ========================================================
    # BUILD PROMPT
    # ========================================================

    prompt = build_prompt(
        user_query,
        retrieved_results
    )


    # ========================================================
    # OLLAMA PAYLOAD
    # ========================================================

    payload = {

        "model":
            MODEL_NAME,

        "prompt":
            prompt,

        # Prevent Qwen3 from consuming the
        # output budget with internal thinking.
        "think":
            False,

        "stream":
            False,

        "options": {

            "temperature":
                0,

            "num_predict":
                MAX_OUTPUT_TOKENS
        }
    }


    print(
        "\n[LLM] Calling Ollama..."
    )


    # ========================================================
    # SEND REQUEST
    # ========================================================

    try:

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            timeout=REQUEST_TIMEOUT
        )


    except requests.exceptions.ConnectionError:

        raise RuntimeError(

            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        )


    except requests.exceptions.Timeout:

        raise RuntimeError(

            "Ollama request timed out."
        )


    except Exception as error:

        raise RuntimeError(

            f"Ollama request failed: {error}"
        )


    # ========================================================
    # HTTP STATUS
    # ========================================================

    print(
        "\n[OLLAMA HTTP STATUS]"
    )

    print(
        response.status_code
    )


    if response.status_code != 200:

        print(
            "\n[OLLAMA ERROR]"
        )

        print(
            response.text
        )

        raise RuntimeError(

            f"Ollama returned HTTP "
            f"{response.status_code}."
        )


    # ========================================================
    # PARSE RESPONSE
    # ========================================================

    try:

        data = response.json()

    except Exception as error:

        print(
            "\n[OLLAMA RAW RESPONSE]"
        )

        print(
            response.text
        )

        raise RuntimeError(

            f"Ollama returned invalid JSON: "
            f"{error}"
        )


    # ========================================================
    # RESPONSE INFO
    # ========================================================

    print(
        "\n[OLLAMA RESPONSE INFO]"
    )


    print(
        "Done:",
        data.get("done")
    )


    print(
        "Done reason:",
        data.get("done_reason")
    )


    print(
        "Thinking:",
        bool(
            data.get("thinking")
        )
    )


    raw_answer = data.get(
        "response",
        ""
    )


    print(
        "Response length:",
        len(raw_answer)
    )


    # ========================================================
    # QWEN ANSWER
    # ========================================================

    print(
        "\n[QWEN ANSWER]"
    )

    print(
        raw_answer
    )


    if not raw_answer.strip():

        print(
            "\n[OLLAMA FULL JSON]"
        )

        print(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            )
        )

        raise RuntimeError(

            "Qwen returned an empty final answer."
        )


    # ========================================================
    # STRUCTURED RAG DATA
    # ========================================================

    print(
        "\n[RAG STRUCTURED DATA]"
    )


    schemes = extract_scheme_info(
        retrieved_results
    )


    print(
        json.dumps(
            schemes,
            indent=2,
            ensure_ascii=False
        )
    )


    # ========================================================
    # SOURCE
    # ========================================================

    source = (
        "Government documents"
    )


    if retrieved_results:

        source = (

            retrieved_results[0]
            .get("metadata", {})
            .get(
                "filename",
                "Government documents"
            )
        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    result = {

        "answer":
            raw_answer.strip(),

        "schemes":
            schemes,

        "source":
            source,

        "language_code":
            language_code
    }


    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("             OLLAMA LLM TEST")
    print("=" * 60)


    test_question = (
        "I am a fisherman. "
        "What government support is available?"
    )


    print(
        "\nTest question:"
    )

    print(
        test_question
    )


    # ========================================================
    # DUMMY RAG RESULTS
    # ========================================================

    test_results = [

        {

            "score":
                0.67,

            "metadata": {

                "filename":
                    "fisheries_scheme.pdf",

                "page":
                    7,

                "sector":
                    "fisheries",

                "category":
                    "fisheries"
            },

            "text": """
Government support is available for fisheries development.

Eligibility: Fishermen and fisheries-related beneficiaries
may be covered according to the applicable scheme guidelines.

Benefits: Financial assistance may be provided for eligible
fisheries development activities.

Application Process: Applications may be submitted according
to the applicable scheme guidelines.
"""
        },


        {

            "score":
                0.63,

            "metadata": {

                "filename":
                    "fisheries_support.pdf",

                "page":
                    10,

                "sector":
                    "fisheries",

                "category":
                    "fisheries"
            },

            "text": """
Various fisheries development activities may receive
government assistance. Fishermen and fisheries-related
beneficiaries may be covered according to scheme guidelines.
"""
        },


        {

            "score":
                0.58,

            "metadata": {

                "filename":
                    "fisheries_guidelines.pdf",

                "page":
                    26,

                "sector":
                    "fisheries",

                "category":
                    "fisheries"
            },

            "text": """
The guidelines describe government support for fisheries
development and related activities.
"""
        }

    ]


    # ========================================================
    # RUN
    # ========================================================

    final_result = ask_llm(

        test_question,

        test_results,

        "en-IN"
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n")
    print("=" * 60)
    print("                 FINAL RESULT")
    print("=" * 60)


    print(
        json.dumps(
            final_result,
            indent=2,
            ensure_ascii=False
        )
    )