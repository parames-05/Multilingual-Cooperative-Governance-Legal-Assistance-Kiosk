import io
import os
import wave

from pydub import AudioSegment


TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1
TARGET_SAMPLE_WIDTH = 2
MAX_DURATION = 30


def process_and_save_audio(raw_data, output_filepath):

    if not raw_data:
        raise ValueError("No audio data received.")

    folder = os.path.dirname(output_filepath)

    if folder:
        os.makedirs(folder, exist_ok=True)

    # Check whether the ESP32 sent a WAV file
    is_wav = (
        len(raw_data) >= 12
        and raw_data[:4] == b"RIFF"
        and raw_data[8:12] == b"WAVE"
    )

    # ==================================================
    # WAV INPUT
    # ==================================================

    if is_wav:

        try:
            with wave.open(io.BytesIO(raw_data), "rb") as wf:
                original_rate = wf.getframerate()
                original_channels = wf.getnchannels()
                original_width = wf.getsampwidth()
                frames = wf.getnframes()

                if original_rate <= 0:
                    raise ValueError("Invalid WAV sample rate.")

                original_duration = frames / float(original_rate)

        except wave.Error as e:
            raise ValueError(f"Invalid WAV file: {e}")

        print("\n[INPUT WAV]")
        print(f"Sample rate : {original_rate} Hz")
        print(f"Channels    : {original_channels}")
        print(f"Bit depth   : {original_width * 8}-bit")
        print(f"Duration    : {original_duration:.2f} sec")

        if original_duration > MAX_DURATION:
            raise ValueError(
                f"Recording is {original_duration:.2f} seconds. "
                f"Maximum is {MAX_DURATION} seconds."
            )

        try:
            audio = AudioSegment.from_wav(
                io.BytesIO(raw_data)
            )
        except Exception as e:
            raise ValueError(
                f"Could not read WAV audio: {e}"
            )

        print("\n[NORMALIZING AUDIO]")

        audio = audio.set_frame_rate(TARGET_SAMPLE_RATE)
        audio = audio.set_channels(TARGET_CHANNELS)
        audio = audio.set_sample_width(TARGET_SAMPLE_WIDTH)

    # ==================================================
    # RAW PCM INPUT
    # ==================================================

    else:

        print("\n[RAW PCM INPUT]")

        if len(raw_data) % 2 != 0:
            raise ValueError(
                "Invalid raw PCM data. "
                "16-bit PCM must contain an even number of bytes."
            )

        duration = len(raw_data) / (
            TARGET_SAMPLE_RATE
            * TARGET_CHANNELS
            * TARGET_SAMPLE_WIDTH
        )

        if duration > MAX_DURATION:
            raise ValueError(
                f"Recording is {duration:.2f} seconds. "
                f"Maximum is {MAX_DURATION} seconds."
            )

        audio = AudioSegment(
            data=raw_data,
            sample_width=TARGET_SAMPLE_WIDTH,
            frame_rate=TARGET_SAMPLE_RATE,
            channels=TARGET_CHANNELS
        )

    # ==================================================
    # FINAL DURATION CHECK
    # ==================================================

    final_duration = len(audio) / 1000.0

    if final_duration > MAX_DURATION:
        raise ValueError(
            f"Final recording is {final_duration:.2f} seconds. "
            f"Maximum is {MAX_DURATION} seconds."
        )

    # ==================================================
    # SAVE WAV
    # ==================================================

    try:
        audio.export(
            output_filepath,
            format="wav"
        )
    except Exception as e:
        raise ValueError(
            f"Could not save WAV file: {e}"
        )

    # ==================================================
    # FINAL VALIDATION
    # ==================================================

    try:
        with wave.open(output_filepath, "rb") as wf:

            final_rate = wf.getframerate()
            final_channels = wf.getnchannels()
            final_width = wf.getsampwidth()
            final_frames = wf.getnframes()

            final_duration = (
                final_frames / float(final_rate)
            )

            if final_rate != TARGET_SAMPLE_RATE:
                raise ValueError(
                    f"Final WAV sample rate is "
                    f"{final_rate} Hz. Expected 16000 Hz."
                )

            if final_channels != TARGET_CHANNELS:
                raise ValueError(
                    f"Final WAV has {final_channels} channels. "
                    f"Expected mono."
                )

            if final_width != TARGET_SAMPLE_WIDTH:
                raise ValueError(
                    f"Final WAV is {final_width * 8}-bit. "
                    f"Expected 16-bit."
                )

            if final_duration > MAX_DURATION:
                raise ValueError(
                    f"Final WAV is {final_duration:.2f} seconds. "
                    f"Maximum is 30 seconds."
                )

    except wave.Error as e:
        raise ValueError(
            f"Generated WAV file is invalid: {e}"
        )

    print("\n[FINAL WAV]")
    print(f"Sample rate : {final_rate} Hz")
    print(f"Channels    : {final_channels}")
    print(f"Bit depth   : {final_width * 8}-bit")
    print(f"Duration    : {final_duration:.2f} sec")
    print(f"Saved       : {output_filepath}")

    return (
        final_duration,
        final_rate,
        final_channels,
        final_width * 8
    )