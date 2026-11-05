import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Streamlit is installed by requirements.txt in Colab. In offline test
# environments, stub its import-only modules so pure HTML helpers can be tested.
try:
    import streamlit  # noqa: F401
except ImportError:
    st = types.ModuleType("streamlit")
    st.__path__ = []
    components = types.ModuleType("streamlit.components")
    components.__path__ = []
    components_v1 = types.ModuleType("streamlit.components.v1")
    st.components = components
    components.v1 = components_v1
    sys.modules["streamlit"] = st
    sys.modules["streamlit.components"] = components
    sys.modules["streamlit.components.v1"] = components_v1

import commentary_engine as engine
import app


class CommentaryEngineTests(unittest.TestCase):
    def test_confirmed_six_is_detected(self):
        self.assertEqual(
            engine.detect_event("Cricket", "The batter hits a clean six over long-on."),
            "Six",
        )

    def test_needs_six_runs_is_not_detected_as_a_six(self):
        self.assertNotEqual(
            engine.detect_event("Cricket", "The batting team needs six runs from the last ball."),
            "Six",
        )

    def test_football_goal_is_detected(self):
        self.assertEqual(
            engine.detect_event("Football", "The striker scores and the ball enters the net."),
            "Goal",
        )

    def test_style_prompts_are_distinct(self):
        prompts = {
            style: engine.build_system_prompt("Cricket", style, "English")
            for style in engine.STYLES
        }
        self.assertEqual(len(set(prompts.values())), len(engine.STYLES))

    def test_offline_commentary_styles_are_distinct_for_six(self):
        lines = [
            engine.offline_commentary("Cricket", "The batter hits a six.", style, "English", "Six")
            for style in engine.STYLES
        ]
        self.assertEqual(len(set(lines)), len(engine.STYLES))

    def test_urdu_and_roman_urdu_scripts_are_distinct(self):
        urdu = engine.offline_commentary("Cricket", "The batter hits a six.", "Energetic", "Urdu", "Six")
        roman = engine.offline_commentary("Cricket", "The batter hits a six.", "Energetic", "Roman Urdu", "Six")
        self.assertTrue(any("\u0600" <= ch <= "\u06FF" for ch in urdu))
        self.assertFalse(any("\u0600" <= ch <= "\u06FF" for ch in roman))

    def test_groq_request_uses_gpt_oss_settings_and_returns_text(self):
        captured = {}
        fake_message = types.SimpleNamespace(content="WHAT A BEAUTIFUL SIX!")
        fake_choice = types.SimpleNamespace(message=fake_message, finish_reason="stop")
        fake_response = types.SimpleNamespace(choices=[fake_choice])

        def fake_create(**kwargs):
            captured.update(kwargs)
            return fake_response

        fake_client = types.SimpleNamespace(
            chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=fake_create))
        )
        fake_groq = types.ModuleType("groq")
        fake_groq.Groq = lambda **kwargs: fake_client

        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key", "GROQ_MODEL": "openai/gpt-oss-20b"}):
            with patch.dict(sys.modules, {"groq": fake_groq}):
                text, status, fallback, event = engine.generate_commentary(
                    "Cricket", "The batter hits a clean six over long-on.", "Energetic", "English"
                )

        self.assertEqual(text, "WHAT A BEAUTIFUL SIX!")
        self.assertFalse(fallback)
        self.assertEqual(event, "Six")
        self.assertEqual(captured.get("include_reasoning"), False)
        self.assertEqual(captured.get("reasoning_effort"), "low")
        self.assertEqual(captured.get("max_completion_tokens"), 1024)

    def test_elevenlabs_style_tags_are_distinct(self):
        source = "What a shot! The ball clears the boundary for six."
        tagged = {
            style: engine._elevenlabs_tagged_text(source, style)
            for style in engine.STYLES
        }
        self.assertEqual(len(set(tagged.values())), len(engine.STYLES))
        self.assertIn("[excited]", tagged["Energetic"])
        self.assertIn("[whispers]", tagged["Dramatic"])
        self.assertIn("[mischievously]", tagged["Funny"])

    def test_elevenlabs_synthesis_uses_mp3_and_voice_settings(self):
        captured = {}
        fake_response = types.SimpleNamespace(
            status_code=200,
            content=b"ID3\x00\x00fake-mp3-audio",
            headers={"content-type": "audio/mpeg"},
            text="",
        )
        def fake_post(url, **kwargs):
            captured["url"] = url
            captured.update(kwargs)
            return fake_response
        with patch.dict(os.environ, {
            "ELEVENLABS_API_KEY": "test-eleven-key",
            "ELEVENLABS_TTS_MODEL": "eleven_v4",
        }, clear=False):
            with patch.object(engine.requests, "post", side_effect=fake_post):
                audio, status = engine.synthesize_expressive_audio(
                    "WHAT A SHOT! A magnificent six.", "Energetic", "English"
                )
        self.assertEqual(audio, fake_response.content)
        self.assertIn("ElevenLabs", status)
        self.assertIn("output_format=mp3_44100_128", captured["url"])
        self.assertEqual(captured["headers"]["xi-api-key"], "test-eleven-key")
        self.assertEqual(captured["json"]["model_id"], "eleven_v4")
        self.assertEqual(captured["json"]["language_code"], "en")
        self.assertIn("[excited]", captured["json"]["text"])

    def test_elevenlabs_rate_limit_has_clear_fallback_message(self):
        fake_response = types.SimpleNamespace(
            status_code=429,
            content=b"",
            headers={"content-type": "application/json"},
            text='{"detail":"quota exceeded"}',
            json=lambda: {"detail": {"message": "quota exceeded"}},
        )
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test-key"}, clear=False):
            with patch.object(engine.requests, "post", return_value=fake_response):
                audio, status = engine.synthesize_expressive_audio(
                    "A goal!", "Energetic", "English"
                )
        self.assertIsNone(audio)
        self.assertIn("rate limit or credit quota", status)


