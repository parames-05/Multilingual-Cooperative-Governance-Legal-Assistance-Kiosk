from audio_handler import process_and_save_audio
from transcriber import get_translation


input_file = "recordings/test_audio.wav"
output_file = "recordings/audio.wav"


print("\n[1] Processing audio...")

with open(input_file, "rb") as f:
    raw_data = f.read()

duration, rate, channels, bit_depth = process_and_save_audio(
    raw_data,
    output_file
)

print(f"Duration: {duration:.2f} seconds")
print(f"Sample rate: {rate} Hz")
print(f"Channels: {channels}")
print(f"Bit depth: {bit_depth}-bit")

print("\n[2] Sending to Sarvam Saaras...")

result = get_translation(output_file)

print("\n[RESULT]")
print("Language:", result["language_code"])
print("Translate:", result["translation"])
print("Request ID:", result["request_id"])