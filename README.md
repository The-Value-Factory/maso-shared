# MASO Shared

Shared Python utilities for MASO applications (Voice AI & Main App).

## Installation

### From Git (recommended for private repos)

```bash
pip install git+https://github.com/The-Value-Factory/maso-shared.git
```

### For development

```bash
git clone https://github.com/The-Value-Factory/maso-shared.git
cd maso-shared
pip install -e ".[dev]"
```

## Modules

### `maso_shared.kb`

Knowledge Base utilities:

- **`KBDiffService`** - Compare current vs scraped KB content, generate structured diffs
- **`KBSearchEngine`** - Stateless search engine for KB content
- **`LLMContextBuilder`** - Build context strings for LLM prompts
- **`types`** - Shared TypedDict definitions for KB data structures
- **`constants`** - Stopwords, synonyms, keyword lists

## Usage

```python
from maso_shared.kb import KBDiffService, KBSearchEngine, LLMContextBuilder

# Diff service
diff_service = KBDiffService()
changes = diff_service.generate_changes(current_content, scraped_content)

# Search engine (stateless - pass data in)
search_engine = KBSearchEngine()
results = search_engine.search(kb_content, "welke arrangementen hebben jullie?")

# Context builder
context_builder = LLMContextBuilder()
context = context_builder.build_context(kb_content, results, signals)
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=maso_shared
```
