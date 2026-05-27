# 🎙️ Mukul Oli - AI Voice Bot Portfolio Assistant

An advanced, interactive voice-enabled chatbot powered by the **Google Gemini 2.5 Flash API**. This intelligent assistant acts as a live, voice-friendly agent for Mukul Oli's developer portfolio, capable of answering queries in first-person regarding his technical expertise, professional background, education, and innovative AI/Full-Stack projects.

---

## 🌟 Features

- **🧠 Intelligent Persona**: Adheres strictly to a curated portfolio factsheet, speaking dynamically as Mukul Oli.
- **⚡ High-Performance Streaming**: Implements real-time token streaming (`/chat-stream`) using Server-Sent Events (SSE) for instantaneous, lag-free conversations.
- **🎙️ Direct WebRTC / Gemini Live API Support**: Ready-to-go client configuration endpoint for full duplex audio/voice connections.
- **🔒 Context-Aware Sessions**: Manages session state with auto-cleaning and an in-memory conversation window (rolling context of the latest messages).
- **🛡️ Precise Response Bounds**: Out-of-bounds queries are gently redirected to Mukul's portfolio context, preventing hallucinated answers or unrelated topics.

---

## 🛠️ Tech Stack

- **Backend Framework**: Flask (Python) with CORS integration.
- **AI Orchestration**: Google Gemini Developer API (using the official modern `google-genai` SDK).
- **Session Management**: UUID-based multi-user session isolation.
- **Environment Management**: Python-dotenv & Pathlib.

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have Python 3.10+ installed.

### 2. Installation

Clone the repository and install the dependencies:

```bash
# Navigate to the workspace
cd "d:\gemmine voice"

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory (or use the existing one) and configure your Gemini API Key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Running the Server

Start the local development server:

```bash
python app.py
```

The server will spin up on **`http://localhost:5000`** and serve the interactive web frontend automatically.

---

## 🔌 API Endpoints

### `GET /`
Serves the premium, responsive test frontend.

### `GET /health`
Simple health check endpoint returning JSON status details.

### `GET /config`
Exposes system prompting configuration and API metadata for direct browser/WebRTC integration.

### `POST /chat`
Accepts a JSON payload representing a text prompt, returning the full response:
```json
{
  "message": "Tell me about your AI experience",
  "session_id": "optional-uuid"
}
```

### `POST /chat-stream`
Accepts JSON chat data and yields a server-sent event (SSE) stream of text chunks. Perfect for text-to-speech synthesis pipelines.

### `POST /clear`
Clears the in-memory chat history associated with a specific `session_id`.

---

## 👤 About Mukul Oli

Mukul Oli is a dedicated **AI Developer** at *Webuters Technologies Pvt. Ltd.*, specialising in:
* **Voice AI & WebRTC Agents** (LiveKit, Twilio, OpenAI Audio)
* **Agentic Frameworks & Multi-Step Reasoning** (LangChain, LangGraph)
* **Retrieval-Augmented Generation (RAG) Platforms** (Pinecone, Firebase, FastAPI/Next.js)

Feel free to connect or explore more projects through this voice agent or via email at **mukuloli43@gmail.com**.
