import json
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.routers import audio as audio_router
from app.routers import choices as choices_router
from app.routers import stories as stories_router
from app.routers import users as users_router
from app.database import build_pooler_connect_args, normalize_database_url
from app.schemas.story import MakeChoiceRequest


class FakeScalars:
    def __init__(self, values):
        self._values = values

    def all(self):
        return list(self._values)


class FakeResult:
    def __init__(self, *, scalar=None, scalars=None, rows=None):
        self._scalar = scalar
        self._scalars = [] if scalars is None else scalars
        self._rows = [] if rows is None else rows

    def scalar_one_or_none(self):
        return self._scalar

    def scalar(self):
        return self._scalar

    def scalars(self):
        return FakeScalars(self._scalars)

    def all(self):
        return list(self._rows)


class FakeDB:
    def __init__(self, results):
        self._results = list(results)
        self._index = 0
        self.flush = AsyncMock()
        self.rollback = AsyncMock()

    async def execute(self, *args, **kwargs):
        result = self._results[self._index]
        self._index += 1
        return result

    def add(self, _obj):
        return None


def fake_db(results):
    return FakeDB(results)


class StoriesRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_list_stories_falls_back_to_english_translation(self):
        story = SimpleNamespace(
            id=uuid4(),
            slug="story-one",
            age_range="4-8",
            region="pan-indian",
            moral="Be kind",
            duration_min=3,
            cover_image="",
            created_at=datetime.now(timezone.utc),
        )
        en_translation = SimpleNamespace(
            story_id=story.id,
            language_code="en",
            title="Story One",
            description="English fallback",
            is_complete=True,
        )
        db = fake_db(
            [
                FakeResult(rows=[(story, 2, 1)]),
                FakeResult(scalars=[en_translation]),
            ]
        )

        with patch.object(
            stories_router.cache_service, "get", new=AsyncMock(return_value=None)
        ), patch.object(stories_router.cache_service, "set", new=AsyncMock()):
            response = await stories_router.list_stories(
                language="hi",
                age_range=None,
                db=db,
            )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].title, "Story One")
        self.assertEqual(response.data[0].language, "en")

    async def test_list_stories_falls_back_to_any_available_translation(self):
        story = SimpleNamespace(
            id=uuid4(),
            slug="story-kn",
            age_range="5-8",
            region="south-india",
            moral="Be truthful",
            duration_min=5,
            cover_image="",
            created_at=datetime.now(timezone.utc),
        )
        kn_translation = SimpleNamespace(
            story_id=story.id,
            language_code="kn",
            title="ಕಥೆ",
            description="Kannada only",
            is_complete=True,
        )
        db = fake_db(
            [
                FakeResult(rows=[(story, 1, 0)]),
                FakeResult(scalars=[kn_translation]),
            ]
        )

        with patch.object(
            stories_router.cache_service, "get", new=AsyncMock(return_value=None)
        ), patch.object(stories_router.cache_service, "set", new=AsyncMock()):
            response = await stories_router.list_stories(
                language="hi",
                age_range=None,
                db=db,
            )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].title, "ಕಥೆ")
        self.assertEqual(response.data[0].language, "kn")

    async def test_get_story_uses_first_node_when_start_flag_missing(self):
        story = SimpleNamespace(
            id=uuid4(),
            slug="story-two",
            age_range="7-10",
            region="pan-indian",
            moral="Stay honest",
            duration_min=4,
            cover_image="",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        en_translation = SimpleNamespace(
            story_id=story.id,
            language_code="en",
            title="Story Two",
            description="Fallback description",
        )
        first_node = SimpleNamespace(
            id=uuid4(),
            node_type="narration",
            display_order=1,
            is_start=False,
            is_end=False,
            text_content={"en": "First"},
            character_id=None,
        )
        second_node = SimpleNamespace(
            id=uuid4(),
            node_type="narration",
            display_order=2,
            is_start=False,
            is_end=True,
            text_content={"en": "Second"},
            character_id=None,
        )
        db = fake_db(
            [
                FakeResult(scalar=story),
                FakeResult(scalars=[en_translation]),
                FakeResult(scalars=[]),
                FakeResult(scalars=[second_node, first_node]),
                FakeResult(scalars=[]),
            ]
        )

        with patch.object(
            stories_router.cache_service, "get", new=AsyncMock(return_value=None)
        ), patch.object(stories_router.cache_service, "set", new=AsyncMock()):
            response = await stories_router.get_story("story-two", language="hi", db=db)

        self.assertEqual(response.language, "en")
        self.assertEqual(response.start_node_id, first_node.id)
        self.assertEqual(response.nodes[0].id, first_node.id)

    async def test_get_story_falls_back_to_non_english_translation(self):
        story = SimpleNamespace(
            id=uuid4(),
            slug="story-three",
            age_range="7-10",
            region="pan-indian",
            moral="Stay honest",
            duration_min=4,
            cover_image="",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        kn_translation = SimpleNamespace(
            story_id=story.id,
            language_code="kn",
            title="ಮೂರು",
            description="Kannada fallback",
        )
        node = SimpleNamespace(
            id=uuid4(),
            node_type="narration",
            display_order=1,
            is_start=True,
            is_end=False,
            text_content={"kn": "ಪಾಠ", "en": "lesson"},
            character_id=None,
        )
        db = fake_db(
            [
                FakeResult(scalar=story),
                FakeResult(scalars=[kn_translation]),
                FakeResult(scalars=[]),
                FakeResult(scalars=[node]),
                FakeResult(scalars=[]),
            ]
        )

        with patch.object(
            stories_router.cache_service, "get", new=AsyncMock(return_value=None)
        ), patch.object(stories_router.cache_service, "set", new=AsyncMock()):
            response = await stories_router.get_story("story-three", language="hi", db=db)

        self.assertEqual(response.language, "kn")
        self.assertEqual(response.title, "ಮೂರು")

    async def test_list_stories_uses_fallback_when_database_unavailable(self):
        class FailingDB:
            async def execute(self, *args, **kwargs):
                raise ConnectionRefusedError("db down")

        fallback_story = {
            "slug": "fallback-story",
            "age_range": "4-8",
            "region": "pan-indian",
            "moral": "Moral",
            "duration_min": 3,
            "cover_image": "",
            "translations": {
                "kn": {"title": "ಕಥೆ", "description": "ವಿವರಣೆ"},
            },
            "characters": [],
            "nodes": [],
        }

        with patch.object(
            stories_router.cache_service, "get", new=AsyncMock(return_value=None)
        ), patch.object(
            stories_router.cache_service, "set", new=AsyncMock()
        ), patch.object(
            stories_router, "load_fallback_stories", return_value=[fallback_story]
        ):
            response = await stories_router.list_stories(
                language="kn",
                age_range=None,
                db=FailingDB(),
            )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].slug, "fallback-story")
        self.assertEqual(response.data[0].title, "ಕಥೆ")


