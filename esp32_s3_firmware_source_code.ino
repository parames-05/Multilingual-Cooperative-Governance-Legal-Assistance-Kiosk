#include <Arduino.h>
#include "driver/i2s.h"
#include "FS.h"
#include "SD.h"
#include "SPI.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ============================================================
// NETWORK & ENDPOINT CONFIGURATION
// ============================================================
const char* WIFI_SSID     = "YOUR_WIFI_SSID";       // ← Replace with your WiFi name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";    // ← Replace with your WiFi password

// Ensure laptop running Flask shares this subnet
const char* SERVER_URL    = "http://<SERVER_IP>:5000/upload";  // ← Replace with Flask server IP

// ============================================================
// LCD BACKPACK CONFIGURATION
// ============================================================
// Use 0x3F or 0x27 depending on your PCF8574 chip
LiquidCrystal_I2C lcd(0x3F, 16, 2);

// ============================================================
// HARDWARE PIN ASSIGNMENTS
// ============================================================
// INMP441 Microphone (I2S_NUM_0 - RX)
#define MIC_SCK     32
#define MIC_WS      25
#define MIC_SD      33

// MAX98357A Amplifier (I2S_NUM_1 - TX)
#define AMP_BCLK    26
#define AMP_LRC     27
#define AMP_DOUT    22

// Trigger Button (Active LOW with internal pullup)
#define BUTTON_PIN  14

// MicroSD SPI Bus (VSPI)
#define SD_CS       5
#define SD_SCK      18
#define SD_MISO     19
#define SD_MOSI     23

// I2C Bus for LCD (Custom GPIO matrix routing)
#define I2C_SDA     21
#define I2C_SCL     15

// ============================================================
// AUDIO PARAMETERS
// ============================================================
#define SAMPLE_RATE     16000
#define BUFFER_LEN      512
#define BITS_PER_SAMPLE 16
#define CHANNELS        1

#define RECORD_FILE "/voice_record.wav"
#define REPLY_FILE  "/reply.wav"

// ============================================================
// FINITE STATE MACHINE & SYSTEM VARS
// ============================================================
enum SystemState {
    STATE_IDLE,
    STATE_RECORDING,
    STATE_UPLOAD
};

SystemState currentState = STATE_IDLE;
int lastButtonState = HIGH;
File audioFile;
uint32_t totalAudioBytes = 0;
float dc_filter = 0;

// ============================================================
// FUNCTION DECLARATIONS
// ============================================================
void setupI2S_Mic();
void setupI2S_Amp();
void connectWiFi();
void startRecording();
void recordAudio();
void finishRecording();
void uploadAudio();
void playWavFile(const char* filePath);
void writeWavHeader(File &file, uint32_t sampleRate, uint16_t bitsPerSample, uint16_t channels, uint32_t dataSize);
void updateWavHeader(File &file, uint32_t dataSize);
bool sendAndReceiveWav(const char* inPath, const char* outPath);
void displayOnLCD(const String &line1, const String &line2);

// ============================================================
// SETUP
// ============================================================
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n========================================");
    Serial.println("   MULTILINGUAL GOVERNMENT ASSISTANT");
    Serial.println("========================================");

    pinMode(BUTTON_PIN, INPUT_PULLUP);

    // 1. Robust LCD Initialisation Sequence
    Wire.begin(I2C_SDA, I2C_SCL, 100000);
    delay(100); // Allow HD44780 power-on reset circuitry to stabilize

    lcd.init();
    delay(20);

    // Re-assert custom I2C pins after library internal Wire calls
    Wire.begin(I2C_SDA, I2C_SCL, 100000);
    lcd.backlight();
    lcd.clear();
    delay(50);

    displayOnLCD("Starting...", "Please wait");

    // 2. Wi-Fi Connection
    connectWiFi();

    // 3. MicroSD SPI Bus Initialisation
    Serial.println("[SD] Initializing...");
    SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
    if (!SD.begin(SD_CS)) {
        Serial.println("[ERROR] SD card initialization failed!");
        displayOnLCD("SD Card Error!", "Check wiring");
        while (true) delay(100);
    }
    Serial.println("[SD] Card initialized successfully.");

    // 4. Configure Audio Hardware Pipelines
    setupI2S_Mic();
    setupI2S_Amp();

    displayOnLCD("Hold to Speak", "System Ready");
    Serial.println("SYSTEM READY: Hold GPIO 14 button and speak.");
}

