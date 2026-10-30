import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()


def get_translation(audio_filepath):

    api_key = os.environ.get("SARVAM_API_KEY")

    if not api_key:
        raise ValueError("SARVAM_API_KEY is missing.")

    client = SarvamAI(
        api_subscription_key=api_key
    )

    with open(audio_filepath, "rb") as audio_file:

        response = client.speech_to_text.transcribe(
            file=audio_file,
            model="saaras:v4",
            mode="translate",
            language_code="unknown"
        )

    return {
        "translation": response.transcript,
        "language_code": response.language_code,
        "request_id": getattr(response, "request_id", None)
    }