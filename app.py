"""Flask backend for generating interview questions using Google Gemini.

Run:
    python app.py

Environment variables:
    GEMINI_API_KEY: Google Gemini API key (required)
"""

from __future__ import annotations

import json
import logging
import os
import traceback
from typing import List

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Configure logging early so every module uses it.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env if present.
load_dotenv()

app = Flask(__name__)
application = app
CORS(app)


@app.route("/")
def home() -> "FlaskResponse":
    """Serve the main application page."""
    return render_template("index.html")


@app.get("/health")
def health() -> "FlaskResponse":
    """Health check endpoint."""
    return jsonify({"status": "ok"})


def generate_questions_with_gemini(job_title: str) -> List[str]:
    """Generate exactly 3 interview questions for the given job title."""

    # ---- 1. Check API key ----
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY is not set in environment / .env file")
        raise RuntimeError("GEMINI_API_KEY is not set")

    logger.debug("GEMINI_API_KEY found (length=%d)", len(api_key))

    # ---- 2. Import google.genai (catches install issues) ----
    try:
        from google import genai
    except ImportError as exc:
        logger.error("Failed to import google-genai: %s", exc)
        raise RuntimeError(
            "google-genai package is not installed. Run: pip install google-genai"
        ) from exc

    # ---- 3. Build client ----
    try:
        client = genai.Client(api_key=api_key)
        logger.debug("Gemini client created successfully")
    except Exception as exc:
        logger.error("Failed to create Gemini client: %s", exc)
        logger.debug(traceback.format_exc())
        raise RuntimeError(f"Could not initialise Gemini client: {exc}") from exc

    prompt = (
        "You are an experienced hiring manager. Generate exactly 3 thoughtful, "
        f"role-specific interview questions for a {job_title} position.\n\n"
        "Rules:\n"
        "- Each question should assess a different competency (e.g. technical skill, "
        "communication, problem-solving, customer empathy, etc.)\n"
        f"- Questions must be specific to the {job_title} role, not generic\n"
        "- Return ONLY a JSON array of 3 strings, with no extra text, no markdown, "
        "no explanation. Example format:\n"
        '[\"Question one?\", \"Question two?\", \"Question three?\"]'
    )

    # ---- 4. Call Gemini API ----
    logger.debug("Sending request to Gemini for job_title=%r", job_title)
    try:
                
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )
        logger.debug("Gemini raw response: %r", getattr(response, "text", response))
    except Exception as exc:
        logger.error("Gemini API request failed: %s", exc)
        logger.debug(traceback.format_exc())
        raise RuntimeError(
            "An error occurred while fetching results. Please try again shortly."
        )

    # ---- 5. Extract text from response ----
    raw_text = getattr(response, "text", None) or ""
    logger.debug("Gemini response text: %r", raw_text)

    if not raw_text.strip():
        logger.error("Gemini returned an empty response body")
        raise RuntimeError(
            "An error occurred while fetching results. Please try again shortly."
        )

    # Strip markdown code fences that Gemini sometimes adds despite instructions.
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[-2] if "```" in cleaned[3:] else cleaned
        cleaned = "\n".join(
            line for line in cleaned.splitlines()
            if not line.startswith("```")
        ).strip()
    logger.debug("Cleaned text for parsing: %r", cleaned)

    # ---- 6. Parse JSON ----
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse error: %s | raw text was: %r", exc, raw_text)
        raise RuntimeError(
            "An error occurred while fetching results. Please try again shortly."
        ) from exc

    # ---- 7. Validate shape ----
    if (
        not isinstance(parsed, list)
        or len(parsed) != 3
        or not all(isinstance(q, str) for q in parsed)
    ):
        logger.error(
            "Unexpected parsed shape: type=%s, len=%s, value=%r",
            type(parsed).__name__,
            len(parsed) if isinstance(parsed, list) else "n/a",
            parsed,
        )
        raise RuntimeError(
            "An error occurred while fetching results. Please try again shortly."
        )

    logger.info("Successfully generated %d questions for %r", len(parsed), job_title)
    return parsed


@app.post("/generate-questions")
def generate_questions() -> "FlaskResponse":
    """Generate interview questions from a provided job title."""

    logger.debug("POST /generate-questions — raw body: %r", request.data)

    payload = request.get_json(silent=True) or {}
    logger.debug("Parsed JSON payload: %r", payload)

    job_title = payload.get("job_title")

    if not isinstance(job_title, str) or not job_title.strip():
        logger.warning("Missing or invalid job_title in request payload")
        return jsonify({"error": "job_title is required"}), 400

    logger.info("Generating questions for job_title=%r", job_title.strip())

    try:
        questions = generate_questions_with_gemini(job_title.strip())
        return jsonify({"questions": questions})
    except Exception as exc:
        # Log the full traceback server-side; return a clear message to the client.
        logger.error("Error in generate_questions_with_gemini: %s", exc)
        logger.debug(traceback.format_exc())
        # Return generic, non-provider-specific error to the client.
        return jsonify({"error": "An error occurred while generating questions."}), 500


# FlaskResponse forward reference for type checkers.
try:
    from flask.wrappers import Response as FlaskResponse  # type: ignore
except Exception:  # pragma: no cover
    FlaskResponse = object  # type: ignore


def main() -> None:
    """Start the Flask development server."""
    # debug=True keeps the reloader; use_reloader=False if you want cleaner logs.
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()