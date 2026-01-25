# Changelog

All notable changes to this project will be documented in this file.

## [0.1.5] - 2026-01-25

### Added
- **Peargent Atlas**: Added support for Peargent Atlas (`peargent.atlas`) to enable visual agent orchestration and project management.
- **New Standard Tools**: Added a suite of powerful tools:
    - `WebSearchTool`: Powered by DuckDuckGo (`ddgs`) to enable agents to perform web searches.
    - `DateTimeTool`: For handling date and time operations, calculations, and timezone conversions.
    - `DiscordTool`: For sending notifications and messages to Discord channels via webhooks.
    - `EmailTool`: For sending emails using SMTP (requires configuration).
    - `TextExtractionTool`: For extracting content from PDFs, Word documents, and HTML pages.
    - `WikipediaKnowledgeTool`: For searching and retrieving summaries from Wikipedia.

### Changed
- **Dependencies**: Added optional dependencies for `web-search` (`ddgs`) and `text-extraction` (`beautifulsoup4`, `pypdf`, `python-docx`).
- **Tests**: Improved test coverage and reliability.
- **Module Organization**: Restricted imports and sorted modules as public vs private API to improve encapsulation and clarity.

