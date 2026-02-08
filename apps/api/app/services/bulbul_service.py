import httpx
import base64
from typing import Optional
from app.config import get_settings

settings = get_settings()

# Language code mapping for Bulbul API
LANGUAGE_CODES = {"en": "en-IN", "hi": "hi-IN", "kn": "kn-IN"}

# Bulbul speaker voices mapping - Valid speakers for bulbul:v3
# From Sarvam docs: shubh, aditya, ritu, priya, neha, rahul, pooja, rohan, simran, kavya,
# amit, dev, ishita, shreya, ratan, varun, manan, sumit, roopa, kabir, aayan, ashutosh,
# advait, amelia, sophia, anand, tanya, tarun, sunny, mani, gokul, vijay, shruti,
# suhani, mohit, kavitha, rehan, soham, rupali
SPEAKER_VOICES = {
    "meera": "shubh",  # Warm elderly female -> map to shubh
    "arvind": "aditya",  # Young male
    "pooja": "pooja",  # Young female (valid)
    "amol": "amit",  # Middle-aged male
    "neha": "neha",  # Cheerful female (valid)
    "ajji": "shubh",  # Narrator - warm female
    "punyakoti": "pooja",  # Gentle female
    "arbhuta": "amit",  # Fierce male
}


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
        self, text: str, language: str, speaker: str = "shubh", code_mix: float = 0.0
    ) -> Optional[bytes]:
        """
        Generate audio using Sarvam Bulbul API

        Args:
            text: Text to synthesize
            language: Language code (en, hi, kn)
            speaker: Speaker voice ID
            code_mix: Code mixing ratio (0.0 to 1.0)

        Returns:
            Audio bytes or None if failed
        """
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY not configured")

        # Map language code
        bulbul_lang = LANGUAGE_CODES.get(language, f"{language}-IN")

        # Map speaker to valid Bulbul speaker
        bulbul_speaker = SPEAKER_VOICES.get(speaker, speaker)

        # Build payload according to Sarvam API docs
        # Note: bulbul:v3 doesn't support pitch, loudness, enable_preprocessing
        payload = {
            "text": text,
            "target_language_code": bulbul_lang,
            "speaker": bulbul_speaker,
            "model": "bulbul:v3",
            "pace": 1.0,
            "speech_sample_rate": "22050",
        }

        async with httpx.AsyncClient() as client:
            try:
                print(f"Bulbul API request: {payload}")
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
        """Get available voices from Bulbul API"""
        # Return local voice mapping for now
        return [
            {
                "id": "meera",
                "name": "Meera",
                "gender": "female",
                "style": "warm_elderly",
            },
            {"id": "arvind", "name": "Arvind", "gender": "male", "style": "young"},
            {"id": "pooja", "name": "Pooja", "gender": "female", "style": "young"},
            {"id": "amol", "name": "Amol", "gender": "male", "style": "middle_aged"},
            {"id": "neha", "name": "Neha", "gender": "female", "style": "cheerful"},
        ]
