# DOCS.md - AI Agent Demo Documentation

## Architecture

The demo implements a minimal agent framework with three layers:

```
User Input -> Parser -> Agent Core -> Tool -> Response
```

### 1. Parser (`agent/parser.py`)

The parser uses regex pattern matching to convert natural language input into structured `Intent` objects. Each intent contains:

- **tool** - which tool should handle the request (e.g., `todo`, `weather`, `calculator`)
- **action** - what operation to perform (e.g., `add`, `delete`, `get`, `evaluate`)
- **arguments** - extracted parameters (e.g., `{"title": "Buy milk"}`)

### 2. Agent Core (`agent/core.py`)

The `Agent` class ties everything together:

- Initializes a `ToolRegistry` with the built-in tools
- Accepts user input via the `process()` method
- Dispatches intents to the correct tool
- Maintains a conversation `history` list

### 3. Tools (`agent/tools.py`)

Three tools are included:

| Tool | Actions | Description |
|------|---------|-------------|
| `TodoTool` | add, list, delete, complete | In-memory to-do list manager |
| `WeatherTool` | get | Simulated weather lookup for 5 cities |
| `CalculatorTool` | evaluate | Safe arithmetic evaluation |

All tools return a `ToolResult` dataclass with `success`, `message`, and `data` fields.

## Supported Commands

```
add todo <title>       Add a new to-do item
list todos             Show all to-do items
delete todo <number>   Delete a to-do by its number
complete todo <number> Mark a to-do as done
weather in <city>      Get weather (london, new york, tokyo, paris, sydney)
calc <expression>      Evaluate arithmetic (e.g., calc 2 + 3 * 4)
help                   Show available commands
```

## Running Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

The test suite covers:

- **Parser tests** - Verifies intent extraction for all command patterns
- **Todo tests** - Add, list, delete, complete operations
- **Weather tests** - Known city lookup, unknown city handling, response structure
- **Calculator tests** - Arithmetic, complex expressions, division by zero, invalid input
- **Integration tests** - Help output, unknown commands, history tracking

## Data Model

### Intent

| Field | Type | Description |
|-------|------|-------------|
| `tool` | `str` | Target tool name |
| `action` | `str` | Operation to perform |
| `arguments` | `dict` | Extracted parameters |
| `raw_input` | `str` | Original user text |

### ToolResult

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the operation succeeded |
| `message` | `str` | Human-readable result message |
| `data` | `dict` | Structured response payload |

## Weather Response Schema

The `WeatherTool` returns data in the following shape:

```json
{
  "city": "London",
  "temp_c": 12,
  "condition": "Cloudy",
  "humidity": 78
}
```

Note: The `temp_c` key matches the internal data model and should be used by consumers to read the temperature in Celsius.
