"""Core agent loop.

Wires together the parser, tool registry, and conversation history
to form a simple interactive agent.
"""

from agent.parser import parse
from agent.tools import (
    CalculatorTool,
    TodoTool,
    ToolRegistry,
    ToolResult,
    WeatherTool,
)


class Agent:
    """A simple tool-calling agent."""

    def __init__(self):
        self.registry = ToolRegistry()
        self.history: list[dict] = []
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register the built-in tools."""
        self.registry.register("todo", TodoTool())
        self.registry.register("weather", WeatherTool())
        self.registry.register("calculator", CalculatorTool())

    def process(self, user_input: str) -> ToolResult:
        """Process a single user input and return a ToolResult.

        Args:
            user_input: The raw text from the user.

        Returns:
            A ToolResult with the outcome of the dispatched tool.
        """
        intent = parse(user_input)

        # Record in history
        self.history.append({"role": "user", "content": user_input, "intent": intent})

        # Handle built-in system commands
        if intent.tool == "system":
            result = self._handle_system(intent.action)
        else:
            tool = self.registry.get(intent.tool)
            if tool is None:
                result = ToolResult(
                    success=False, message=f"Unknown tool: {intent.tool}"
                )
            else:
                result = tool.handle(intent.action, intent.arguments)

        self.history.append({"role": "agent", "content": result.message})
        return result

    def _handle_system(self, action: str) -> ToolResult:
        if action == "help":
            tools = self.registry.list_tools()
            return ToolResult(
                success=True,
                message=(
                    "Available commands:\n"
                    "  add todo <title>     - Add a new todo\n"
                    "  list todos           - List all todos\n"
                    "  delete todo <n>      - Delete todo by number\n"
                    "  complete todo <n>    - Mark todo as done\n"
                    "  weather in <city>    - Get weather for a city\n"
                    "  calc <expression>    - Evaluate a math expression\n"
                    "  help                 - Show this message"
                ),
                data={"tools": tools},
            )
        return ToolResult(
            success=False,
            message="I didn't understand that. Type 'help' for available commands.",
        )


def main() -> None:
    """Run the agent in interactive mode."""
    agent = Agent()
    print("AI Agent Demo (type 'help' for commands, Ctrl+C to exit)")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            result = agent.process(user_input)
            print(f"Agent: {result.message}")
            print()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
