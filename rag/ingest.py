import os
import json
import re

from pypdf import PdfReader
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KNOWLEDGE_BASE = os.path.join(
    BASE_DIR,
    "knowledge_base"
)

OUTPUT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "processed_chunks.json"
)


# Number of characters in each chunk
CHUNK_SIZE = 1200

# Overlap between chunks
CHUNK_OVERLAP = 200


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if not text:
        return ""

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces at beginning/end of lines
    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    text = "\n".join(lines)

    return text.strip()


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf(filepath):

    pages = []

    try:

        reader = PdfReader(filepath)

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            try:

                text = page.extract_text()

            except Exception:

                text = ""

            text = clean_text(text)

            if text:

                pages.append({
                    "page": page_number,
                    "text": text
                })

    except Exception as e:

        print(
            f"[ERROR] PDF failed: {filepath}"
        )

        print(
            f"        {e}"
        )

        return []

    return pages


# ============================================================
# HTML EXTRACTION
# ============================================================

def extract_html(filepath):

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            html = file.read()

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # Remove unnecessary web elements
        for element in soup([
            "script",
            "style",
            "noscript"
        ]):

            element.decompose()

        text = soup.get_text(
            separator="\n"
        )

        text = clean_text(text)

        if text:

            return [{
                "page": 1,
                "text": text
            }]

    except Exception as e:

        print(
            f"[ERROR] HTML failed: {filepath}"
        )

        print(
            f"        {e}"
        )

    return []


# ============================================================
# DOCUMENT EXTRACTION
# ============================================================

def extract_document(filepath):

    extension = os.path.splitext(
        filepath
    )[1].lower()

    if extension == ".pdf":

        return extract_pdf(filepath)

    if extension == ".html":

        return extract_html(filepath)

    return []


# ============================================================
# METADATA
# ============================================================

def get_metadata(filepath):

    relative_path = os.path.relpath(
        filepath,
        KNOWLEDGE_BASE
    )

    parts = relative_path.split(
        os.sep
    )

    filename = os.path.basename(
        filepath
    )

    # Default values
    sector = "unknown"
    category = "unknown"

    # Example:
    #
    # 02_agriculture/
    # pm_kisan/
    # RevisedFAQ.pdf
    #
    # parts =
    # ["02_agriculture", "pm_kisan", "RevisedFAQ.pdf"]

    if len(parts) >= 2:

        sector = parts[0]

        category = parts[1]

    elif len(parts) == 1:

        sector = parts[0]

    return {
        "sector": sector,
        "category": category,
        "filename": filename,
        "filepath": relative_path
    }


# ============================================================
# CHUNKING
# ============================================================

def create_chunks(text):

    if not text:

        return []

    chunks = []

    start = 0

    text_length = len(text)

    while start < text_length:

        end = start + CHUNK_SIZE

        chunk = text[start:end]

        # Try to end the chunk at a sentence boundary
        if end < text_length:

            last_period = chunk.rfind(".")

            last_question = chunk.rfind("?")

            last_newline = chunk.rfind("\n")

            boundary = max(
                last_period,
                last_question,
                last_newline
            )

            if boundary > CHUNK_SIZE * 0.6:

                end = start + boundary + 1

                chunk = text[start:end]

        chunk = chunk.strip()

        if chunk:

            chunks.append(chunk)

        # Move forward with overlap
        start = end - CHUNK_OVERLAP

        if start < 0:

            start = 0

        # Safety against infinite loops
        if end >= text_length:

            break

    return chunks


# ============================================================
# FIND DOCUMENTS
# ============================================================

def find_documents():

    documents = []

    for root, dirs, files in os.walk(
        KNOWLEDGE_BASE
    ):

        for filename in files:

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension in [
                ".pdf",
                ".html"
            ]:

                filepath = os.path.join(
                    root,
                    filename
                )

                documents.append(
                    filepath
                )

    return documents


# ============================================================
# MAIN INGESTION
# ============================================================

def ingest():

    print("\n")
    print("=" * 60)
    print("           GOVERNMENT SCHEME INGESTION")
    print("=" * 60)

    print(
        "\nKnowledge base:",
        KNOWLEDGE_BASE
    )

    # --------------------------------------------------------
    # FIND DOCUMENTS
    # --------------------------------------------------------

    documents = find_documents()

    print(
        "\nDocuments found:",
        len(documents)
    )

    if not documents:

        print(
            "\n[ERROR] No PDF or HTML documents found."
        )

        return


    all_chunks = []

    successful_documents = 0

    failed_documents = 0


    # --------------------------------------------------------
    # PROCESS EACH DOCUMENT
    # --------------------------------------------------------

    for index, filepath in enumerate(
        documents,
        start=1
    ):

        filename = os.path.basename(
            filepath
        )

        print(
            f"\n[{index}/{len(documents)}] {filename}"
        )

        pages = extract_document(
            filepath
        )

        if not pages:

            print(
                "   [FAILED] No text extracted"
            )

            failed_documents += 1

            continue


        metadata = get_metadata(
            filepath
        )

        document_chunks = 0


        # ----------------------------------------------------
        # PROCESS EACH PAGE
        # ----------------------------------------------------

        for page_data in pages:

            page_number = page_data["page"]

            text = page_data["text"]

            chunks = create_chunks(
                text
            )


            # ------------------------------------------------
            # CREATE CHUNK RECORDS
            # ------------------------------------------------

            for chunk_index, chunk in enumerate(
                chunks,
                start=1
            ):

                record = {

                    "id": len(all_chunks),

                    "text": chunk,

                    "metadata": {

                        "sector": metadata["sector"],

                        "category": metadata["category"],

                        "filename": metadata["filename"],

                        "filepath": metadata["filepath"],

                        "page": page_number,

                        "chunk": chunk_index

                    }

                }

                all_chunks.append(
                    record
                )

                document_chunks += 1


        if document_chunks > 0:

            successful_documents += 1

            print(
                "   [OK]",
                document_chunks,
                "chunks"
            )

        else:

            failed_documents += 1

            print(
                "   [FAILED] No usable chunks"
            )


    # --------------------------------------------------------
    # SAVE PROCESSED DATA
    # --------------------------------------------------------

    print(
        "\nSaving processed chunks..."
    )

    try:

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                all_chunks,
                file,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:

        print(
            "\n[ERROR] Could not save output:"
        )

        print(e)

        return


    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("             INGESTION COMPLETE")
    print("=" * 60)

    print(
        "\nDocuments found    :",
        len(documents)
    )

    print(
        "Documents processed:",
        successful_documents
    )

    print(
        "Documents failed   :",
        failed_documents
    )

    print(
        "Total chunks       :",
        len(all_chunks)
    )

    print(
        "\nOutput:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nNext step:"
    )

    print(
        "Create embeddings → FAISS vector database"
    )

    print(
        "\n" + "=" * 60
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    ingest()