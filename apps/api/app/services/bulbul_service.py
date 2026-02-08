import httpx
import base64
import re
from typing import Optional
from app.config import get_settings
from pydub import AudioSegment
import io

settings = get_settings()

# Language code mapping for Bulbul API
LANGUAGE_CODES = {"en": "en-IN", "hi": "hi-IN", "kn": "kn-IN"}


def add_natural_pauses(text: str) -> str:
    """
    Add natural conversational pauses to text for more human-like speech.
    Converts written text to spoken style with breathing room.
    """
    # Add slight pause after commas by replacing with comma + ellipsis
    text = re.sub(r"(?<=[,;])(?!\s*\.\.\.)", "... ", text)

    # Add longer pause at end of sentences
    text = re.sub(r'(?<=[.!?])(\s+)(?=[A-Z"])', r"...\1", text)

    return text


def add_silence_to_audio(audio_bytes: bytes, silence_ms: int = 500) -> bytes:
    """Add silence at end of audio segment for natural pauses"""
    try:
        audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))
        silence = AudioSegment.silent(duration=silence_ms)
        audio_with_pause = audio + silence

        buffer = io.BytesIO()
        audio_with_pause.export(buffer, format="wav")
        return buffer.getvalue()
    except Exception as e:
        print(f"Warning: Could not add silence: {e}")
        return audio_bytes


# IMPROVED: Better voice mappings based on Sarvam characteristics
# From Sarvam docs - Voice characteristics:
# Shubh: Confident, Warm (Male) - Best for narration
# Roopa: Clear, Professional (Female) - Good for narrator
# Aditya: Deep, Authoritative (Male) - Best for serious/fierce characters
# Priya: Friendly, Conversational (Female) - Best for gentle/motherly
# Ritu: Balanced, Clear (Female)
# Neha: Energetic, Cheerful (Female)
# Rahul: Young, Energetic (Male)
# Kavya: Soft, Gentle (Female)
# Ishita: Warm, Caring (Female)
# Amit: Strong, Bold (Male)

CHARACTER_VOICE_MAPPING = {
    # Story characters - Punyakoti
    "ajji": "shubh",  # Narrator: Warm, confident male voice (better than female for storytelling)
    "punyakoti": "priya",  # Gentle cow: Friendly, conversational female
    "arbhuta": "aditya",  # Fierce tiger: Deep, authoritative male
    # Alternative mappings for variety
    "narrator": "shubh",  # Warm storyteller
    "hero": "aditya",  # Deep, heroic
    "heroine": "priya",  # Friendly, relatable
    "villain": "rahul",  # Strong, bold
    "elder": "shubh",  # Warm, authoritative
    "child": "kavya",  # Soft, gentle
    "crow": "neha",  # Energetic, cheerful
    "fox": "aditya",  # Deep, cunning
}

# Default temperature for expressiveness (0.6 is default, 0.8 is more expressive)
DEFAULT_TEMPERATURE = 1.0  # Maximum stable expressiveness for storytelling


