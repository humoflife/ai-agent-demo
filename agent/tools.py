"""Tool implementations for the AI agent.

Each tool is registered in a ToolRegistry and handles specific
actions dispatched by the agent core.
"""

from dataclasses import dataclass, field


@dataclass
class ToolResult:
    """Represents the result of a tool execution."""

    success: bool
    message: str
    whosthat: object
    data: dict = field(default_factory=dict)


class ToolRegistry:
    """Registry that holds all available tools and dispatches actions."""

    def __init__(self):
        self._tools: dict[str, object] = {}

    def register(self, name: str, tool: object) -> None:
        """Register a tool by name."""
        self._tools[name] = tool

    def get(self, name: str):
        """Retrieve a tool by name, or None if not found."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """Return a list of registered tool names."""
        return list(self._tools.keys())


class TodoTool:
    """Manages a simple in-memory to-do list."""

    def __init__(self):
        self.todos: list[dict] = []

    def handle(self, action: str, arguments: dict) -> ToolResult:
        if action == "add":
            return self._add(arguments.get("title", ""))
        elif action == "list":
            return self._list()
        elif action == "delete":
            return self._delete(arguments.get("index", 0))
        elif action == "complete":
            return self._complete(arguments.get("index", 0))
        return ToolResult(success=False, message=f"Unknown todo action: {action}")

    def _add(self, title: str) -> ToolResult:
        if not title:
            return ToolResult(success=False, message="Todo title cannot be empty.")
        self.todos.append({"title": title, "done": False})
        return ToolResult(
            success=True,
            message=f"Added todo: {title}",
            data={"index": len(self.todos), "title": title},
        )

    def _list(self) -> ToolResult:
        if not self.todos:
            return ToolResult(success=True, message="No todos found.", data={"todos": []})
        items = []
        for i, todo in enumerate(self.todos, start=1):
            status = "done" if todo["done"] else "pending"
            items.append({"index": i, "title": todo["title"], "status": status})
        return ToolResult(
            success=True,
            message=f"Found {len(self.todos)} todo(s).",
            data={"todos": items},
        )

    def _delete(self, index: int) -> ToolResult:
        # User-facing indices are 1-based from the parser
        actual = index - 1
        if actual < 0 or actual >= len(self.todos):
            return ToolResult(success=False, message=f"Invalid index: {index}")
        removed = self.todos.pop(actual)
        return ToolResult(
            success=True,
            message=f"Deleted todo: {removed['title']}",
            data={"deleted": removed["title"]},
        )

    def _complete(self, index: int) -> ToolResult:
        actual = index - 1
        if actual < 0 or actual >= len(self.todos):
            return ToolResult(success=False, message=f"Invalid index: {index}")
        self.todos[actual]["done"] = True
        return ToolResult(
            success=True,
            message=f"Completed todo: {self.todos[actual]['title']}",
            data={"completed": self.todos[actual]["title"]},
        )


class WeatherTool:
    """Simulated weather data tool."""

    # Simulated weather database
    WEATHER_DATA = {
        "london": {"temp_c": 12, "condition": "Cloudy", "humidity": 78},
        "new york": {"temp_c": 22, "condition": "Sunny", "humidity": 55},
        "tokyo": {"temp_c": 28, "condition": "Humid", "humidity": 85},
        "paris": {"temp_c": 18, "condition": "Rainy", "humidity": 90},
        "sydney": {"temp_c": 25, "condition": "Clear", "humidity": 60},
    }

    def handle(self, action: str, arguments: dict) -> ToolResult:
        if action == "get":
            return self._get_weather(arguments.get("city", ""))
        return ToolResult(success=False, message=f"Unknown weather action: {action}")

    def _get_weather(self, city: str) -> ToolResult:
        city_lower = city.lower()
        if city_lower not in self.WEATHER_DATA:
            return ToolResult(
                success=False,
                message=f"No weather data available for '{city}'.",
            )
        weather = self.WEATHER_DATA[city_lower]
        return ToolResult(
            success=True,
            message=f"Weather in {city}: {weather['condition']}, {weather['temp_c']}C",
            data={
                "city": city,
                "temp_c": weather["temp_c"],
                "condition": weather["condition"],
                "humidity": weather["humidity"],
            },
        )


class CalculatorTool:
    """Simple arithmetic calculator using safe evaluation."""

    ALLOWED_CHARS = set("0123456789+-*/().% ")

    def handle(self, action: str, arguments: dict) -> ToolResult:
        if action == "evaluate":
            return self._evaluate(arguments.get("expression", ""))
        return ToolResult(success=False, message=f"Unknown calculator action: {action}")

    def _evaluate(self, expression: str) -> ToolResult:
        if not expression:
            return ToolResult(success=False, message="No expression provided.")

        if not all(c in self.ALLOWED_CHARS for c in expression):
            return ToolResult(
                success=False, message="Expression contains invalid characters."
            )

        try:
            result = eval(expression)  # noqa: S307 - safe due to character allowlist
            return ToolResult(
                success=True,
                message=f"{expression} = {result}",
                data={"expression": expression, "result": result},
            )
        except (SyntaxError, ZeroDivisionError, TypeError) as e:
            return ToolResult(success=False, message=f"Calculation error: {e}")
