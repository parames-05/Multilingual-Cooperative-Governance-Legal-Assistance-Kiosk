import requests

# The URL where your Flask server is listening
url = "http://127.0.0.1:5000/upload"
audio_file = "recordings/test_audio.wav"
output_file = "recordings/esp32_response.wav"

print(f"Reading {audio_file}...")
with open(audio_file, "rb") as f:
    raw_audio = f.read()

print("Sending HTTP POST to main.py...")
# Sending the raw binary data exactly how the C++ code will do it
response = requests.post(url, data=raw_audio)

print(f"\n[SERVER RESPONSE]")
print(f"Status code: {response.status_code}")

if response.status_code == 200:

    # Server now returns a .wav file instead of JSON
    with open(output_file, "wb") as f:
        f.write(response.content)

    print(f"WAV file saved: {output_file}")
    print(f"Size: {len(response.content)} bytes")
    print("\n.wav sent to ESP32 successfully!")

else:
    # Error responses are still JSON
    print(response.json())