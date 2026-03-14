"""Unit tests for the AI agent."""

import pytest

from agent.core import Agent
from agent.parser import parse


class TestParser:
    """Tests for the intent parser."""

    def test_parse_add_todo(self):
        intent = parse("add todo Buy groceries")
        assert intent.tool == "todo"
        assert intent.action == "add"
        assert intent.arguments["title"] == "buy groceries"

    def test_parse_list_todos(self):
        intent = parse("list todos")
        assert intent.tool == "todo"
        assert intent.action == "list"

    def test_parse_delete_todo(self):
        intent = parse("delete todo 2")
        assert intent.tool == "todo"
        assert intent.action == "delete"
        assert intent.arguments["index"] == 2

    def test_parse_complete_todo(self):
        intent = parse("complete todo 1")
        assert intent.tool == "todo"
        assert intent.action == "complete"
        assert intent.arguments["index"] == 1

    def test_parse_weather(self):
        intent = parse("weather in London")
        assert intent.tool == "weather"
        assert intent.action == "get"
        assert intent.arguments["city"] == "london"

    def test_parse_calculator(self):
        intent = parse("calc 2 + 3 * 4")
        assert intent.tool == "calculator"
        assert intent.action == "evaluate"
        assert intent.arguments["expression"] == "2 + 3 * 4"

    def test_parse_help(self):
        intent = parse("help")
        assert intent.tool == "system"
        assert intent.action == "help"

    def test_parse_unknown(self):
        intent = parse("what is the meaning of life")
        assert intent.tool == "system"
        assert intent.action == "unknown"


    def test_parse_empty_input(self):
        """Empty and whitespace-only input should return unknown intent, not crash."""
        intent = parse("")
        assert intent.tool == "system"
        assert intent.action == "unknown"

    def test_parse_whitespace_only(self):
        """Whitespace-only input should return unknown intent, not crash."""
        intent = parse("   ")

    def test_parse_none_input(self):
        """None input should return unknown intent, not crash."""
        intent = parse(None)
        assert intent.tool == "system"
        assert intent.action == "unknown"

    def test_parse_help_prefix_no_match(self):
        """Words starting with 'help' (e.g. 'helpful') should not trigger help."""
        intent = parse("helpful hints")
        assert intent.tool == "system"
        assert intent.action == "unknown"


class TestTodoTool:
    """Tests for the to-do tool."""

    def test_add_todo(self):
        agent = Agent()
        result = agent.process("add todo Buy milk")
        assert result.success is True
        assert "buy milk" in result.message.lower()

    def test_add_whitespace_only_todo(self):
        """Whitespace-only titles should be rejected, not added as blank todos."""
        from agent.tools import TodoTool

        tool = TodoTool()
        result = tool._add("   ")
        assert result.success is False
        assert tool.todos == []

    def test_list_empty(self):
        agent = Agent()
        result = agent.process("list todos")
        assert result.success is True
        assert result.data["todos"] == []

    def test_add_and_list(self):
        agent = Agent()
        agent.process("add todo First task")
        agent.process("add todo Second task")
        result = agent.process("list todos")
        assert len(result.data["todos"]) == 2

    def test_delete_todo(self):
        """Deleting todo 1 should remove the first item.

        The parser produces 1-based indices. After adding two items,
        'delete todo 1' should remove the first one, leaving only
        the second.
        """
        agent = Agent()
        agent.process("add todo First")
        agent.process("add todo Second")
        result = agent.process("delete todo 1")
        assert result.success is True

        remaining = agent.process("list todos")
        assert len(remaining.data["todos"]) == 1
        # After deleting 'First', only 'Second' should remain
        assert remaining.data["todos"][0]["title"] == "second"

    def test_complete_todo(self):
        agent = Agent()
        agent.process("add todo Do laundry")
        result = agent.process("complete todo 1")
        assert result.success is True

        listing = agent.process("list todos")
        assert listing.data["todos"][0]["status"] == "done"


class TestWeatherTool:
    """Tests for the weather tool."""

    def test_known_city(self):
        agent = Agent()
        result = agent.process("weather in London")
        assert result.success is True
        assert "cloudy" in result.message.lower()

    def test_unknown_city(self):
        agent = Agent()
        result = agent.process("weather in Atlantis")
        assert result.success is False

    def test_weather_data_keys(self):
        """The weather response data should use 'temp_c' to match
        the internal data model and documentation.
        """
        agent = Agent()
        result = agent.process("weather in Tokyo")
        assert "temp_c" in result.data, (
            f"Expected 'temp_c' key in weather data, got: {list(result.data.keys())}"
        )
        assert result.data["temp_c"] == 28


class TestCalculatorTool:
    """Tests for the calculator tool."""

    def test_simple_addition(self):
        agent = Agent()
        result = agent.process("calc 2 + 3")
        assert result.success is True
        assert result.data["result"] == 5

    def test_complex_expression(self):
        agent = Agent()
        result = agent.process("calc (10 + 5) * 2")
        assert result.success is True
        assert result.data["result"] == 30

    def test_division_by_zero(self):
        agent = Agent()
        result = agent.process("calc 1 / 0")
        assert result.success is False

    def test_invalid_characters(self):
        agent = Agent()
        result = agent.process("calc import os")
        assert result.success is False

    def test_non_numeric_result_empty_tuple(self):
        """eval('()') returns an empty tuple, not a number — should fail."""
        from agent.tools import CalculatorTool

        calc = CalculatorTool()
        result = calc._evaluate("()")
        assert result.success is False

    def test_non_numeric_result_ellipsis(self):
        """eval('...') returns Ellipsis, not a number — should fail."""
        from agent.tools import CalculatorTool

        calc = CalculatorTool()
        result = calc._evaluate("...")
        assert result.success is False


class TestAgentIntegration:
    """Integration tests for the full agent loop."""

    def test_help_command(self):
        agent = Agent()
        result = agent.process("help")
        assert result.success is True
        assert "Available commands" in result.message

    def test_unknown_command(self):
        agent = Agent()
        result = agent.process("fly me to the moon")
        assert result.success is False

    def test_history_tracking(self):
        agent = Agent()
        agent.process("help")
        agent.process("calc 1 + 1")
        # Each process call adds a user entry and an agent entry
        assert len(agent.history) == 4
