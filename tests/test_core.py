"""
Tests unitarios básicos para A.M.Y core.

Ejecutar con: pytest tests/ -v
"""
import json
import pytest

from cognition.reasoning import _clean_json, _fix_json, _parse_json_robust
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from skills.library import SkillLibrary


class TestJSONParsing:
    """Tests para el parsing robusto de JSON del LLM."""

    def test_clean_json_with_markdown_fences(self):
        text = '```json\n{"action": "test"}\n```'
        result = _clean_json(text)
        assert result == '{"action": "test"}'

    def test_clean_json_without_fences(self):
        text = '{"action": "test"}'
        result = _clean_json(text)
        assert result == '{"action": "test"}'

    def test_fix_json_trailing_comma(self):
        text = '{"a": 1,}'
        result = _fix_json(text)
        assert json.loads(result) == {"a": 1}

    def test_fix_json_unterminated_string(self):
        text = '{"key": "value'
        result = _fix_json(text)
        # Should add closing brace
        assert result.endswith('}')

    def test_parse_json_robust_valid(self):
        text = '{"action": "test", "value": 42}'
        result = _parse_json_robust(text)
        assert result["action"] == "test"
        assert result["value"] == 42

    def test_parse_json_robust_with_markdown(self):
        text = 'Some text\n```json\n{"action": "test"}\n```\nMore text'
        result = _parse_json_robust(text)
        assert result["action"] == "test"

    def test_parse_json_robust_partial(self):
        text = '{"action": "test", "content": "unterminated'
        result = _parse_json_robust(text)
        assert "action" in result


class TestEpisodicMemory:
    """Tests para memoria episódica."""

    @pytest.mark.asyncio
    async def test_add_and_retrieve(self):
        memory = EpisodicMemory({"episodic_log_path": "/tmp/test_episodic.jsonl"})
        await memory.record("test_event", "content", metadata={"data": 42})
        events = await memory.get_recent(1)
        assert len(events) == 1
        assert events[0]["event_type"] == "test_event"

    @pytest.mark.asyncio
    async def test_get_recent_limits(self):
        memory = EpisodicMemory({"episodic_log_path": "/tmp/test_episodic2.jsonl"})
        for i in range(5):
            await memory.record(f"event_{i}", f"content {i}", metadata={"i": i})
        events = await memory.get_recent(3)
        assert len(events) == 3


class TestSemanticMemory:
    """Tests para memoria semántica."""

    @pytest.mark.asyncio
    async def test_add_fact(self):
        memory = SemanticMemory({"knowledge_graph_path": "/tmp/test_kg.json"})
        await memory.add_fact("primes", "have_property", "infinite", confidence=0.9)
        facts = await memory.query(subject="primes")
        assert len(facts) >= 1

    @pytest.mark.asyncio
    async def test_query_nonexistent(self):
        memory = SemanticMemory({"knowledge_graph_path": "/tmp/test_kg2.json"})
        facts = await memory.query(subject="nonexistent")
        assert facts == []


class TestSkillLibrary:
    """Tests para la biblioteca de skills."""

    @pytest.mark.asyncio
    async def test_add_and_retrieve(self):
        library = SkillLibrary({"library_path": "/tmp/test_skills"})
        await library.register_skill(
            name="test_skill",
            description="A test skill",
            code="print('hello')"
        )
        skills = await library.retrieve("test")
        assert len(skills) >= 1
        assert skills[0]["name"] == "test_skill"

    @pytest.mark.asyncio
    async def test_retrieve_empty(self):
        library = SkillLibrary({"library_path": "/tmp/test_skills_empty"})
        skills = await library.retrieve("nonexistent")
        assert skills == []