// ============================================================
// MAIN LOOP
// ============================================================
void loop() {
    int buttonState = digitalRead(BUTTON_PIN);

    // Button Pressed (Trigger Recording)
    if (lastButtonState == HIGH && buttonState == LOW && currentState == STATE_IDLE) {
        startRecording();
    }

    // Active Recording
    if (currentState == STATE_RECORDING && buttonState == LOW) {
        recordAudio();
    }

    // Button Released (Finalize & Transition to Upload)
    if (lastButtonState == LOW && buttonState == HIGH && currentState == STATE_RECORDING) {
        finishRecording();
    }

    lastButtonState = buttonState;

    // Send Audio to Server and Stream Back Reply
    if (currentState == STATE_UPLOAD) {
        uploadAudio();
    }
}

// ============================================================
// WI-FI INITIALIZATION
// ============================================================
void connectWiFi() {
    Serial.println("[WIFI] Connecting...");
    displayOnLCD("Connecting WiFi", "Please wait...");

    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int dots = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        lcd.setCursor(dots % 16, 1);
        lcd.print(".");
        dots++;

        if (dots >= 60) {
            Serial.println("\n[ERROR] WiFi connection failed!");
            displayOnLCD("WiFi Failed!", "Check password");
            while (true) delay(100);
        }
    }

    Serial.println("\n[WIFI] Connected! IP: " + WiFi.localIP().toString());
    displayOnLCD("WiFi Connected", WiFi.localIP().toString());
    delay(1200);
}

// ============================================================
// I2S HARDWARE DRIVERS (MIC & AMP)
// ============================================================
void setupI2S_Mic() {
    i2s_config_t mic_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = BUFFER_LEN,
        .use_apll = false
    };

    i2s_pin_config_t mic_pins = {
        .mck_io_num = I2S_PIN_NO_CHANGE,
        .bck_io_num = MIC_SCK,
        .ws_io_num = MIC_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = MIC_SD
    };

    i2s_driver_install(I2S_NUM_0, &mic_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &mic_pins);
    i2s_stop(I2S_NUM_0);
}

void setupI2S_Amp() {
    i2s_config_t amp_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 16,        // Expanded buffer pool prevents SD SPI read underruns
        .dma_buf_len = 1024,        // Increased chunk size guarantees zero audio crackle
        .use_apll = false
    };

    i2s_pin_config_t amp_pins = {
        .mck_io_num = I2S_PIN_NO_CHANGE,
        .bck_io_num = AMP_BCLK,
        .ws_io_num = AMP_LRC,
        .data_out_num = AMP_DOUT,
        .data_in_num = I2S_PIN_NO_CHANGE
    };

    i2s_driver_install(I2S_NUM_1, &amp_config, 0, NULL);
    i2s_set_pin(I2S_NUM_1, &amp_pins);
    i2s_stop(I2S_NUM_1);
}

// ============================================================
// AUDIO RECORDING
// ============================================================
void startRecording() {
    i2s_stop(I2S_NUM_1); // Mute amplifier to avoid acoustic feedback
    displayOnLCD("Listening...", "Keep holding");

    audioFile = SD.open(RECORD_FILE, FILE_WRITE);
    if (!audioFile) {
        displayOnLCD("SD Write Error!", "Cannot open file");
        return;
    }

    writeWavHeader(audioFile, SAMPLE_RATE, BITS_PER_SAMPLE, CHANNELS, 0);
    totalAudioBytes = 0;
    dc_filter = 0;

    i2s_start(I2S_NUM_0);
    currentState = STATE_RECORDING;
}