class BulbulService:
    def __init__(self):
        self.api_key = settings.sarvam_api_key
        self.base_url = settings.sarvam_base_url
        # Correct header name according to Sarvam docs
        self.headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def synthesize(
        self,
        text: str,
        language: str,
        speaker: str = "shubh",
        code_mix: float = 0.0,
        temperature: float = None,
        add_pauses: bool = True,
    ) -> Optional[bytes]:
        """
        Generate audio using Sarvam Bulbul API with improved human-like voices

        Args:
            text: Text to synthesize
            language: Language code (en, hi, kn)
            speaker: Speaker voice ID (character name)
            code_mix: Code mixing ratio (0.0 to 1.0)
            temperature: Voice expressiveness (0.01 to 2.0, default 0.75)
            add_pauses: Add natural pauses between sentences

        Returns:
            Audio bytes or None if failed
        """
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY not configured")

        # Map language code
        bulbul_lang = LANGUAGE_CODES.get(language, f"{language}-IN")

        # IMPROVED: Map character to best Bulbul voice
        bulbul_speaker = CHARACTER_VOICE_MAPPING.get(speaker.lower(), speaker)

        # Use temperature for more human-like expressiveness
        if temperature is None:
            temperature = DEFAULT_TEMPERATURE

        # IMPROVED: Add natural conversational pauses
        if add_pauses:
            text = add_natural_pauses(text)

        # Build payload according to Sarvam API docs
        # IMPROVED: Added temperature for better expressiveness
        payload = {
            "text": text,
            "target_language_code": bulbul_lang,
            "speaker": bulbul_speaker,
            "model": "bulbul:v3",
            "pace": 0.95,  # Slightly slower for storytelling
            "speech_sample_rate": "44100",  # CD quality
            "temperature": temperature,  # More expressive/human-like
        }

        async with httpx.AsyncClient() as client:
            try:
                print(f"Synthesizing: {speaker} ({bulbul_speaker}), {len(text)} chars")
                response = await client.post(
                    f"{self.base_url}/text-to-speech",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0,
                )
                response.raise_for_status()

                data = response.json()

                # Extract audio from base64
                if "audios" in data and len(data["audios"]) > 0:
                    audio_b64 = data["audios"][0]
                    audio_bytes = base64.b64decode(audio_b64)

                    # IMPROVED: Add silence at end for natural pauses between nodes
                    if add_pauses:
                        audio_bytes = add_silence_to_audio(audio_bytes, silence_ms=800)

                    return audio_bytes

                return None

            except httpx.HTTPError as e:
                print(f"Bulbul API error: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

    def get_speaker_for_character(self, character_name: str) -> str:
        """Get the appropriate Bulbul speaker voice for a character name"""
        if not character_name:
            return "meera"

        name_lower = character_name.lower()

        # Map character names to voices
        if (
            "ajji" in name_lower
            or "narrator" in name_lower
            or "grandmother" in name_lower
        ):
            return "shubh"
        elif "punyakoti" in name_lower or "cow" in name_lower:
            return "priya"
        elif "arbhuta" in name_lower or "tiger" in name_lower:
            return "aditya"
        elif "crow" in name_lower:
            return "neha"
        elif "fox" in name_lower:
            return "aditya"
        elif "hero" in name_lower or "boy" in name_lower or "man" in name_lower:
            return "aditya"
        elif "heroine" in name_lower or "girl" in name_lower or "woman" in name_lower:
            return "priya"
        elif "child" in name_lower:
            return "kavya"
        elif "elder" in name_lower or "king" in name_lower or "teacher" in name_lower:
            return "shubh"
        elif "villain" in name_lower or "monster" in name_lower:
            return "rahul"
        else:
            # Default based on common endings
            if name_lower.endswith("a") or name_lower.endswith("i"):
                return "priya"
            else:
                return "shubh"

    async def get_voices(self) -> list:
        """Get available voices with characteristics"""
        return [
            {
                "id": "ajji",
                "name": "Ajji (Narrator)",
                "gender": "female",
                "bulbul_voice": "shubh",
                "characteristics": "Warm, Confident - Perfect for storytelling",
            },
            {
                "id": "punyakoti",
                "name": "Punyakoti",
                "gender": "female",
                "bulbul_voice": "priya",
                "characteristics": "Friendly, Conversational - Gentle and motherly",
            },
            {
                "id": "arbhuta",
                "name": "Arbhuta (Tiger)",
                "gender": "male",
                "bulbul_voice": "aditya",
                "characteristics": "Deep, Authoritative - Fierce and powerful",
            },
            {
                "id": "crow",
                "name": "Crow",
                "gender": "female",
                "bulbul_voice": "neha",
                "characteristics": "Energetic, Cheerful - Smart and clever",
            },
            {
                "id": "fox",
                "name": "Fox",
                "gender": "male",
                "bulbul_voice": "aditya",
                "characteristics": "Deep, Cunning - Clever trickster",
            },
        ]
