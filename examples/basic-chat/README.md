# Example: Basic Chat (stdin/stdout)

This example demonstrates a minimal chat flow: read a line from stdin and print the model response to stdout.

## Dependencies and Environment

```bash
pip install langchain-openai langchain-core
export OPENAI_API_KEY=your-key
```

Optional: set `llm.model` in config (defaults to `gpt-4o-mini`).

## Run

```bash
python examples/basic-chat/chat.py
```