void recordAudio() {
    int32_t rx_buffer[BUFFER_LEN];
    int16_t pcm16_buffer[BUFFER_LEN];
    size_t bytes_read = 0;

    i2s_read(I2S_NUM_0, rx_buffer, sizeof(rx_buffer), &bytes_read, portMAX_DELAY);
    int samples = bytes_read / sizeof(int32_t);

    for (int i = 0; i < samples; i++) {
        int32_t raw = rx_buffer[i] >> 14;
        
        // High-pass filter removes DC bias
        dc_filter = (0.995 * dc_filter) + (0.005 * raw);
        int32_t ac = (raw - (int32_t)dc_filter) * 4;

        if (ac > 32767)  ac = 32767;
        if (ac < -32768) ac = -32768;
        pcm16_buffer[i] = (int16_t)ac;
    }

    size_t bytesToWrite = samples * sizeof(int16_t);
    audioFile.write((const uint8_t*)pcm16_buffer, bytesToWrite);
    totalAudioBytes += bytesToWrite;
}

void finishRecording() {
    i2s_stop(I2S_NUM_0);

    updateWavHeader(audioFile, totalAudioBytes);
    audioFile.close();

    displayOnLCD("Processing...", "Sending to Server");
    currentState = STATE_UPLOAD;
}

// ============================================================
// HTTP PIPELINE: POST WAV & DOWNLOAD TTS REPLY
// ============================================================
void uploadAudio() {
    if (WiFi.status() != WL_CONNECTED) {
        displayOnLCD("WiFi Error!", "Reconnect");
        currentState = STATE_IDLE;
        return;
    }

    displayOnLCD("Server Thinking", "Receiving Audio");
    bool success = sendAndReceiveWav(RECORD_FILE, REPLY_FILE);

    if (success) {
        displayOnLCD("Speaking...", "Playing reply");
        playWavFile(REPLY_FILE);
    } else {
        displayOnLCD("Error!", "No audio back");
        delay(2000);
    }

    displayOnLCD("Hold to Speak", "System Ready");
    currentState = STATE_IDLE;
}

bool sendAndReceiveWav(const char* inPath, const char* outPath) {
    File uploadFile = SD.open(inPath, FILE_READ);
    if (!uploadFile) {
        Serial.println("[ERROR] Cannot open recorded file for upload.");
        return false;
    }

    WiFiClient client;
    HTTPClient http;

    http.setTimeout(30000); // 30-second timeout allows server AI models to run

    if (!http.begin(client, SERVER_URL)) {
        uploadFile.close();
        return false;
    }

    http.addHeader("Content-Type", "audio/wav");
    int httpResponseCode = http.sendRequest("POST", &uploadFile, uploadFile.size());
    uploadFile.close();

    Serial.printf("[HTTP] Status: %d\n", httpResponseCode);

    if (httpResponseCode == 200) {
        if (SD.exists(outPath)) SD.remove(outPath);
        File replyFile = SD.open(outPath, FILE_WRITE);
        if (!replyFile) {
            Serial.println("[ERROR] Failed to create reply.wav on SD!");
            http.end();
            return false;
        }

        WiFiClient* stream = http.getStreamPtr();
        uint8_t buffer[512];
        size_t totalReceived = 0;

        while (http.connected() || stream->available()) {
            if (stream->available()) {
                int bytesRead = stream->read(buffer, sizeof(buffer));
                if (bytesRead > 0) {
                    replyFile.write(buffer, bytesRead);
                    totalReceived += bytesRead;
                }
            }
        }
        replyFile.flush();
        replyFile.close();
        http.end();

        Serial.printf("[HTTP] Saved incoming audio: %u bytes\n", totalReceived);
        return (totalReceived > 100);
    }

    http.end();
    return false;
}

