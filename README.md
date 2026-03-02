# ai-agent-demo

A demonstration repository showcasing a simple AI agent that uses a tool-calling pattern to process user requests. The agent can perform calculations, fetch weather data, and manage a to-do list.

## Overview

This project implements a lightweight AI agent framework in Python that:

- Parses user intents from natural language input
- Routes requests to the appropriate tool handler
- Maintains conversation context across interactions
- Returns structured responses

## Project Structure

```
.
├── LICENSE
├── README.md
├── DOCS.md
├── requirements.txt
├── agent/
│   ├── __init__.py
│   ├── core.py          # Main agent loop
│   ├── tools.py         # Tool implementations
│   └── parser.py        # Intent parser
└── tests/
    ├── __init__.py
    └── test_agent.py    # Unit tests
```

## Quick Start

```bash
# Clone the repository
git clone https://github.com/humoflife/ai-agent-demo.git
cd ai-agent-demo

# Install dependencies
pip install -r requirements.txt

# Run the agent
python -m agent.core

# Run tests
python -m pytest tests/ -v
```

## Requirements

- Python 3.10+

## License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