class StreamlitFrontendTests(unittest.TestCase):
    def test_stage_has_cricket_characters(self):
        stage = app._build_stage_html("Cricket", "Energetic", "English", "A six!", None)
        self.assertIn("THE COMMENTATOR", stage)
        self.assertIn("BATTER", stage)
        self.assertIn("BOWLER", stage)
        self.assertIn("browser-play", stage)
        self.assertEqual(stage.count("</section>"), 1)

    def test_idle_stage_does_not_offer_empty_playback(self):
        stage = app._build_stage_html("Cricket", "Energetic", "English", "Describe a moment", None, narration_ready=False)
        self.assertIn("Audio narration will appear here", stage)
        self.assertNotIn("browser-play", stage)

    def test_stage_has_football_characters_and_audio_element(self):
        stage = app._build_stage_html("Football", "Dramatic", "English", "A goal!", b"RIFF\x00\x00\x00\x00WAVE")
        self.assertIn("STRIKER", stage)
        self.assertIn("GOALKEEPER", stage)
        self.assertIn("commentary-audio", stage)
        self.assertIn("audio/mpeg", stage)
        self.assertNotIn("browser-play", stage)

    def test_user_text_is_html_escaped(self):
        stage = app._build_stage_html("Cricket", "Funny", "English", "<script>alert('x')</script>", None)
        self.assertNotIn("<script>alert('x')</script>", stage)

    def test_frontend_has_only_four_input_controls_and_no_hf(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        for label in ["Choose sport", "Commentary delivery", "Language", "Describe the match situation"]:
            self.assertIn(f'"{label}"', source)
        self.assertNotIn("history", source.lower())
        self.assertNotIn("gradio", source.lower())
        self.assertNotIn("huggingface", source.lower())
        self.assertNotIn("gemini", source.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
