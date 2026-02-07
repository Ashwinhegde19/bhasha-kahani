"""
Supabase Storage Service for Audio Files
Free tier: 1GB storage, 2GB bandwidth
No credit card required!
"""

import httpx
from typing import Optional
from app.config import get_settings

settings = get_settings()


class StorageService:
    """Supabase Storage service for audio files"""

    def __init__(self):
        self.supabase_url = None
        self.supabase_key = getattr(settings, "supabase_service_key", None) or getattr(
            settings, "supabase_key", None
        )
        self.bucket_name = "audio-files"
        self._storage_url = None

        # Extract Supabase URL from database URL
        if hasattr(settings, "database_url") and settings.database_url:
            try:
                # Parse: postgresql://user:pass@db.xxxxx.supabase.co:5432/dbname
                host = settings.database_url.split("@")[1].split(":")[0]
                if "supabase.co" in host:
                    # Extract project ref: db.xxxxx -> xxxxx
                    project_ref = host.replace("db.", "").replace(".supabase.co", "")
                    self.supabase_url = f"https://{project_ref}.supabase.co"
            except:
                pass

    @property
    def storage_url(self) -> Optional[str]:
        """Get Supabase storage URL"""
        if self._storage_url is None and self.supabase_url:
            self._storage_url = f"{self.supabase_url}/storage/v1"
        return self._storage_url

    def is_configured(self) -> bool:
        """Check if Supabase storage is configured"""
        return all([self.storage_url, self.supabase_key])

    async def upload_audio(
        self,
        audio_bytes: bytes,
        story_slug: str,
        node_id: str,
        language: str,
        speaker: str,
    ) -> Optional[str]:
        """
        Upload audio file to Supabase Storage and return public URL

        Args:
            audio_bytes: Raw audio file bytes
            story_slug: Story identifier (e.g., 'clever-crow')
            node_id: Node UUID
            language: Language code (en, hi, kn)
            speaker: Speaker voice ID

        Returns:
            Public URL of uploaded file or None if failed
        """
        if not self.is_configured():
            print("⚠️  Supabase storage not configured - returning placeholder URL")
            print(
                "   To enable: Get your service key from Supabase Dashboard > Project Settings > API"
            )
            return None

        try:
            # Create file path: stories/{slug}/audio/{language}/{speaker}/{node_id}.mp3
            file_path = f"stories/{story_slug}/audio/{language}/{speaker}/{node_id}.mp3"

            # Upload via Supabase Storage API
            upload_url = f"{self.storage_url}/object/{self.bucket_name}/{file_path}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    upload_url,
                    headers={
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "audio/mpeg",
                        "x-upsert": "true",  # Overwrite if exists
                    },
                    content=audio_bytes,
                    timeout=30.0,
                )

                if response.status_code in [200, 201]:
                    # Return public URL
                    public_url = f"{self.storage_url}/object/public/{self.bucket_name}/{file_path}"
                    print(f"✅ Uploaded to Supabase: {public_url}")
                    return public_url
                else:
                    print(f"❌ Upload failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None

        except Exception as e:
            print(f"❌ Storage upload error: {e}")
            return None

    async def delete_audio(self, file_path: str) -> bool:
        """Delete audio file from storage"""
        if not self.is_configured():
            return False

        try:
            delete_url = f"{self.storage_url}/object/{self.bucket_name}/{file_path}"

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    delete_url,
                    headers={"Authorization": f"Bearer {self.supabase_key}"},
                    timeout=10.0,
                )
                return response.status_code in [200, 204]

        except Exception as e:
            print(f"Storage delete error: {e}")
            return False


# Keep R2Service for backward compatibility
class R2Service(StorageService):
    """Alias for StorageService (backward compatibility)"""

    pass
