<p align="center">
  <img src="https://img.shields.io/badge/SIH-2026-blueviolet?style=for-the-badge&logo=government&logoColor=white" alt="SIH 2026"/>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-API-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/Ollama-Qwen3-FF6F00?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama"/>
  <img src="https://img.shields.io/badge/Sarvam_AI-TTS%20%26%20STT-00C853?style=for-the-badge" alt="Sarvam AI"/>
</p>

<h1 align="center">🏛️ Multilingual Government Scheme Assistant</h1>

<p align="center">
  <b>An AI-powered voice assistant that helps citizens discover government schemes — in their own language.</b>
</p>

<p align="center">
  <i>Built for Smart India Hackathon 2026 · Problem Statement 2</i>
</p>

---

## ✨ What It Does

A farmer speaks into an **ESP32 microphone** in Hindi, Tamil, or any Indian language. Seconds later, they hear a **spoken response** explaining exactly which government schemes they're eligible for — complete with benefits, eligibility, and how to apply.

No apps. No screens. No literacy required. Just **voice in, voice out**.

---

## 🏗️ Architecture

```
┌──────────────┐         ┌──────────────────────────────────────────────────┐
│              │  audio   │                  FLASK SERVER                    │
│    ESP32     │ ──────► │                                                  │
│  Microphone  │         │  ┌───────────┐   ┌─────────┐   ┌────────────┐   │
│              │         │  │  Audio     │──►│ Sarvam  │──►│  RAG       │   │
│              │ ◄────── │  │  Handler   │   │ Saaras  │   │  Retriever │   │
│   Speaker    │  .wav   │  └───────────┘   │  (STT)  │   │  (FAISS)   │   │
│              │         │                  └─────────┘   └─────┬──────┘   │
└──────────────┘         │                                      │          │
                         │                                      ▼          │
                         │  ┌───────────┐   ┌─────────┐   ┌────────────┐   │
                         │  │  Sarvam   │◄──│Response │◄──│  Qwen3     │   │
                         │  │  Bulbul   │   │Formatter│   │  (Ollama)  │   │
                         │  │  (TTS)    │   └─────────┘   └────────────┘   │
                         │  └───────────┘                                  │
                         └──────────────────────────────────────────────────┘
```

---

## 🧩 Tech Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **Hardware** | ESP32 | Captures audio & plays response |
| **Server** | Flask | REST API to receive/send audio |
| **Speech-to-Text** | Sarvam Saaras | Multilingual Indian language ASR |
| **Embeddings** | Sentence Transformers | Semantic search over documents |
| **Vector Store** | FAISS | Fast similarity search |
| **LLM** | Qwen3 1.7B (Ollama) | Grounded answer generation |
| **Text-to-Speech** | Sarvam Bulbul | Natural Indian language TTS |
| **Knowledge Base** | Government PDFs | Schemes across 6 sectors |

---

## 📁 Project Structure

```
.
├── main.py                  # Flask server — entry point
├── audio_handler.py         # Processes raw/WAV audio from ESP32
├── transcriber.py           # Sarvam Saaras STT integration
├── scheme_logic.py          # Orchestrates RAG → LLM pipeline
├── response_formatter.py    # Formats LLM output for speech
├── tts_handler.py           # Sarvam Bulbul TTS integration
├── simulate_esp32.py        # Simulates ESP32 for local testing
├── test_pipeline.py         # End-to-end pipeline test
│
├── esp32_s3_firmware_source_code.ino   # ESP32 Arduino firmware
├── ESP32-S3 Multilingual Voice Assistant System Documentation.pdf
│
├── llm/
│   └── llm_handler.py       # Ollama/Qwen3 prompt + inference
│
├── rag/
│   ├── embeddings.py        # Embedding model loader
│   ├── retriever.py         # FAISS search logic
│   └── ingest.py            # PDF → chunks → vectors pipeline
│
├── knowledge_base/          # Source government documents
│   ├── 01_cooperatives/
│   ├── 02_agriculture/
│   ├── 03_finance/
│   ├── 04_allied_agriculture/
│   ├── 05_rural_development/
│   └── 06_social_welfare/
│
├── vector_db/               # Generated FAISS index (gitignored)
├── recordings/              # Runtime audio files (gitignored)
├── requirements.txt
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.com/)** installed and running
- **[FFmpeg](https://ffmpeg.org/)** installed (required by `pydub`)
- **Sarvam AI API Key** — get one at [sarvam.ai](https://www.sarvam.ai/)

### 1️⃣ Clone & Install

```bash
git clone https://github.com/<your-username>/SIH_PS2_2K26.git
cd SIH_PS2_2K26

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### 2️⃣ Pull the LLM

```bash
ollama pull qwen3:1.7b
```

### 3️⃣ Set Up Environment Variables

Create a `.env` file in the project root:

```env
SARVAM_API_KEY=your_sarvam_api_key_here
```

### 4️⃣ Build the Vector Database

```bash
python rag/ingest.py
```

> This processes all PDFs in `knowledge_base/` and creates the FAISS index in `vector_db/`.

### 5️⃣ Run the Server

```bash
python main.py
```

The server starts at **`http://127.0.0.1:5000`** — waiting for audio from the ESP32 or the simulator.

### 6️⃣ Test Without Hardware

```bash
python simulate_esp32.py
```

---

## 🔄 Request Flow

```
1. ESP32 sends raw audio        →  POST /upload
2. Audio normalized to WAV      →  16kHz, mono, 16-bit
3. Sarvam Saaras transcribes    →  Hindi/Tamil/etc. → English
4. FAISS retrieves top-3 docs   →  Semantic search
5. Qwen3 generates answer       →  Grounded on retrieved docs
6. Response formatted for TTS   →  Clean, speakable text
7. Sarvam Bulbul generates WAV  →  Natural speech
8. WAV sent back to ESP32       →  Plays on speaker
```

---

## 📂 Knowledge Base Sectors

| # | Sector | Contents |
|:-:|:-------|:---------|
| 01 | 🤝 Cooperatives | Multi-state cooperative laws, PACS digitization |
| 02 | 🌾 Agriculture | PMFBY, e-NAM, crop insurance, FPOs |
| 03 | 💰 Finance | Income tax benefits for cooperatives, NCDC |
| 04 | 🐄 Allied Agriculture | Fisheries, livestock, dairy, poultry |
| 05 | 🏘️ Rural Development | MGNREGA, rural housing, rural infra |
| 06 | 🫂 Social Welfare | SC/ST schemes, women & child welfare |

---

## ⚙️ Configuration

Key parameters in [`llm/llm_handler.py`](llm/llm_handler.py):

| Parameter | Default | Description |
|:----------|:--------|:------------|
| `MODEL_NAME` | `qwen3:1.7b` | Ollama model to use |
| `MAX_OUTPUT_TOKENS` | `200` | Max response length |
| `MAX_RESULTS` | `3` | Top-K RAG results |
| `REQUEST_TIMEOUT` | `180s` | Ollama request timeout |

---

## 🛡️ Environment Variables

| Variable | Required | Description |
|:---------|:--------:|:------------|
| `SARVAM_API_KEY` | ✅ | API key for Sarvam AI (STT + TTS) |

---

<p align="center">
  <sub>Built with ❤️ for Smart India Hackathon 2026</sub>
</p>
