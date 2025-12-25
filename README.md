<p align="center">
  <img src=".github/assets/peargent.png" alt="Peargent Logo">
</p>

# Peargent

[![PyPI version](https://badge.fury.io/py/peargent.svg?bust=1)](https://badge.fury.io/py/peargent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Python framework for building intelligent AI agents with simplicity at its core.

## Features

- **Advanced Tracing** - Track every action, decision, and API call with detailed telemetry and database persistence
- **Smart History Management** - Built-in conversation history with intelligent context windowing and buffer management
- **Multi-LLM Support** - Seamlessly switch between OpenAI, Anthropic, Groq, Gemini, and more
- **Type-Safe Tools** - Pydantic-powered tool system with automatic validation
- **Agent Pools** - Run multiple agents concurrently with shared context
- **Streaming Support** - Real-time streaming responses with event handling
- **Cost Tracking** - Monitor token usage and costs across all LLM providers

## Installation

```bash
pip install peargent
```

## Quick Start

```python
from peargent import create_agent
from peargent.models import groq, anthropic, openai

# Use any model provider
agent = create_agent(
    name="assistant",
    persona="You are a helpful AI assistant.",
    model=anthropic("claude-3-5-sonnet-20241022")  # or groq("llama-3.3-70b-versatile"), openai("gpt-4o")
)

result = agent.run("What is the capital of France?")
print(result)
```

For more examples and detailed documentation, visit [Docs](https://peargent.online).

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

## License

MIT License - see [LICENSE](LICENSE) file for details

