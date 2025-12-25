# Contributing to Peargent

Thank you for your interest in contributing to Peargent! We welcome contributions from the community and are grateful for any help you can provide.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Please be kind and courteous to others, and focus on constructive feedback.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/peargent.git
   cd peargent
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/Quanta-Naut/peargent.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip or another package manager

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **macOS/Linux**: `source venv/bin/activate`

3. Install the package in development mode with dev dependencies:
   ```bash
   pip install -e .
   ```

4. Copy the environment template and configure your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. Verify your setup by running the basic example:
   ```bash
   python examples/01-getting-started/basic_agent.py
   ```
   You should see the agent output if everything is configured correctly.

## How to Contribute

### Types of Contributions

- 🐛 **Bug fixes**: Help us squash bugs
- ✨ **New features**: Add new capabilities to the framework
- 📝 **Documentation**: Improve docs, examples, or code comments
- 🧪 **Tests**: Add or improve test coverage
- 🔧 **Refactoring**: Improve code quality without changing functionality

### Contribution Workflow

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following our [style guidelines](#style-guidelines)

3. **Test your changes** to ensure nothing is broken

4. **Commit your changes** with a descriptive message:
   ```bash
   git commit -m "feat: add new streaming callback support"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** against the `main` branch

## Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Update documentation if you're adding or changing functionality
3. Add tests for new features
4. Ensure all tests pass locally before submitting
5. Write a clear PR description explaining:
   - What changes you made
   - Why you made them
   - Any breaking changes or migration notes
6. Link any related issues in your PR description

### Commit Message Convention

We follow conventional commits. Use these prefixes:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) conventions
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [Flake8](https://flake8.pycqa.org/) for linting
- Use type hints where possible
- Write docstrings for public functions and classes

### Formatting

Run Black before committing:
```bash
black peargent/
```

Run Flake8 to check for issues:
```bash
flake8 peargent/
```

### Documentation

- Use clear, concise language
- Include code examples where helpful
- Keep docstrings up to date with code changes

## Reporting Bugs

When reporting bugs, please include:

1. **A clear title** describing the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs **actual behavior**
4. **Environment details**:
   - Python version
   - Peargent version
   - Operating system
   - LLM provider being used
5. **Error messages** or stack traces (if applicable)
6. **Minimal code example** that reproduces the issue

[Open a bug report →](https://github.com/Peargent/peargent/issues/new)

## Feature Requests

We love hearing ideas for new features! When submitting a feature request:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** you're trying to solve
3. **Explain your proposed solution**
4. **Consider alternatives** you've thought about
5. **Provide examples** of how the feature would be used

[Request a feature →](https://github.com/Peargent/peargent/issues/new)

## Questions?

If you have questions about contributing, feel free to:

- Open a [GitHub Discussion](https://github.com/Peargent/peargent/discussions)
- Check the [documentation](https://peargent.online)

---

Thank you for contributing to Peargent! 🍐
