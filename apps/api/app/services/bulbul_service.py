import httpx
import base64
from typing import Optional
from app.config import get_settings

settings = get_settings()

# Language code mapping for Bulbul API
LANGUAGE_CODES = {"en": "en-IN", "hi": "hi-IN", "kn": "kn-IN"}

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
DEFAULT_TEMPERATURE = 0.75


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
    ) -> Optional[bytes]:
        """
        Generate audio using Sarvam Bulbul API with improved human-like voices

        Args:
            text: Text to synthesize
            language: Language code (en, hi, kn)
            speaker: Speaker voice ID (character name)
            code_mix: Code mixing ratio (0.0 to 1.0)
            temperature: Voice expressiveness (0.01 to 2.0, default 0.75)

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

        # Build payload according to Sarvam API docs
        # IMPROVED: Added temperature for better expressiveness
        payload = {
            "text": text,
            "target_language_code": bulbul_lang,
            "speaker": bulbul_speaker,
            "model": "bulbul:v3",
            "pace": 1.0,  # Normal pace
            "speech_sample_rate": "24000",  # Higher quality
            "temperature": temperature,  # More expressive/human-like
            # Note: WAV format (default) for pydub compatibility
        }

        async with httpx.AsyncClient() as client:
            try:
                print(
                    f"Bulbul API request: speaker={bulbul_speaker}, lang={bulbul_lang}, temp={temperature}"
                )
                response = await client.post(
                    f"{self.base_url}/text-to-speech",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0,
                )
                print(f"Bulbul API response status: {response.status_code}")
                response.raise_for_status()

                data = response.json()
                print(f"Bulbul API response: {data.keys()}")

                # Extract audio from base64
                if "audios" in data and len(data["audios"]) > 0:
                    audio_b64 = data["audios"][0]
                    return base64.b64decode(audio_b64)

                return None

            except httpx.HTTPError as e:
                print(f"Bulbul API error: {e}")
                if hasattr(e, "response") and e.response is not None:
                    print(f"Response content: {e.response.text}")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

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
