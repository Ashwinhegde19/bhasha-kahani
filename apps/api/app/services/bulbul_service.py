import httpx
import base64
from typing import Optional
from app.config import get_settings

settings = get_settings()

# Language code mapping for Bulbul API
LANGUAGE_CODES = {
    "en": "en-IN",
    "hi": "hi-IN", 
    "kn": "kn-IN"
}

# Bulbul speaker voices mapping
SPEAKER_VOICES = {
    # Default voices
    "meera": "meera",      # Warm elderly female (narrator)
    "arvind": "arvind",    # Young male
    "pooja": "pooja",      # Young female
    "amol": "amol",        # Middle-aged male
    "neha": "neha",        # Cheerful female
    # Add more as needed
}


class BulbulService:
    def __init__(self):
        self.api_key = settings.sarvam_api_key
        self.base_url = settings.sarvam_base_url
        self.headers = {
            "API-Subscription-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def synthesize(
        self, 
        text: str, 
        language: str, 
        speaker: str = "meera",
        code_mix: float = 0.0
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
        
        # Map speaker
        bulbul_speaker = SPEAKER_VOICES.get(speaker, speaker)
        
        payload = {
            "inputs": [text],
            "target_language_code": bulbul_lang,
            "speaker": bulbul_speaker,
            "model": "bulbul:v3",
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.0,
            "speech_sample_rate": 22050,
            "enable_preprocessing": True,
            "override_triplets": {}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/speech/generate",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract audio from base64
                if "audios" in data and len(data["audios"]) > 0:
                    audio_b64 = data["audios"][0]
                    return base64.b64decode(audio_b64)
                
                return None
                
            except httpx.HTTPError as e:
                print(f"Bulbul API error: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None
    
    async def get_voices(self) -> list:
        """Get available voices from Bulbul API"""
        # Return local voice mapping for now
        return [
            {"id": "meera", "name": "Meera", "gender": "female", "style": "warm_elderly"},
            {"id": "arvind", "name": "Arvind", "gender": "male", "style": "young"},
            {"id": "pooja", "name": "Pooja", "gender": "female", "style": "young"},
            {"id": "amol", "name": "Amol", "gender": "male", "style": "middle_aged"},
            {"id": "neha", "name": "Neha", "gender": "female", "style": "cheerful"},
        ]
