# Interview Question Generator (Flask + Gemini)

Generate 3 role-specific interview questions from a job title using Google Gemini.

## Prerequisites

- Python **3.8+**
- A free Google Gemini API key from: https://ai.google.dev/

## Installation

1. Clone / open this project folder.
2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate it:

   **Windows (cmd):**
   ```bash
   venv\Scripts\activate
   ```

## Installation

1. Clone / open this project folder.
2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate it:

   **Windows (cmd):**
   ```bash
   venv\Scripts\activate
   ```

4. Install or upgrade dependencies:

   ```bash
   pip install --upgrade -r requirements.txt
   ```

5. Configure your API key:
   - Copy `.env.example` to `.env`
   - Set your key:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## How to run

1. Start the Flask backend:

   ```bash
   python app.py
   ```

   The backend runs on `http://localhost:5000`.

2. Open the frontend:
   - Open `http://localhost:5000` in your browser.

## How to get a free Gemini API key

Create a key at: https://ai.google.dev/

## Project structure

- `app.py` - Flask backend (Gemini integration + API endpoints)
- `templates/index.html` - Main application page
- `static/css/style.css` - Application styles
- `static/js/script.js` - Frontend JavaScript
- `requirements.txt` - Python dependencies
- `.env.example` - Example environment variable file
- `.gitignore` - Ignores `.env` and cache folders


curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: AIzaSyD16oyccc8Tpd5s7g6phXKgOch-0Qc_akM' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
