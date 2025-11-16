<p align="center">
  <img src=".github/assets/peargent.png" alt="Peargent Logo">
</p>

# Peargent

[![PyPI version](https://badge.fury.io/py/peargent.svg?bust=1)](https://badge.fury.io/py/peargent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Python framework for building intelligent AI agents with advanced tracing, history management, and seamless LLM integration.

## Features

- **Advanced Tracing** - Track every action, decision, and API call with detailed telemetry and database persistence
- **Smart History Management** - Built-in conversation history with intelligent context windowing and buffer management
- **Multi-LLM Support** - Seamlessly switch between OpenAI, Anthropic, Groq, and more
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
from peargent.models import groq

agent = create_agent(
    name="assistant",
    persona="You are a helpful AI assistant.",
    model=groq("llama-3.3-70b-versatile")
)

result = agent.run("What is the capital of France?")
print(result)
```

For more examples and detailed documentation, visit the [Documentation](your-docs-url-here).


## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Created by [Quanta-Naut](https://github.com/Quanta-Naut)

