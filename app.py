"""The Call — AI Commentator Studio (Streamlit edition).

Four inputs only: sport, commentary delivery, language, and match situation.
Groq generates the script; ElevenLabs TTS performs it when configured. If TTS is
unavailable, the embedded browser narrator is offered as a fallback.
"""
from __future__ import annotations

import base64
import html
import json
import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import commentary_engine as engine
from _characters import (
    _svg_commentator,
    _svg_batter,
    _svg_bowler,
    _svg_striker,
    _svg_keeper,
)

APP_DIR = Path(__file__).resolve().parent
CSS_PATH = APP_DIR / "app.css"
STAGE_CSS_PATH = APP_DIR / "stage.css"
MAX_SITUATION_CHARS = engine.MAX_SITUATION_CHARS


def _get_secret(name: str) -> str:
    """Read Streamlit Secrets or environment variables without exposing values."""
    try:
        value = st.secrets.get(name, "")
        if value:
            return str(value).strip()
    except Exception:
        pass
    return os.getenv(name, "").strip()


def _load_css() -> None:
    if CSS_PATH.exists():
        st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def _clean_html(value: str) -> str:
    return html.escape(value or "").replace("\n", "<br>")


def _script_json(value) -> str:
    """Serialize values safely inside an inline script element."""
    return (json.dumps(value, ensure_ascii=False)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def _build_stage_html(
    sport: str,
    delivery: str,
    language: str,
    message: str,
    audio_bytes: bytes | None,
    narration_ready: bool = True,
    audio_mime_type: str = "audio/mpeg",
) -> str:
    """Create an isolated animated character stage with synced narration controls."""
    if sport == "Cricket":
        player_one, role_one = _svg_batter(), "BATTER"
        player_two, role_two = _svg_bowler(), "BOWLER"
    else:
        player_one, role_one = _svg_striker(), "STRIKER"
        player_two, role_two = _svg_keeper(), "GOALKEEPER"

    stage_css = STAGE_CSS_PATH.read_text(encoding="utf-8") if STAGE_CSS_PATH.exists() else ""
    stage_message = (message or "Your match moment will appear here.").strip()
    if len(stage_message) > 180:
        stage_message = stage_message[:177].rstrip() + "…"
    safe_message = _clean_html(stage_message)

    profiles = engine.make_style_voice_profiles()
    profile = profiles.get(delivery, profiles["Energetic"])
    transcript_json = _script_json(message or "")
    language_json = _script_json(language)
    style_json = _script_json(delivery)
    profile_json = _script_json(profile)

    if audio_bytes:
        encoded = base64.b64encode(audio_bytes).decode("ascii")
        # ElevenLabs returns MP3 (mp3_44100_128) on the configured free plan.
        player_markup = f"""
        <div class="audio-box">
          <div class="audio-label">EXPRESSIVE ELEVENLABS NARRATION</div>
          <audio id="commentary-audio" controls preload="metadata">
            <source src="data:{audio_mime_type};base64,{encoded}" type="{audio_mime_type}">
          </audio>
          <a class="audio-download" download="ai-commentator-voice.mp3" href="data:{audio_mime_type};base64,{encoded}">Download audio ↓</a>
        </div>
        """
        player_script = """
        const audio = document.getElementById('commentary-audio');
        if (audio) {
          audio.addEventListener('play', () => setTalking(true));
          audio.addEventListener('pause', () => setTalking(false));
          audio.addEventListener('ended', () => setTalking(false));
        }
        """
    elif narration_ready:
        player_markup = """
        <div class="audio-box browser-audio">
          <div class="audio-label">DEVICE VOICE · BACKUP NARRATION</div>
          <div class="audio-actions">
            <button id="browser-play" type="button">▶ Play commentary</button>
            <button id="browser-stop" type="button" class="stop-button">■ Stop</button>
          </div>
          <div class="audio-note">Uses the voice available in your browser/device. ElevenLabs provides expressive acting when configured.</div>
        </div>
        """
        player_script = f"""
        const transcript = {transcript_json};
        const language = {language_json};
        const style = {style_json};
        const profile = {profile_json};
        const playButton = document.getElementById('browser-play');
        const stopButton = document.getElementById('browser-stop');
        let currentUtterance = null;
        if (playButton) playButton.addEventListener('click', () => {{
          if (!('speechSynthesis' in window)) {{
            document.getElementById('voice-note').textContent = 'This browser does not support speech narration.';
            return;
          }}
          window.speechSynthesis.cancel();
          currentUtterance = new SpeechSynthesisUtterance(transcript);
          currentUtterance.lang = language === 'Urdu' || language === 'Roman Urdu' ? 'ur-PK' : 'en-US';
          currentUtterance.rate = profile.rate || 1;
          currentUtterance.pitch = profile.pitch || 1;
          currentUtterance.volume = 1;
          currentUtterance.onstart = () => setTalking(true);
          currentUtterance.onend = () => setTalking(false);
          currentUtterance.onerror = () => setTalking(false);
          window.speechSynthesis.speak(currentUtterance);
        }});
        if (stopButton) stopButton.addEventListener('click', () => {{
          if ('speechSynthesis' in window) window.speechSynthesis.cancel();
          setTalking(false);
        }});
        """
        player_markup = player_markup.replace(
            '<div class="audio-note">',
            '<div class="audio-note" id="voice-note">',
        )
    else:
        player_markup = """<div class="audio-box"><div class="audio-note">Audio narration will appear here after you generate a commentary call.</div></div>"""
        player_script = ""

    return f"""<!doctype html>
    <html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>{stage_css}</style></head>
    <body>
      <section class="broadcast-stage" id="broadcast-stage">
        <div class="stage-heading"><span>THE COMMENTARY BOOTH</span><span>{engine.STYLE_EMOJI.get(delivery, '🎙️')} {html.escape(delivery.upper())}</span></div>
        <div class="speech-bubble">{safe_message}</div>
        <div class="character-cast">
          <div class="character-card commentator-card">
            {_svg_commentator(False)}
            <div class="character-name">THE COMMENTATOR</div>
            <div class="character-role">ON AIR · LIVE VOICE</div>
            <div class="sound-wave"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
          </div>
          <div class="character-card player-card">{player_one}<div class="character-name">{role_one}</div><div class="character-role">{html.escape(sport.upper())}</div></div>
          <div class="character-card player-card">{player_two}<div class="character-name">{role_two}</div><div class="character-role">{html.escape(sport.upper())}</div></div>
        </div>
        {player_markup}
      </section>
      <script>
        function setTalking(on) {{
          const speaker = document.querySelector('.talker');
          const stage = document.getElementById('broadcast-stage');
          if (speaker) speaker.classList.toggle('is-talking', !!on);
          if (stage) stage.classList.toggle('speaking-now', !!on);
        }}
        {player_script}
      </script>
    </body></html>"""


def _render_result(result: dict, sport: str, delivery: str, language: str, situation: str) -> None:
    commentary = result.get("commentary", "")
    audio_bytes = result.get("audio_bytes")
    with st.container(border=True):
        st.markdown('<div class="result-kicker">THE BIG CALL</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="commentary-copy">{_clean_html(commentary)}</div>', unsafe_allow_html=True)
        status = result.get("status", "")
        if result.get("used_fallback"):
            st.warning(status)
        else:
            st.success(status)
        if audio_bytes:
            st.caption(result.get("audio_status", "Expressive narration ready."))
        else:
            st.info(result.get("audio_status") or "ElevenLabs voice was unavailable. Use the device voice player below.")

    stage_message = commentary or situation
    components.html(
        _build_stage_html(sport, delivery, language, stage_message, audio_bytes, narration_ready=True),
        height=430,
        scrolling=False,
    )


def main() -> None:
    st.set_page_config(
        page_title="The Call · AI Commentator",
        page_icon="🎙️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    for name in ("GROQ_API_KEY", "ELEVENLABS_API_KEY"):
        if not os.getenv(name):
            secret = _get_secret(name)
            if secret:
                os.environ[name] = secret

    _load_css()

    st.markdown(
        """
        <div class="brand-row">
          <div class="brand-lockup"><span class="brand-icon">🎙️</span><span>THE CALL <i>/</i> AI COMMENTATOR</span></div>
          <div class="brand-note">CRICKET · FOOTBALL · BIG FEELINGS</div>
        </div>
        <section class="hero-copy">
          <div class="eyebrow">A LITTLE DRAMA. A LOT OF SPORT.</div>
          <h1>Make the moment<br><em>sound legendary.</em></h1>
          <p>Tell us what happened. Pick the voice of the moment. We’ll turn your match description into original live-style commentary — then perform it.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([0.92, 1.08], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="panel-heading">01 <span>SET THE SCENE</span></div>', unsafe_allow_html=True)
            with st.form("commentary_form", clear_on_submit=False):
                sport = st.radio(
                    "Choose sport",
                    options=engine.SPORTS,
                    horizontal=True,
                    format_func=lambda value: "🏏 Cricket" if value == "Cricket" else "⚽ Football",
                )
                delivery = st.selectbox(
                    "Commentary delivery",
                    options=engine.STYLES,
                    format_func=lambda value: f"{engine.STYLE_EMOJI.get(value, '🎙️')}  {value}",
                )
                language = st.selectbox("Language", options=engine.LANGUAGES, index=0)
                situation = st.text_area(
                    "Describe the match situation",
                    max_chars=MAX_SITUATION_CHARS,
                    height=165,
                    placeholder=(
                        "Example: The batter swings through the line and sends a clean six over long-on…"
                        if sport == "Cricket"
                        else "Example: The striker fires a powerful shot towards the top corner and the goalkeeper makes a stunning save…"
                    ),
                )
                submitted = st.form_submit_button("🎙️  MAKE THE CALL", type="primary", use_container_width=True)

    if submitted:
        situation = (situation or "").strip()
        if not situation:
            st.session_state["last_result"] = {
                "commentary": "Please describe the match situation first, then press MAKE THE CALL.",
                "status": "Match situation is required.",
                "used_fallback": True, "audio_bytes": None,
                "audio_status": "No narration was generated.",
                "sport": sport, "delivery": delivery, "language": language,
                "situation": "",
            }
        else:
            with st.spinner("The commentator is preparing the call…"):
                text, status, used_fallback, event = engine.generate_commentary(
                    sport=sport,
                    situation=situation,
                    style=delivery,
                    language=language,
                    personality=(
                        "A witty, charismatic, original sports commentator. "
                        "Expressive, audience-friendly and fact-grounded. "
                        "Use vivid live-broadcast phrasing, but never invent players, scores or events."
                    ),
                    commentator_name="The Boundary Voice",
                    event_choice="Auto-detect",
                )
                audio_bytes = None
                audio_status = ""
                if text:
                    audio_bytes, audio_status = engine.synthesize_expressive_audio(
                        text=text,
                        style=delivery,
                        language=language,
                        voice_id="",
                        intensity=4,
                    )
                st.session_state["last_result"] = {
                    "commentary": text,
                    "status": f"{event} · {status}",
                    "used_fallback": used_fallback,
                    "audio_bytes": audio_bytes,
                    "audio_status": audio_status,
                    "sport": sport,
                    "delivery": delivery,
                    "language": language,
                    "situation": situation,
                }

    with right:
        result = st.session_state.get("last_result")
        if result and (result.get("commentary") or result.get("status")):
            result_sport = result.get("sport", sport)
            result_delivery = result.get("delivery", delivery)
            result_language = result.get("language", language)
            _render_result(
                result,
                result_sport,
                result_delivery,
                result_language,
                result.get("situation", situation),
            )
        else:
            components.html(
                _build_stage_html(sport, delivery, language, situation or "Give me a match moment. I’ll give it a voice.", None, narration_ready=False),
                height=430,
                scrolling=False,
            )
            st.markdown(
                '<div class="empty-note">Your commentary and narration will appear here. Choose four settings and make the call.</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="footer-note">THE CALL · Original sports commentary, powered by Groq inference and optional ElevenLabs voice performance. No real commentator is imitated.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
