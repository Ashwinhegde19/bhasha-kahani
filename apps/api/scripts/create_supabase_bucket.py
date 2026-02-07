#!/usr/bin/env python3
"""
Create Supabase Storage bucket for audio files
Run this once to set up the bucket
"""

import asyncio
import httpx
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import get_settings

settings = get_settings()


async def create_bucket():
    """Create the audio-files bucket in Supabase Storage"""

    # Extract Supabase URL from database URL
    supabase_url = None
    if hasattr(settings, "database_url") and settings.database_url:
        try:
            host = settings.database_url.split("@")[1].split(":")[0]
            if "supabase.co" in host:
                project_ref = host.replace("db.", "").replace(".supabase.co", "")
                supabase_url = f"https://{project_ref}.supabase.co"
        except:
            pass

    if not supabase_url:
        print("❌ Could not extract Supabase URL from DATABASE_URL")
        return False

    # Get service key
    service_key = getattr(settings, "supabase_service_key", None)
    if not service_key:
        print("❌ SUPABASE_SERVICE_KEY not configured in .env")
        print("   Get it from: Supabase Dashboard > Project Settings > API")
        return False

    storage_url = f"{supabase_url}/storage/v1"

    print(f"🚀 Creating bucket 'audio-files' in Supabase...")
    print(f"   URL: {storage_url}")

    async with httpx.AsyncClient() as client:
        # Create bucket
        response = await client.post(
            f"{storage_url}/bucket",
            headers={
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
            },
            json={
                "id": "audio-files",
                "name": "audio-files",
                "public": True,  # Make bucket public for audio playback
            },
        )

        if response.status_code in [200, 201]:
            print("✅ Bucket 'audio-files' created successfully!")
            print(f"   Public URL: {storage_url}/object/public/audio-files/")
            return True
        elif response.status_code == 409 and "already exists" in response.text.lower():
            print("✅ Bucket 'audio-files' already exists!")
            return True
        else:
            print(f"❌ Failed to create bucket: {response.status_code}")
            print(f"Response: {response.text}")
            return False


if __name__ == "__main__":
    success = asyncio.run(create_bucket())
    sys.exit(0 if success else 1)