class DatabaseConfigRegressionTests(unittest.TestCase):
    def test_normalize_database_url_maps_sslmode_to_connect_args(self):
        normalized_url, connect_args = normalize_database_url(
            "postgresql://user:pass@host:6543/postgres?sslmode=require"
        )

        self.assertEqual(
            normalized_url,
            "postgresql+asyncpg://user:pass@host:6543/postgres",
        )
        self.assertEqual(connect_args, {"ssl": "require"})

    def test_build_pooler_connect_args_disables_statement_cache(self):
        connect_args = build_pooler_connect_args({"ssl": "require"})

        self.assertEqual(connect_args["prepared_statement_cache_size"], 0)
        self.assertEqual(connect_args["statement_cache_size"], 0)
        self.assertEqual(connect_args["ssl"], "require")
        self.assertTrue(callable(connect_args["prepared_statement_name_func"]))
        prepared_name = connect_args["prepared_statement_name_func"]()
        self.assertTrue(prepared_name.startswith("__asyncpg_stmt_"))


class AudioRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_audio_returns_202_while_generating(self):
        node_id = uuid4()
        story_id = uuid4()
        node = SimpleNamespace(
            id=node_id,
            story_id=story_id,
            text_content={"hi": "नमस्ते", "en": "hello"},
        )
        db = fake_db(
            [
                FakeResult(scalar=None),
                FakeResult(scalar=node),
            ]
        )

        with patch.object(
            audio_router.cache_service, "get_audio_url", new=AsyncMock(return_value=None)
        ), patch.object(
            audio_router.cache_service, "set_audio_url", new=AsyncMock()
        ), patch.object(
            audio_router.bulbul_service, "synthesize", new=AsyncMock(return_value=None)
        ):
            response = await audio_router.get_audio(
                node_id=node_id,
                language=" HI ",
                speaker=" Meera ",
                code_mix=0.0,
                db=db,
            )

        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 202)
        payload = json.loads(response.body.decode())
        self.assertEqual(payload["language"], "hi")
        self.assertEqual(payload["speaker"], "meera")
        self.assertEqual(payload["status"], "generating")

    async def test_get_audio_handles_unique_insert_race(self):
        node_id = uuid4()
        story_id = uuid4()
        node = SimpleNamespace(
            id=node_id,
            story_id=story_id,
            text_content={"en": "Hello world"},
        )
        existing = SimpleNamespace(
            r2_url="https://audio.example.com/existing.mp3",
            code_mix_ratio=Decimal("0.00"),
            duration_sec=Decimal("1.25"),
            file_size=4321,
        )
        db = fake_db(
            [
                FakeResult(scalar=None),
                FakeResult(scalar=node),
                FakeResult(scalar="story-slug"),
                FakeResult(scalar=existing),
            ]
        )
        db.flush.side_effect = IntegrityError(None, None, Exception("duplicate"))

        with patch.object(
            audio_router.cache_service, "get_audio_url", new=AsyncMock(return_value=None)
        ), patch.object(
            audio_router.cache_service, "set_audio_url", new=AsyncMock()
        ), patch.object(
            audio_router.bulbul_service,
            "synthesize",
            new=AsyncMock(return_value=b"audio-bytes"),
        ), patch.object(
            audio_router.r2_service,
            "upload_audio",
            new=AsyncMock(return_value="https://audio.example.com/new.mp3"),
        ):
            response = await audio_router.get_audio(
                node_id=node_id,
                language="EN",
                speaker="MEERA",
                code_mix=0.0,
                db=db,
            )

        self.assertTrue(response.is_cached)
        self.assertEqual(response.audio_url, existing.r2_url)
        db.rollback.assert_awaited_once()

    async def test_get_audio_returns_503_when_database_unavailable(self):
        class FailingDB:
            async def execute(self, *args, **kwargs):
                raise ConnectionRefusedError("db down")

            def add(self, _obj):
                return None

            async def flush(self):
                return None

            async def rollback(self):
                return None

        with patch.object(
            audio_router.cache_service, "get_audio_url", new=AsyncMock(return_value=None)
        ):
            with self.assertRaises(HTTPException) as ctx:
                await audio_router.get_audio(
                    node_id=uuid4(),
                    language="en",
                    speaker="meera",
                    code_mix=0.0,
                    db=FailingDB(),
                )

        self.assertEqual(ctx.exception.status_code, 503)


class ProgressRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_update_progress_keeps_completed_state(self):
        story_id = uuid4()
        node_id = uuid4()
        user_id = uuid4()
        story = SimpleNamespace(id=story_id)
        node = SimpleNamespace(id=node_id, story_id=story_id, display_order=1, is_end=False)
        progress = SimpleNamespace(
            user_id=user_id,
            story_id=story_id,
            current_node_id=node_id,
            play_count=2,
            total_time_sec=120,
            last_played_at=None,
            is_completed=True,
            completion_percentage=100.0,
        )
        db = fake_db(
            [
                FakeResult(scalar=story),
                FakeResult(scalar=node),
                FakeResult(scalar=progress),
                FakeResult(scalar=10),
            ]
        )

        result = await users_router.update_progress(
            user_id=user_id,
            token_user_id=None,
            story_id=story_id,
            current_node_id=node_id,
            is_completed=False,
            time_spent_sec=5,
            db=db,
        )

        self.assertEqual(result["success"], True)
        self.assertTrue(progress.is_completed)
        self.assertEqual(float(progress.completion_percentage), 100.0)


class ChoiceRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_make_choice_replaces_choice_history_list(self):
        story_id = uuid4()
        node_id = uuid4()
        next_node_id = uuid4()
        user_id = uuid4()

        story = SimpleNamespace(id=story_id, slug="story-three")
        current_node = SimpleNamespace(id=node_id, story_id=story_id)
        choice = SimpleNamespace(
            id=uuid4(),
            node_id=node_id,
            choice_key="A",
            text_content={"en": "Choose A"},
            next_node_id=next_node_id,
        )
        next_node = SimpleNamespace(
            id=next_node_id,
            story_id=story_id,
            node_type="narration",
            display_order=2,
            is_start=False,
            is_end=False,
            text_content={"en": "Next node"},
            character_id=None,
        )
        original_choices = [
            {
                "node_id": str(uuid4()),
                "choice_key": "B",
                "made_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
        progress = SimpleNamespace(
            user_id=user_id,
            story_id=story_id,
            current_node_id=node_id,
            choices_made=original_choices,
            play_count=1,
            total_time_sec=0,
            is_completed=False,
            completion_percentage=0.0,
        )
        db = fake_db(
            [
                FakeResult(scalar=story),
                FakeResult(scalar=current_node),
                FakeResult(scalar=choice),
                FakeResult(scalar=next_node),
                FakeResult(scalar=4),
                FakeResult(scalar=progress),
            ]
        )

        response = await choices_router.make_choice(
            slug="story-three",
            request=MakeChoiceRequest(node_id=node_id, choice_key="A"),
            user_id=user_id,
            token_user_id=None,
            language="en",
            db=db,
        )

        self.assertEqual(response.success, True)
        self.assertIsNot(progress.choices_made, original_choices)
        self.assertEqual(len(progress.choices_made), 2)
        self.assertEqual(response.progress["choices_made_count"], 2)


if __name__ == "__main__":
    unittest.main()
