#!/usr/bin/env python3
"""
Deploy Bhasha Kahani API to Render.com using Render API
"""

import asyncio
import httpx
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import get_settings

settings = get_settings()


async def deploy_to_render():
    """Deploy service to Render using API"""

    api_key = settings.render_api_key
    if not api_key:
        print("❌ RENDER_API_KEY not configured!")
        print("   Add to your .env file:")
        print("   RENDER_API_KEY=your_api_key_here")
        print(
            "\n   Get API key from: https://dashboard.render.com/u/settings?add-api-key"
        )
        return False

    print("🚀 Deploying to Render.com...")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        # First, get the list of workspaces
        print("\n1️⃣  Getting workspaces...")
        try:
            response = await client.get(
                "https://api.render.com/v1/owners", headers=headers
            )
            response.raise_for_status()
            workspaces = response.json()

            if not workspaces:
                print("❌ No workspaces found!")
                return False

            owner_id = workspaces[0]["owner"]["id"]
            owner_name = workspaces[0]["owner"]["name"]
            print(f"   ✓ Found workspace: {owner_name}")

        except Exception as e:
            print(f"❌ Failed to get workspaces: {e}")
            return False

        # Create the service
        print("\n2️⃣  Creating web service...")
        service_config = {
            "type": "web_service",
            "name": "bhasha-kahani-api",
            "ownerId": owner_id,
            "repo": "https://github.com/Ashwinhegde19/bhasha-kahani",
            "serviceDetails": {
                "runtime": "python",
                "region": "singapore",
                "plan": "starter",  # Using starter instead of free for better API support
                "branch": "develop",
                "rootDir": "apps/api",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
                "healthCheckPath": "/health",
                "envSpecificDetails": {"runtime": "python"},
            },
            "envVars": [
                {"key": "DATABASE_URL", "value": settings.database_url},
                {"key": "SUPABASE_SERVICE_KEY", "value": settings.supabase_service_key},
                {"key": "SARVAM_API_KEY", "value": settings.sarvam_api_key},
                {"key": "SECRET_KEY", "value": settings.secret_key},
                {"key": "PYTHON_VERSION", "value": "3.12.0"},
            ],
        }

        try:
            response = await client.post(
                "https://api.render.com/v1/services",
                headers=headers,
                json=service_config,
            )

            if response.status_code == 201:
                service = response.json()
                service_id = service.get("id", "unknown")
                service_name = service.get("name", "unknown")
                service_url = service.get("serviceDetails", {}).get("url", "unknown")

                print(f"   ✓ Service created: {service_name}")
                print(f"   ✓ Service ID: {service_id}")
                print(f"   ✓ URL: {service_url}")
                print(f"\n   🎉 Deployed successfully!")
                print(f"\n   Your API will be live at:")
                print(f"   {service_url}")
                print(f"\n   Health check:")
                print(f"   {service_url}/health")

                return True

            elif response.status_code == 409:
                print("   ⚠️  Service already exists!")
                print("   Check your Render dashboard for 'bhasha-kahani-api'")
                print("   URL: https://dashboard.render.com")
                return True
            else:
                print(f"❌ Failed to create service: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Failed to create service: {e}")
            return False


async def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("BHASHA KAHANI - RENDER DEPLOYMENT")
    print("=" * 60 + "\n")

    success = await deploy_to_render()

    print("\n" + "=" * 60)
    if success:
        print("✅ DEPLOYMENT INITIATED!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("   1. Wait 2-3 minutes for build to complete")
        print("   2. Check status: https://dashboard.render.com")
        print("   3. Test API once live")
    else:
        print("❌ DEPLOYMENT FAILED")
        print("=" * 60)
        print("\n💡 Alternative: Deploy manually via dashboard")
        print("   1. Go to https://dashboard.render.com/services")
        print("   2. Click 'New +' → 'Web Service'")
        print("   3. Connect your GitHub repo")
        print("   4. Configure settings from render.yaml")
        sys.exit(1)

    print()


if __name__ == "__main__":
    asyncio.run(main())
