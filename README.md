# The Call — AI Commentator Studio (Streamlit)

A beginner-friendly sports commentary application with four inputs only:

1. Choose sport: Cricket or Football
2. Commentary delivery: Energetic, Dramatic, Funny, Emotional or Professional
3. Language: English, Urdu or Roman Urdu
4. Describe the match situation

Press **MAKE THE CALL**. Groq generates the commentary, then ElevenLabs TTS automatically creates expressive narration when `ELEVENLABS_API_KEY` is available. If ElevenLabs TTS is unavailable, the character-stage player provides a browser speech fallback.

## Project structure

```text
AI_Commentator_Studio/
├── app.py                    # Streamlit frontend
├── app.css                   # Main theme (Pantone-inspired palette)
├── stage.css                 # Animated character and audio-player theme
├── commentary_engine.py      # Groq generation + ElevenLabs TTS
├── _characters.py            # Original inline SVG characters
├── requirements.txt
└── tests/
    └── test_project.py
```

## Run in Google Colab

1. Open `AI_Commentator_Instructor_Streamlit_ElevenLabs.ipynb` in Colab.
2. Run the upload cell and upload `AI_Commentator_Studio_Streamlit_ElevenLabs.zip`.
3. Run the dependency installation cell.
4. Add Colab Secrets `GROQ_API_KEY` and `ELEVENLABS_API_KEY` (the latter is optional).
5. Run the API test, commentary/TTS demo and unit tests.
6. Run the Streamlit cell. The app appears in an iframe inside Colab.

The Colab runtime must remain active. Restarting or disconnecting the runtime stops the app. The notebook includes an optional Cloudflare Quick Tunnel cell for a temporary public preview. Quick Tunnel URLs are temporary, have no uptime guarantee, and stop working when the tunnel process ends. They are not permanent production hosting.

## Run locally on your computer

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Set environment variables without putting secrets in source files:

**Windows PowerShell**
```powershell
$env:GROQ_API_KEY="your-groq-key"
$env:ELEVENLABS_API_KEY="your-elevenlabs-key"  # optional
streamlit run app.py
```

**macOS/Linux**
```bash
export GROQ_API_KEY="your-groq-key"
export ELEVENLABS_API_KEY="your-elevenlabs-key"  # optional
streamlit run app.py
```

## APIs and privacy

- Groq uses the already-trained `openai/gpt-oss-20b` model for inference. The project does not train or download a model.
- ElevenLabs TTS is optional and uses the `eleven_v4` model through the ElevenLabs text-to-speech API.
- If ElevenLabs TTS cannot produce audio, an in-browser speech-synthesis fallback is offered.
- Never commit API keys to source code or share a public Colab notebook containing key values.
- The application instructs the model to use only match facts provided by the visitor; users should still review generated text.

## Theme and characters

The warm UI uses screen approximations inspired by Pantone 12-0812 Alabaster Gleam, 18-1411 TCX Plum Wine and 18-0622 TCX Olive Drab. The commentator, batter, bowler, striker and goalkeeper are original inline SVGs. The commentator's mouth and sound bars animate while narration plays.

## Tests

```bash
python -m unittest discover -s tests -v
```


### ElevenLabs voice configuration

Add `ELEVENLABS_API_KEY` to Colab Secrets. The app uses the `eleven_v4` model and MP3 output through the ElevenLabs REST API. The default voice is the public George example voice ID from the official quickstart; to change it without adding a UI control, set the optional `ELEVENLABS_VOICE_ID` environment variable. The app falls back to browser speech synthesis if the API is unavailable or rate-limited.