// ============================================================
// WAV PLAYBACK ENGINE (ANTI-CRACKLE + DIGITAL GAIN)
// ============================================================
void playWavFile(const char* filePath) {
    File file = SD.open(filePath, FILE_READ);
    if (!file) {
        Serial.println("[ERROR] Reply file not found on SD.");
        return;
    }

    // Skip the 44-byte WAV header to get to raw PCM samples
    file.seek(44);

    i2s_start(I2S_NUM_1);

    int16_t mono_buf[512];
    int16_t stereo_buf[1024];
    size_t bytes_written = 0;

    while (file.available()) {
        int bytesRead = file.read((uint8_t*)mono_buf, sizeof(mono_buf));
        int samples = bytesRead / sizeof(int16_t);

        for (int i = 0; i < samples; i++) {
            // Apply 1.5x digital gain boost with boundary clamping
            int32_t val = (int32_t)(mono_buf[i] * 1.5);
            if (val > 32767)  val = 32767;
            if (val < -32768) val = -32768;

            stereo_buf[i * 2]     = (int16_t)val;
            stereo_buf[i * 2 + 1] = (int16_t)val;
        }

        i2s_write(I2S_NUM_1, stereo_buf, samples * 2 * sizeof(int16_t), &bytes_written, portMAX_DELAY);
    }

    i2s_zero_dma_buffer(I2S_NUM_1);
    i2s_stop(I2S_NUM_1);
    file.close();
}

// ============================================================
// LCD & UTILITIES
// ============================================================
void displayOnLCD(const String &line1, const String &line2) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(line1.substring(0, min(16, (int)line1.length())));
    lcd.setCursor(0, 1);
    lcd.print(line2.substring(0, min(16, (int)line2.length())));
}

void writeWavHeader(File &file, uint32_t sampleRate, uint16_t bitsPerSample, uint16_t channels, uint32_t dataSize) {
    uint32_t byteRate = sampleRate * channels * (bitsPerSample / 8);
    uint16_t blockAlign = channels * (bitsPerSample / 8);
    uint32_t chunkSize = 36 + dataSize;

    uint8_t header[44] = {
        'R', 'I', 'F', 'F',
        (uint8_t)(chunkSize & 0xFF), (uint8_t)((chunkSize >> 8) & 0xFF), (uint8_t)((chunkSize >> 16) & 0xFF), (uint8_t)((chunkSize >> 24) & 0xFF),
        'W', 'A', 'V', 'E',
        'f', 'm', 't', ' ',
        16, 0, 0, 0,
        1, 0,
        (uint8_t)(channels & 0xFF), (uint8_t)((channels >> 8) & 0xFF),
        (uint8_t)(sampleRate & 0xFF), (uint8_t)((sampleRate >> 8) & 0xFF), (uint8_t)((sampleRate >> 16) & 0xFF), (uint8_t)((sampleRate >> 24) & 0xFF),
        (uint8_t)(byteRate & 0xFF), (uint8_t)((byteRate >> 8) & 0xFF), (uint8_t)((byteRate >> 16) & 0xFF), (uint8_t)((byteRate >> 24) & 0xFF),
        (uint8_t)(blockAlign & 0xFF), (uint8_t)((blockAlign >> 8) & 0xFF),
        (uint8_t)(bitsPerSample & 0xFF), (uint8_t)((bitsPerSample >> 8) & 0xFF),
        'd', 'a', 't', 'a',
        (uint8_t)(dataSize & 0xFF), (uint8_t)((dataSize >> 8) & 0xFF), (uint8_t)((dataSize >> 16) & 0xFF), (uint8_t)((dataSize >> 24) & 0xFF)
    };
    file.write(header, 44);
}

void updateWavHeader(File &file, uint32_t dataSize) {
    uint32_t chunkSize = 36 + dataSize;
    file.seek(4);
    file.write((uint8_t*)&chunkSize, 4);
    file.seek(40);
    file.write((uint8_t*)&dataSize, 4);
}