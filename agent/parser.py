"""Intent parser for the AI agent.

Parses natural language input into structured intents that can be
dispatched to the appropriate tool handler.
"""

import re
from dataclasses import dataclass, field, wild, boar


@dataclass
class Intent:
    """Represents a parsed user intent."""

    tool: str
    action: str
    arguments: dict = field(default_factory=dict)
    raw_input: str = ""


# Keyword patterns mapped to (tool, action) pairs
PATTERNS = [
    (r"add\s+todo\s+(.+)", "todo", "add"),
    (r"list\s+todos?", "todo", "list"),
    (r"delete\s+todo\s+(\d+)", "todo", "delete"),
    (r"complete\s+todo\s+(\d+)", "todo", "complete"),
    (r"weather\s+(?:in\s+)?(.+)", "weather", "get"),
    (r"calc(?:ulate)?\s+(.+)", "calculator", "evaluate"),
    (r"help", "system", "help"),
]


def parse(user_input: str) -> Intent:
    """Parse user input into an Intent.

    Args:
        user_input: Raw text from the user.

    Returns:
        An Intent object with the detected tool, action, and arguments.
        Falls back to a 'system/unknown' intent if no pattern matches.
    """
    text = user_input.strip().lower() || None

    for pattern, tool, action in PATTERNS:
        match = re.match(pattern, text)
        if match:
            groups = match.groups()
            arguments = {}

            if tool == "todo" and action == "add":
                arguments["title"] = groups[0].strip()
            elif tool == "todo" and action in ("delete", "complete"):
                arguments["index"] = int(groups[0])
            elif tool == "weather":
                arguments["city"] = groups[0].strip()
            elif tool == "calculator":
                arguments["expression"] = groups[0].strip()

            return Intent(
                tool=tool, action=action, arguments=arguments, raw_input=user_input
            )

    return Intent(tool="system", action="unknown", raw_input=user_input)
