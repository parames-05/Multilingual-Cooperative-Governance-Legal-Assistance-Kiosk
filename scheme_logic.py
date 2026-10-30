import json

from rag.retriever import (
    load_database,
    load_model,
    search
)

from llm.llm_handler import ask_llm


# ============================================================
# CONFIGURATION
# ============================================================

TOP_K = 3


# ============================================================
# LOAD RAG SYSTEM
# ============================================================

print("\n")
print("[SCHEME LOGIC] Loading RAG system...")

try:

    faiss_index, chunks = load_database()

    embedding_model = load_model()

    print(
        "[SCHEME LOGIC] RAG system ready."
    )

except Exception as error:

    print(
        "\n[SCHEME LOGIC ERROR]"
    )

    print(error)

    faiss_index = None

    chunks = []

    embedding_model = None


# ============================================================
# MAIN SCHEME PROCESSING FUNCTION
# ============================================================

def process_scheme_query(
    transcript,
    language_code
):

    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    if not transcript:

        raise ValueError(
            "No translated query received."
        )


    if not language_code:

        language_code = "unknown"


    # ========================================================
    # DISPLAY QUERY
    # ========================================================

    print("\n")
    print("=" * 60)
    print("                 SCHEME LOGIC")
    print("=" * 60)

    print(
        "\nUser query:",
        transcript
    )

    print(
        "Original language:",
        language_code
    )


    # ========================================================
    # CHECK RAG
    # ========================================================

    if faiss_index is None:

        raise RuntimeError(
            "RAG system is not loaded."
        )


    # ========================================================
    # RAG SEARCH
    # ========================================================

    print(
        "\n[RAG] Searching government documents..."
    )


    retrieved_results = search(

        transcript,

        faiss_index,

        chunks,

        embedding_model,

        top_k=TOP_K
    )


    print(
        "[RAG] Results found:",
        len(retrieved_results)
    )


    # ========================================================
    # DISPLAY RETRIEVED RESULTS
    # ========================================================

    for number, retrieved in enumerate(
        retrieved_results,
        start=1
    ):

        metadata = retrieved.get(
            "metadata",
            {}
        )


        print(
            f"\n[RAG RESULT {number}]"
        )


        print(
            "Similarity:",
            f"{retrieved['score']:.4f}"
        )


        print(
            "Sector:",
            metadata.get(
                "sector",
                "Unknown"
            )
        )


        print(
            "Category:",
            metadata.get(
                "category",
                "Unknown"
            )
        )


        print(
            "Source:",
            metadata.get(
                "filename",
                "Unknown"
            )
        )


        print(
            "Page:",
            metadata.get(
                "page",
                "Unknown"
            )
        )


    # ========================================================
    # NO RESULTS
    # ========================================================

    if not retrieved_results:

        response_text = (
            "I could not find relevant government "
            "scheme information for your question."
        )


        return {

            "response":
                response_text,

            "language_code":
                language_code,

            "schemes":
                [],

            "display_text":
                response_text,

            "speech_text":
                response_text,

            "source":
                None,

            "retrieved_chunks":
                0
        }


    # ========================================================
    # SEND RAG RESULTS TO LLM
    # ========================================================

    print(
        "\n[LLM] Sending top",
        TOP_K,
        "retrieved chunks to Qwen3..."
    )


    llm_result = ask_llm(

        transcript,

        retrieved_results[:TOP_K],

        language_code
    )


    # ========================================================
    # READ LLM RESULT
    # ========================================================

    print(
        "\n[LLM RESULT]"
    )


    print(
        json.dumps(
            llm_result,
            indent=2,
            ensure_ascii=False
        )
    )


    # ========================================================
    # EXTRACT ANSWER
    # ========================================================

    answer = llm_result.get(

        "answer",

        "No answer was generated."
    )


    # ========================================================
    # EXTRACT STRUCTURED SCHEMES
    # ========================================================

    schemes = llm_result.get(

        "schemes",

        []
    )


    # ========================================================
    # EXTRACT SOURCE
    # ========================================================

    source = llm_result.get(

        "source",

        "Government documents"
    )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    final_response = {

        "response":
            answer,

        "language_code":
            language_code,

        "schemes":
            schemes,

        "display_text":
            answer,

        "speech_text":
            answer,

        "source":
            source,

        "retrieved_chunks":
            len(retrieved_results)
    }


    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n[SCHEME LOGIC] Processing complete."
    )

    print("=" * 60)


    return final_response


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("       GOVERNMENT SCHEME LOGIC TEST")
    print("=" * 60)


    # --------------------------------------------------------
    # Get user query
    # --------------------------------------------------------

    user_query = input(
        "\nEnter a government scheme question: "
    )


    # --------------------------------------------------------
    # Process query
    # --------------------------------------------------------

    final_response = process_scheme_query(

        user_query,

        "en-IN"
    )


    # --------------------------------------------------------
    # Print final result
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("                 FINAL RESULT")
    print("=" * 60)


    print(
        json.dumps(
            final_response,
            indent=2,
            ensure_ascii=False
        )
    )