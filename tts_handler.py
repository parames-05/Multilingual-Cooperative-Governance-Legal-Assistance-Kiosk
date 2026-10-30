import os

from dotenv import load_dotenv
from sarvamai import SarvamAI
from sarvamai.play import save

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

TTS_MODEL = "bulbul:v3"
TTS_OUTPUT_DIR = "recordings"
TTS_OUTPUT_FILE = "response.wav"

# Languages supported by Sarvam Bulbul v3
SUPPORTED_LANGUAGES = {
    "hi-IN",
    "ta-IN",
    "te-IN",
    "en-IN",
    "bn-IN",
    "gu-IN",
    "kn-IN",
    "ml-IN",
    "mr-IN",
    "od-IN",
    "pa-IN",
}

FALLBACK_LANGUAGE = "en-IN"


# ============================================================
# GENERATE SPEECH
# ============================================================

def generate_speech(text, language_code):
    """
    Converts text to speech using Sarvam Bulbul v3.

    Args:
        text          : The clean text to speak.
        language_code : BCP-47 language code (e.g. "hi-IN").

    Returns:
        Absolute path to the saved .wav file.
    """

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    if not text or not text.strip():
        raise ValueError("No text provided for TTS.")

    api_key = os.environ.get("SARVAM_API_KEY")

    if not api_key:
        raise ValueError("SARVAM_API_KEY is missing.")

    # --------------------------------------------------------
    # Resolve language
    # --------------------------------------------------------

    if language_code not in SUPPORTED_LANGUAGES:

        print(
            f"    [TTS] Language '{language_code}' not "
            f"supported by Bulbul. Falling back to "
            f"'{FALLBACK_LANGUAGE}'."
        )

        language_code = FALLBACK_LANGUAGE

    # --------------------------------------------------------
    # Ensure output directory exists
    # --------------------------------------------------------

    os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(
        TTS_OUTPUT_DIR,
        TTS_OUTPUT_FILE
    )

    # --------------------------------------------------------
    # Call Sarvam Bulbul TTS
    # --------------------------------------------------------

    print(f"    [TTS] Model    : {TTS_MODEL}")
    print(f"    [TTS] Language : {language_code}")
    print(f"    [TTS] Text len : {len(text)} chars")

    client = SarvamAI(
        api_subscription_key=api_key
    )

    response = client.text_to_speech.convert(
        text=text,
        language_code=language_code,
        model=TTS_MODEL,
    )

    # --------------------------------------------------------
    # Save audio using Sarvam SDK
    # --------------------------------------------------------

    save(response, output_path)

    file_size = os.path.getsize(output_path)

    print(f"    [TTS] Saved    : {output_path}")
    print(f"    [TTS] Size     : {file_size} bytes")

    return os.path.abspath(output_path)
