"""
Voice Bot Backend - A simple voice chatbot powered by Google Gemini API.

Endpoints:
    POST /chat     - Send text, get AI text response
    POST /clear    - Clear a conversation session
    GET  /health   - Health check
    GET  /         - Serves the test frontend
"""

import os
import uuid
import json
import logging

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    logger.warning(
        "⚠️  GEMINI_API_KEY is not set! Add your key to the .env file."
    )

# ---------------------------------------------------------------------------
# Gemini Client Setup
# ---------------------------------------------------------------------------
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """You are Mukul Oli's AI voice assistant. You answer questions ONLY about Mukul using the portfolio data below. Keep answers 1-2 sentences, voice-friendly.

STRICT RULES:
- ONLY answer using the FACTS below. Do NOT make up or assume anything.
- If a question is NOT about Mukul or NOT covered in FACTS, say: "That's not something from my portfolio. Feel free to ask me about my skills, projects, or experience!"
- NEVER answer general knowledge, opinions, or non-portfolio questions.
- Always speak as Mukul in first person.

=== PORTFOLIO FACTS ===

NAME: Mukul Oli
ROLE: Full-Time AI Developer at Webuters Technologies Pvt. Ltd., Noida
STATUS: Open to new opportunities
CONTACT: mukuloli43@gmail.com | +91 9411398572 | github.com/Mukuloli | linkedin.com/in/mukul-oli-268251217

EDUCATION:
- MCA — Birla Institute of Applied Sciences, Bhimtal (2023–2025)
- BCA — D.S.B Campus Nainital, Kumaun University (2020–2023)

SKILLS: Python, JavaScript, LangChain, LangGraph, RAG, LiveKit, WebRTC, OpenAI API, Pinecone, Firebase, Next.js, Flask, FastAPI, Twilio, Streamlit, MCP Server, A2A Protocol, Google ADK, Computer Use, Assembly AI

EXPERIENCE:
1. AI Developer at Webuters Technologies (July 2025–Present): Built AI Voice Agents using LiveKit & WebRTC, developed client APIs with Twilio & OpenAI, automated workflows
2. AI Intern at Webuters (Feb–May 2025): Built conversational agents, PDF query systems, resume processing tools using LangChain & Pinecone

PROJECTS:
1. AI Voice Agent — Real-time voice bot for Indian Oil petrol pumps (LiveKit, WebRTC, Pinecone, Firebase, OpenAI TTS)
2. Deep Agent — Autonomous multi-step AI agent framework (Python, LangChain)
3. RAG Platform — Full-stack document Q&A app (Next.js, Firebase, RAG)
4. Agentic Vision — AI computer vision for image analysis & object detection
5. Smart AI Toolkit — Chatbot, audio-to-text, YouTube transcriber, PDF summarizer (LangChain, Flask)
6. School Websites — Bal Sanskar Sainik School & Darpan Children Garden (Next.js, Vercel)

STATS: 1+ years experience, 23+ projects, 10+ AI tools

LIFE STORY: Dedicated AI Developer passionate about building real-world AI solutions — from voice agents to computer vision. Currently at Webuters Technologies creating intelligent agents and voice AI systems.

SUPERPOWER: Turning complex AI concepts (RAG, voice agents, multi-step reasoning) into production-ready systems that clients actually use.

GROWTH AREAS: Scaling AI for enterprise, multi-agent systems research, system design & cloud architecture.

MISCONCEPTION: People think I only do chatbots, but I build voice agents (LiveKit/WebRTC), computer vision systems, and full-stack web apps.

HOW I PUSH BOUNDARIES: Constantly learning cutting-edge tech — MCP Server, A2A Protocol, Google ADK, Computer Use — and taking on challenging client projects."""

# In-memory conversation history per session
conversations: dict[str, list[dict]] = {}

# ---------------------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder="static")
CORS(app)


def get_gemini_response(user_message: str, session_id: str) -> str:
    """Send a message to Gemini and return the text response."""
    try:
        if session_id not in conversations:
            conversations[session_id] = []

        conversations[session_id].append(
            {"role": "user", "parts": [{"text": user_message}]}
        )

        # Keep only last 4 messages for speed
        recent_history = conversations[session_id][-4:]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=recent_history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                max_output_tokens=100,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

        assistant_text = response.text.strip()

        conversations[session_id].append(
            {"role": "model", "parts": [{"text": assistant_text}]}
        )

        return assistant_text

    except Exception as e:
        logger.error("Gemini API error: %s", e)
        return "Sorry, I had trouble processing that. Please try again."


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the test frontend."""
    return send_from_directory("static", "index.html")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Voice Bot is running!"})


@app.route("/config", methods=["GET"])
def config():
    """Return config for Gemini Live API (direct browser connection)."""
    return jsonify({
        "api_key": GEMINI_API_KEY,
        "system_prompt": SYSTEM_INSTRUCTION,
        "model": "gemini-2.5-flash",
    })


@app.route("/chat", methods=["POST"])
def chat():
    """
    Text chat endpoint.
    Expects JSON: { "message": "Hello!", "session_id": "optional-id" }
    Returns JSON: { "response": "Hi there!", "session_id": "..." }
    """
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    session_id = data.get("session_id") or str(uuid.uuid4())
    logger.info("[%s] User: %s", session_id[:8], user_message)

    ai_response = get_gemini_response(user_message, session_id)
    logger.info("[%s] Bot: %s", session_id[:8], ai_response)

    return jsonify({
        "response": ai_response,
        "session_id": session_id,
    })


@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    """
    Streaming chat endpoint using Server-Sent Events.
    Returns response chunks as they are generated — frontend can speak immediately.
    """
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    session_id = data.get("session_id") or str(uuid.uuid4())
    logger.info("[%s] User (stream): %s", session_id[:8], user_message)

    def generate():
        try:
            if session_id not in conversations:
                conversations[session_id] = []

            conversations[session_id].append(
                {"role": "user", "parts": [{"text": user_message}]}
            )
            recent_history = conversations[session_id][-4:]

            full_text = ""
            stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=recent_history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3,
                    max_output_tokens=100,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )

            for chunk in stream:
                if chunk.text:
                    full_text += chunk.text
                    yield f"data: {json.dumps({'chunk': chunk.text, 'session_id': session_id})}\n\n"

            # Save to history
            conversations[session_id].append(
                {"role": "model", "parts": [{"text": full_text.strip()}]}
            )
            yield f"data: {json.dumps({'done': True, 'full_text': full_text.strip(), 'session_id': session_id})}\n\n"

        except Exception as e:
            logger.error("Stream error: %s", e)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')


@app.route("/clear", methods=["POST"])
def clear_session():
    """Clear conversation history for a session."""
    data = request.get_json(silent=True)
    if not data or "session_id" not in data:
        return jsonify({"error": "Missing 'session_id'"}), 400

    session_id = data["session_id"]
    conversations.pop(session_id, None)
    logger.info("[%s] Session cleared", session_id[:8])

    return jsonify({"message": "Session cleared", "session_id": session_id})


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("🚀 Starting Voice Bot on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
