"""
Cloudflare R2 Storage Service
R2 is S3-compatible object storage
"""

import boto3
from botocore.config import Config
from typing import Optional
from app.config import get_settings

settings = get_settings()


class R2Service:
    def __init__(self):
        self.bucket_name = settings.r2_bucket_name
        self.public_url = settings.r2_public_url

        # R2 is S3-compatible
        self.s3_client = boto3.client(
            service_name="s3",
            endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",  # R2 uses 'auto' region
        )

    async def upload_audio(
        self,
        audio_bytes: bytes,
        story_slug: str,
        node_id: str,
        language: str,
        speaker: str,
    ) -> Optional[str]:
        """
        Upload audio file to R2 and return public URL

        Args:
            audio_bytes: Raw audio file bytes
            story_slug: Story identifier (e.g., 'clever-crow')
            node_id: Node UUID
            language: Language code (en, hi, kn)
            speaker: Speaker voice ID

        Returns:
            Public URL of uploaded file or None if failed
        """
        try:
            # Create key: stories/{slug}/audio/{language}/{speaker}/{node_id}.mp3
            file_key = f"stories/{story_slug}/audio/{language}/{speaker}/{node_id}.mp3"

            # Upload to R2
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=audio_bytes,
                ContentType="audio/mpeg",
                Metadata={
                    "language": language,
                    "speaker": speaker,
                    "node-id": str(node_id),
                },
            )

            # Return public URL
            if self.public_url:
                return f"{self.public_url}/{file_key}"
            else:
                # Construct URL from endpoint
                return f"https://{settings.r2_account_id}.r2.cloudflarestorage.com/{self.bucket_name}/{file_key}"

        except Exception as e:
            print(f"R2 upload error: {e}")
            return None

    async def delete_audio(self, file_key: str) -> bool:
        """Delete audio file from R2"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except Exception as e:
            print(f"R2 delete error: {e}")
            return False

    async def check_file_exists(self, file_key: str) -> bool:
        """Check if file exists in R2 bucket"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except Exception:
            return False

    def generate_file_key(
        self, story_slug: str, node_id: str, language: str, speaker: str
    ) -> str:
        """Generate the S3/R2 key for an audio file"""
        return f"stories/{story_slug}/audio/{language}/{speaker}/{node_id}.mp3"
