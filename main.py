from flask import Flask, request, jsonify, send_file

from audio_handler import process_and_save_audio
from transcriber import get_translation
from scheme_logic import process_scheme_query
from response_formatter import format_for_speech
from tts_handler import generate_speech


app = Flask(__name__)

AUDIO_FILE = "recordings/audio.wav"


@app.route("/upload", methods=["POST"])
def upload_audio():

    try:
        print("\n========================================")
        print("        NEW AUDIO REQUEST")
        print("========================================")

        # ----------------------------------------
        # 1. Receive raw audio from ESP32
        # ----------------------------------------

        raw_audio = request.get_data()

        if not raw_audio:
            return jsonify({
                "success": False,
                "error": "No audio data received."
            }), 400

        print(f"[1] Received {len(raw_audio)} bytes")


        # ----------------------------------------
        # 2. Process and save audio
        # ----------------------------------------

        print("[2] Processing audio...")

        duration, rate, channels, bit_depth = process_and_save_audio(
            raw_audio,
            AUDIO_FILE
        )

        print(f"    Duration   : {duration:.2f} seconds")
        print(f"    Sample rate: {rate} Hz")
        print(f"    Channels   : {channels}")
        print(f"    Bit depth  : {bit_depth}-bit")


        # ----------------------------------------
        # 3. Send audio to Sarvam
        # ----------------------------------------

        print("\n[3] Sending to Sarvam Saaras...")

        speech_result = get_translation(AUDIO_FILE)

        language_code = speech_result["language_code"]
        translation = speech_result["translation"]
        request_id = speech_result["request_id"]

        print(f"    Language   : {language_code}")
        print(f"    Translation: {translation}")
        print(f"    Request ID : {request_id}")


        # ----------------------------------------
        # 4. Send translated query to scheme logic
        # ----------------------------------------

        print("\n[4] Searching government schemes...")

        scheme_result = process_scheme_query(
            translation,
            language_code
        )


        # ----------------------------------------
        # 5. Format LLM response for speech
        # ----------------------------------------

        print("\n[5] Formatting response for TTS...")

        speech_text = format_for_speech(scheme_result)

        print(f"    Speech text: {speech_text[:100]}...")


        # ----------------------------------------
        # 6. Convert text to speech (Sarvam Bulbul)
        # ----------------------------------------

        print("\n[6] Generating speech audio...")

        wav_path = generate_speech(
            speech_text,
            "en-IN"
        )

        print("    TTS complete!")


        # ----------------------------------------
        # 7. Send .wav file back to ESP32
        # ----------------------------------------

        print("\n[7] Sending .wav to ESP32...")
        print("========================================\n")

        return send_file(
            wav_path,
            mimetype="audio/wav",
            as_attachment=True,
            download_name="response.wav"
        )


    except Exception as e:

        print("\n[ERROR]")
        print(str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":

    print("""
========================================
   MULTILINGUAL GOVERNMENT ASSISTANT
========================================

Server running at:

http://127.0.0.1:5000

Waiting for ESP32 / simulator...
""")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )