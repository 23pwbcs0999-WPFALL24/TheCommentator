"""Core logic for AI Commentator Studio.

Groq performs text generation (inference). ElevenLabs TTS optionally performs
its resulting script with expressive, style-directed delivery. No model is
trained or downloaded. All network keys are read from environment variables.
"""
from __future__ import annotations

import os
import re
from typing import Optional

import requests

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
ELEVENLABS_TTS_MODEL = os.getenv("ELEVENLABS_TTS_MODEL", "eleven_v4")
# This is the public example voice used by ElevenLabs' API quickstart. You can
# override it with ELEVENLABS_VOICE_ID without adding another UI control.
ELEVENLABS_DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
ELEVENLABS_OUTPUT_FORMAT = "mp3_44100_128"
MAX_SITUATION_CHARS = 1800
MAX_COMMENTARY_CHARS = 900

SPORTS = ["Cricket", "Football"]
STYLES = ["Energetic", "Dramatic", "Funny", "Emotional", "Professional"]
LANGUAGES = ["English", "Urdu", "Roman Urdu"]

STYLE_EMOJI = {
    "Energetic": "⚡", "Dramatic": "🎭", "Funny": "😄",
    "Emotional": "❤️", "Professional": "🎙️",
}

STYLE_WRITING_GUIDES = {
    "Energetic": "Write like a high-voltage live stadium caller. Use a punchy opening, short rhythmic bursts, vivid action verbs and a rising exclamation at the key moment. A confirmed six should sound like a celebration: 'WHAT A BEAUTIFUL SIX!' A confirmed goal should get a big goal call. Be excited without making up crowd reactions or match facts.",
    "Dramatic": "Write a cinematic, suspense-building call. Use a controlled opening, deliberate ellipses, short pauses and a clear tension-to-release arc. For an airborne six, build the question of whether it will clear the rope, then announce the six only because the user confirmed it. Do not shout every sentence.",
    "Funny": "Write playful, witty live commentary with clever sports metaphors and conversational timing. Keep the action accurate and the humour friendly. Do not mock a player, invent a mistake, or joke about injury.",
    "Emotional": "Write warm, heartfelt commentary that highlights the human feeling of the confirmed moment. Use sincere phrasing, gentle build-up and a meaningful final line. Do not invent a player's personal history, crowd reaction or match importance.",
    "Professional": "Write polished television play-by-play. Use precise sports vocabulary, concise observation, calm confidence and restrained emphasis. State the action clearly and explain its immediate significance only when supported by the situation.",
}

STYLE_TTS_GUIDES = {
    "Energetic": "Deliver as an electrifying live sports commentator. Bright, forward, highly animated voice; noticeably quicker pace; rising pitch and strong dynamic lift on action words; punchy consonants; joyful, emphatic finish. Make a confirmed SIX or GOAL sound like a thrilling live call. Do not keep shouting after the key word.",
    "Dramatic": "Act the call like the decisive final seconds of a major sporting contest. Begin lower, slower and controlled. Create suspense with deliberate pauses and a gradual rise in pitch and intensity. Release the tension strongly only on the confirmed event, then finish with weight. Do not use the same volume throughout.",
    "Funny": "Use a playful, amused broadcaster performance. Light smile in the voice, nimble conversational rhythm, expressive pitch movement and well-timed comic emphasis. Let the witty phrase land naturally; avoid a flat read or exaggerated cartoon voice.",
    "Emotional": "Use a warm, resonant, heartfelt sports-storytelling performance. Gentle pace, sincere tone, expressive warmth and soft emphasis. Let the final phrase carry a little more feeling, without becoming melodramatic or shouting.",
    "Professional": "Perform like a premium television sports broadcaster. Composed, clear, confident and authoritative, with crisp diction, even pacing and controlled emphasis on the important sporting detail. No unnecessary shouting or exaggerated pitch swings.",
}

STYLE_INTENSITY = {
    1: "Subtle performance; keep the emotion restrained.",
    2: "Light but clearly audible performance character.",
    3: "Balanced, unmistakable broadcast performance.",
    4: "Strong performance contrast and expressive delivery.",
    5: "Very expressive performance, while keeping every word intelligible.",
}

EVENTS = {
    "Cricket": ["Auto-detect", "Six", "Four", "Wicket", "Catch", "Yorker", "Dot ball", "Final-over pressure", "Final-ball pressure", "Other"],
    "Football": ["Auto-detect", "Goal", "Penalty", "Big save", "Free kick", "Counter-attack", "Missed chance", "Last-minute pressure", "Other"],
}

# The copy below is a deterministic teaching/demo fallback, not AI output.
OFFLINE_LINES = {
    ("Cricket", "Six", "Energetic"): "WHAT A BEAUTIFUL SIX! That is clean, powerful hitting — straight over the boundary! What a strike!",
    ("Cricket", "Six", "Dramatic"): "Up it goes... hanging in the air... and it is a SIX! A huge hit, delivered in one breathtaking moment.",
    ("Cricket", "Six", "Funny"): "That ball has booked a one-way trip beyond the boundary! A proper six — somebody check its return ticket!",
    ("Cricket", "Six", "Emotional"): "What a beautiful six. The timing, the confidence and the commitment — this is the joy of cricket in one shot.",
    ("Cricket", "Six", "Professional"): "A well-executed six. Excellent contact and sufficient power to clear the boundary with authority.",
    ("Cricket", "Four", "Energetic"): "FOUR! Finds the gap and races away to the boundary! Superb placement!",
    ("Cricket", "Four", "Dramatic"): "Into the gap... the ball keeps moving... and it reaches the boundary. Four runs, with real intent.",
    ("Cricket", "Four", "Funny"): "The ball has found the gap before the fielding side could close the door. Four!",
    ("Cricket", "Four", "Emotional"): "A lovely boundary. Not just power — timing, touch and confidence coming together in one shot.",
    ("Cricket", "Four", "Professional"): "A controlled boundary, placed into the gap. Good balance between timing and placement.",
    ("Cricket", "Wicket", "Energetic"): "OUT! WHAT A BREAKTHROUGH! The bowling side has struck with a wicket!",
    ("Cricket", "Wicket", "Dramatic"): "The moment arrives... a wicket! A decisive breakthrough, and the pressure has a new chapter.",
    ("Cricket", "Wicket", "Funny"): "That is one delivery the batter will not want on repeat. The bowling side gets the breakthrough!",
    ("Cricket", "Wicket", "Emotional"): "A wicket that changes the feeling of the moment. One player walks away disappointed; the bowler has a moment to savour.",
    ("Cricket", "Wicket", "Professional"): "A key dismissal. The bowling side has found a breakthrough in this passage of play.",
    ("Football", "Goal", "Energetic"): "GOOOOAL! WHAT A FINISH! The ball is in the net — a brilliant attacking moment!",
    ("Football", "Goal", "Dramatic"): "The strike is away... the finish is there... GOOOAL! The moment has its answer.",
    ("Football", "Goal", "Funny"): "That finish deserves a second look. The ball finds the net — the goalkeeper has a problem to solve!",
    ("Football", "Goal", "Emotional"): "GOAL. A moment full of joy, relief and sporting emotion — what a finish.",
    ("Football", "Goal", "Professional"): "A clinical finish. The attacking move ends with the ball in the net and a goal on the board.",
    ("Football", "Big save", "Energetic"): "WHAT A SAVE! Quick reactions and a brilliant stop to keep that effort out!",
    ("Football", "Big save", "Dramatic"): "The shot is away... the goalkeeper reaches... and keeps it out. A remarkable save.",
    ("Football", "Big save", "Funny"): "The goalkeeper has just said, 'Not today!' An excellent stop to deny the attempt.",
    ("Football", "Big save", "Emotional"): "A huge save. Concentration, courage and commitment in one important moment.",
    ("Football", "Big save", "Professional"): "An excellent save. Strong positioning and quick reactions keep the attempt out.",
}

URDU_OFFLINE = {
    ("Cricket", "Six", "Energetic"): "کیا شاندار چھکا ہے! گیند سیدھی باؤنڈری کے پار — زبردست شاٹ!",
    ("Cricket", "Six", "Dramatic"): "گیند فضا میں... ایک لمحے کا انتظار... اور یہ چھکا ہے! دباؤ میں کمال کا شاٹ۔",
    ("Cricket", "Six", "Funny"): "لگتا ہے گیند نے باؤنڈری کے پار مستقل رہائش اختیار کر لی ہے! کیا چھکا ہے!",
    ("Cricket", "Six", "Emotional"): "کیا خوبصورت چھکا ہے۔ ٹائمنگ، اعتماد اور جذبہ — کرکٹ کا اصل حسن یہی ہے۔",
    ("Cricket", "Six", "Professional"): "بہترین ٹائمنگ کے ساتھ کھیلا گیا شاٹ، گیند باؤنڈری کے پار اور چھ رنز۔",
    ("Football", "Goal", "Energetic"): "گوووول! کیا زبردست فنش ہے! گیند جال میں پہنچ گئی!",
    ("Football", "Goal", "Dramatic"): "شاٹ نکل چکا ہے... اور یہ گوووول! فیصلہ کن لمحے میں شاندار فنش۔",
    ("Football", "Goal", "Funny"): "گول کیپر کے پاس اس شاٹ کا کوئی جواب نہیں تھا! کیا خوبصورت فنش ہے!",
    ("Football", "Goal", "Emotional"): "گول! خوشی، سکون اور جذبے سے بھرا لمحہ — فٹبال کی یہی خوبصورتی ہے۔",
    ("Football", "Goal", "Professional"): "بہترین فنش۔ حملے کا اختتام گیند کے جال میں پہنچنے پر ہوا۔",
}

ROMAN_URDU_OFFLINE = {
    ("Cricket", "Six", "Energetic"): "Kya khoobsurat SIX hai! Ball seedhi boundary ke paar — kya zabardast shot!",
    ("Cricket", "Six", "Dramatic"): "Ball hawa mein... ek lamhe ka intezar... aur yeh SIX hai! Pressure mein kamaal ka shot.",
    ("Cricket", "Six", "Funny"): "Lagta hai ball ne boundary ke paar permanent rehne ka faisla kar liya hai! Kya six hai!",
    ("Cricket", "Six", "Emotional"): "Kya khoobsurat six hai. Timing, confidence aur jazba — cricket ka asal husn yehi hai.",
    ("Cricket", "Six", "Professional"): "Behtareen timing ke saath khela gaya shot. Ball boundary ke paar aur chhay runs.",
    ("Football", "Goal", "Energetic"): "GOOOAL! Kya zabardast finish hai! Ball seedhi net mein!",
    ("Football", "Goal", "Dramatic"): "Shot nikal chuka hai... aur yeh GOOOAL! Faisla-kun lamhe mein shandaar finish.",
    ("Football", "Goal", "Funny"): "Goalkeeper ke paas is shot ka koi jawab nahi tha! Kya khoobsurat finish hai!",
    ("Football", "Goal", "Emotional"): "GOAL! Khushi, sukoon aur jazbay se bhara lamha — football ki yehi khoobsurti hai.",
    ("Football", "Goal", "Professional"): "Behtareen finish. Attacking move ka ikhtitam ball ke net mein pohanchne par hua.",
}


def detect_event(sport: str, situation: str) -> str:
    """Conservative event detection; 'needs six runs' must not become a six."""
    text = (situation or "").lower()
    if sport == "Cricket":
        needs_runs = re.search(r"\b(need(?:s|ed)?|require(?:s|d)?|must score|target)\b.{0,40}\b(6|six|4|four)\s+runs?\b", text)
        patterns = [
            ("Wicket", r"\b(wicket|bowled|is out|dismissed|stumps are knocked)\b"),
            ("Catch", r"\b(caught|takes? the catch|brilliant catch)\b"),
            ("Six", r"\b(six|for six|over the boundary|over the rope|clears? the boundary)\b"),
            ("Four", r"\b(four|for four|to the boundary|boundary)\b"),
            ("Yorker", r"\byorker\b"),
            ("Dot ball", r"\bdot ball\b"),
            ("Final-ball pressure", r"\b(final ball|last ball)\b"),
            ("Final-over pressure", r"\b(final over|last over)\b"),
        ]
        if needs_runs:
            patterns = [p for p in patterns if p[0] not in {"Six", "Four"}]
    else:
        patterns = [
            ("Goal", r"\b(goal|scores|scored|into the net|finds the net)\b"),
            ("Penalty", r"\bpenalty\b"),
            ("Big save", r"\b(save|saved|goalkeeper stops|keeper stops)\b"),
            ("Free kick", r"\bfree kick\b"),
            ("Counter-attack", r"\b(counter.attack|breakaway)\b"),
            ("Missed chance", r"\b(missed chance|misses the shot|wide|over the bar)\b"),
            ("Last-minute pressure", r"\b(last minute|stoppage time|injury time)\b"),
        ]
    for event, pattern in patterns:
        if re.search(pattern, text):
            return event
    return "General play"


def build_system_prompt(
    sport: str,
    style: str,
    language: str,
    personality: str = "",
    commentator_name: str = "",
    confirmed_event: str = "General play",
) -> str:
    lang_instruction = {
        "English": "Use natural spoken English.",
        "Urdu": "Use natural Urdu in Urdu script (اردو), with fluent Pakistani sports-broadcast phrasing.",
        "Roman Urdu": "Use natural spoken Pakistani Roman Urdu in Latin letters. Do not write Urdu script.",
    }[language]
    voice_persona = personality.strip() or "A charismatic, original sports commentator: vivid, expressive, audience-friendly and clear."
    stage_name = commentator_name.strip() or "The Stadium Voice"
    role_a, role_b = (("batter", "bowler") if sport == "Cricket" else ("attacking player", "goalkeeper / defender"))
    return f"""You are {stage_name}, an original {sport.lower()} commentator writing a spoken live-broadcast call.

SPORT: {sport}
SELECTED STYLE: {style}
LANGUAGE: {language}. {lang_instruction}
CONFIRMED EVENT: {confirmed_event}
COMMENTATOR PERSONALITY: {voice_persona}

STYLE DIRECTION — MAKE THIS OBVIOUS IN THE WORDING:
{STYLE_WRITING_GUIDES[style]}

SPORTS-CALL WRITING RULES:
- Sound like a live commentator reacting in real time, not a generic summary or motivational quote.
- For a confirmed cricket Six in Energetic style, use a decisive call such as 'WHAT A BEAUTIFUL SIX!' or a natural equivalent in the selected language. Make the first line instantly exciting.
- For a confirmed football Goal in Energetic style, use a goal call such as 'GOOOOAL!' or a natural equivalent.
- Dramatic style must have a build-up, a pause or suspense marker, and a release. Funny must contain a harmless witty line. Emotional must sound heartfelt. Professional must be crisp and composed.
- Each style should sound as though a different broadcast director briefed the same commentator. Avoid reusing the same opening across styles.
- Use short spoken sentences, varied rhythm, sports vocabulary and punctuation appropriate to the selected delivery.
- Mention {role_a} and {role_b} only as roles unless names are explicitly provided by the user.

FACTUAL BOUNDARIES:
- The user-provided situation and optional participant fields are the ONLY source of match facts.
- Do not invent names, team names, score, overs, balls, match minute, stadium, crowd response, weather, injury, referee/umpire decision, technique, direction of a shot, or outcome.
- Do not announce that a six, wicket, goal, penalty conversion or save happened unless the user text or explicitly selected key moment confirms it.
- If the situation describes a possibility or build-up, comment on the tension; do not announce an outcome.
- Do not add a score or claim that a moment changes the match unless the user gave that context.
- Do not imitate, impersonate or borrow signature catchphrases from real commentators.

OUTPUT: 2–4 short sentences, approximately 30–55 words. Output only the commentary, in the selected language. No title, markdown, analysis, disclaimers or stage directions.
"""


def offline_commentary(
    sport: str, situation: str, style: str, language: str,
    event: str, participant_a: str = "", participant_b: str = "",
) -> str:
    """Return a clearly-labelled deterministic fallback when APIs are unavailable."""
    lookup = {
        "English": OFFLINE_LINES,
        "Urdu": URDU_OFFLINE,
        "Roman Urdu": ROMAN_URDU_OFFLINE,
    }[language]
    text = lookup.get((sport, event, style))
    if not text:
        opening = {
            "Energetic": "WHAT A MOMENT!",
            "Dramatic": "The tension is building...",
            "Funny": "Well, that is an interesting turn of events!",
            "Emotional": "This is what makes sport special.",
            "Professional": "An important passage of play.",
        }[style]
        if language == "Urdu":
            opening = {
                "Energetic": "کیا زبردست لمحہ ہے!", "Dramatic": "تناؤ بڑھ رہا ہے...",
                "Funny": "یہ تو دلچسپ موڑ ہے!", "Emotional": "کھیل کی خوبصورتی ایسے لمحوں میں ہے۔",
                "Professional": "کھیل کا ایک اہم مرحلہ۔",
            }[style]
        elif language == "Roman Urdu":
            opening = {
                "Energetic": "Kya zabardast lamha hai!", "Dramatic": "Tanaao barh raha hai...",
                "Funny": "Yeh to dilchasp mor hai!", "Emotional": "Khel ki khoobsurti aise lamhon mein hai.",
                "Professional": "Khel ka ek ahem marhala.",
            }[style]
        text = f"{opening} {situation.strip()}"
    if participant_a:
        text = text.replace("the batter", participant_a).replace("the striker", participant_a).replace("the attacking player", participant_a)
    if participant_b:
        text = text.replace("the bowler", participant_b).replace("the goalkeeper", participant_b).replace("the defender", participant_b)
    return text


def _get_secret(name: str) -> str:
    """Read a secret from environment variables; never print or expose it."""
    return os.getenv(name, "").strip()


def generate_commentary(
    sport: str,
    situation: str,
    style: str,
    language: str,
    personality: str = "",
    commentator_name: str = "",
    event_choice: str = "Auto-detect",
    participant_a: str = "",
    participant_b: str = "",
    regenerate: bool = False,
) -> tuple[str, str, bool, str]:
    situation = (situation or "").strip()
    if not situation:
        return "", "Please describe a match situation first.", False, ""
    if len(situation) > MAX_SITUATION_CHARS:
        return "", f"Please keep the situation under {MAX_SITUATION_CHARS} characters.", False, ""

    detected = detect_event(sport, situation)
    event = detected if event_choice in {"Auto-detect", "Other", ""} else event_choice
    system_prompt = build_system_prompt(sport, style, language, personality, commentator_name, event)
    participant_lines = []
    if participant_a.strip():
        label = "Batter" if sport == "Cricket" else "Attacking player"
        participant_lines.append(f"{label}: {participant_a.strip()}")
    if participant_b.strip():
        label = "Bowler" if sport == "Cricket" else "Goalkeeper / defender"
        participant_lines.append(f"{label}: {participant_b.strip()}")
    participants = "\n".join(participant_lines) if participant_lines else "No names supplied. Do not invent names."
    variation = "Create a fresh alternative. Change the opening, rhythm and wording, but preserve all facts." if regenerate else "Create the first version."
    user_prompt = f"MATCH SITUATION (only source of facts):\n{situation}\n\nPARTICIPANTS:\n{participants}\n\n{variation}"

    api_key = _get_secret("GROQ_API_KEY")
    if not api_key:
        fallback = offline_commentary(sport, situation, style, language, event, participant_a, participant_b)
        return fallback, "Offline fallback · GROQ_API_KEY not configured. Add a Groq key for live AI generation.", True, event

    try:
        from groq import Groq
        client = Groq(api_key=api_key, timeout=40.0, max_retries=1)
        # Groq's GPT-OSS guidance recommends putting instructions in the
        # user message. For GPT-OSS, include_reasoning=False is supported;
        # reasoning_format is not supported by this model.
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        result = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": combined_prompt}],
            reasoning_effort="low",
            include_reasoning=False,
            temperature=0.86,
            max_completion_tokens=1024,
            stream=False,
        )
        choice = result.choices[0]
        text = (choice.message.content or "").strip()
        if not text:
            finish_reason = getattr(choice, "finish_reason", None) or "unknown"
            message_fields = list(choice.message.model_dump().keys()) if hasattr(choice.message, "model_dump") else ["content"]
            raise RuntimeError(
                "Groq returned an empty final message "
                f"(finish_reason={finish_reason}; message_fields={message_fields})."
            )
        return text[:MAX_COMMENTARY_CHARS], f"Live AI inference · {GROQ_MODEL}", False, event
    except Exception as exc:
        message = str(exc).lower()
        if "429" in message or "rate" in message:
            reason = "Groq rate limit reached (HTTP 429). Check your account's current limits."
        elif "401" in message or "authentication" in message or "invalid api key" in message:
            reason = "Groq rejected the API key. Check GROQ_API_KEY."
        elif "404" in message or "model" in message and "not found" in message:
            reason = f"Model unavailable: {GROQ_MODEL}. Check Groq's current model catalogue."
        elif "timeout" in message or "connection" in message:
            reason = "Could not reach Groq. Check internet connectivity."
        elif "empty final message" in message:
            reason = (
                "Groq responded but returned no final commentary. "
                "The request uses GPT-OSS low reasoning and include_reasoning=False. "
                "Check the Groq response fields and current model status."
            )
        else:
            # Keep credentials out of logs; the exception message contains the useful API detail.
            safe_detail = str(exc).replace(_get_secret("GROQ_API_KEY"), "[API KEY REDACTED]")
            reason = f"Groq request failed ({type(exc).__name__}): {safe_detail[:240]}"
        fallback = offline_commentary(sport, situation, style, language, event, participant_a, participant_b)
        return fallback, f"Offline fallback · {reason}", True, event


def _elevenlabs_tagged_text(text: str, style: str) -> str:
    """Add supported ElevenLabs v4 acting tags without changing spoken facts.

    Audio tags are model instructions, not commentary content. They are placed
    around the existing transcript; no players, scores or events are invented.
    """
    spoken = (text or "").strip()
    if not spoken:
        return ""

    # Use sentence boundaries to create a clear build-and-release for dramatic
    # and energetic calls. If there is only one sentence, retain a simple tag.
    parts = re.split(r"(?<=[.!?؟۔])\s+", spoken, maxsplit=1)
    first = parts[0]
    remainder = parts[1] if len(parts) > 1 else ""

    if style == "Energetic":
        if remainder:
            return f"[excited] {first} [shouts] {remainder}"
        return f"[excited] {spoken} [shouts]"
    if style == "Dramatic":
        if remainder:
            return f"[whispers] {first} [excited] {remainder}"
        return f"[whispers] {spoken} [shouts]"
    if style == "Funny":
        return f"[mischievously] {spoken}"
    if style == "Emotional":
        return f"[warm, heartfelt, sincere delivery] {spoken}"
    # A restrained direction helps preserve clear broadcast diction.
    return f"[calm, clear, confident sports broadcaster delivery] {spoken}"


def _elevenlabs_voice_settings(style: str, intensity: int = 3) -> dict:
    """Return Eleven v4 voice settings; variation differs by delivery style."""
    stability = {
        "Energetic": 0.30,
        "Dramatic": 0.28,
        "Funny": 0.42,
        "Emotional": 0.48,
        "Professional": 0.72,
    }.get(style, 0.45)
    level = max(1, min(5, int(intensity)))
    # Higher intensity slightly lowers stability for more expressive variation.
    stability = max(0.15, min(0.90, stability + (3 - level) * 0.035))
    return {
        "stability": stability,
        "similarity_boost": 0.75,
        "use_speaker_boost": True,
    }


def synthesize_expressive_audio(
    text: str,
    style: str,
    language: str,
    voice_id: str = "",
    intensity: int = 3,
) -> tuple[Optional[bytes], str]:
    """Generate expressive MP3 narration through the ElevenLabs TTS API.

    The selected style is expressed through ElevenLabs v4 audio tags and
    per-request voice stability. The spoken commentary itself stays intact.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        return None, "ELEVENLABS_API_KEY is not configured. Use browser narration or add an ElevenLabs API key."
    if not text or not text.strip():
        return None, "Generate commentary before creating audio."
    if style not in STYLES:
        return None, f"Unsupported commentary style: {style}."

    selected_voice = (voice_id or ELEVENLABS_DEFAULT_VOICE_ID).strip()
    if not selected_voice:
        return None, "No ElevenLabs voice ID is configured. Set ELEVENLABS_VOICE_ID or use the default voice."

    language_code = {
        "English": "en",
        "Urdu": "ur",
        "Roman Urdu": "ur",
    }.get(language)
    tagged_text = _elevenlabs_tagged_text(text, style)

    payload = {
        "text": tagged_text,
        "model_id": ELEVENLABS_TTS_MODEL,
        "language_code": language_code,
        "voice_settings": _elevenlabs_voice_settings(style, intensity),
    }
    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/"
        f"{selected_voice}?output_format={ELEVENLABS_OUTPUT_FORMAT}"
    )

    try:
        response = requests.post(
            url,
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json=payload,
            timeout=(10, 120),
        )
        if response.status_code >= 400:
            try:
                body = response.json()
                detail = body.get("detail", body.get("error", body))
                if isinstance(detail, dict):
                    detail = detail.get("message") or detail.get("detail") or str(detail)
                detail = str(detail)
            except Exception:
                detail = (response.text or "").strip()

            if response.status_code == 429:
                return None, "ElevenLabs rate limit or credit quota reached. Check your usage window or use browser voice."
            if response.status_code in (401, 403):
                return None, "ElevenLabs rejected the API key or its permissions. Check ELEVENLABS_API_KEY and Text to Speech access."
            if response.status_code == 402:
                return None, "ElevenLabs account/plan limit reached. Check your subscription and remaining credits."
            if response.status_code in (400, 404, 422):
                return None, f"ElevenLabs TTS request, voice or model issue ({response.status_code}): {detail[:240]}"
            return None, f"ElevenLabs TTS failed ({response.status_code}): {detail[:240]}"

        audio = getattr(response, "content", b"") or b""
        if not audio:
            return None, "ElevenLabs returned an empty audio response. Try a shorter commentary."
        content_type = (response.headers.get("content-type", "") or "").lower()
        if "json" in content_type:
            return None, "ElevenLabs returned JSON instead of audio. Check model, voice ID and API permissions."
        return audio, f"Expressive ElevenLabs TTS · {ELEVENLABS_TTS_MODEL} · {style} · MP3"

    except requests.Timeout:
        return None, "ElevenLabs TTS timed out. Try a shorter commentary or browser voice."
    except requests.RequestException as exc:
        return None, f"Network error while contacting ElevenLabs: {type(exc).__name__}."
    except Exception as exc:
        return None, f"Could not create ElevenLabs audio ({type(exc).__name__}): {str(exc)[:160]}"

def make_style_voice_profiles() -> dict:
    """Browser-voice settings; these are best-effort and depend on device voices."""
    return {
        "Energetic": {"rate": 1.18, "pitch": 1.18, "hint": "Fast, bright, rising energy"},
        "Dramatic": {"rate": 0.83, "pitch": 0.90, "hint": "Slow build, controlled suspense"},
        "Funny": {"rate": 1.04, "pitch": 1.20, "hint": "Playful, light, expressive"},
        "Emotional": {"rate": 0.91, "pitch": 0.96, "hint": "Warm, gentle, heartfelt"},
        "Professional": {"rate": 0.98, "pitch": 1.00, "hint": "Steady, composed broadcast"},
    }
