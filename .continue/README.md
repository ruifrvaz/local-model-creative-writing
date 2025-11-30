# Continue.dev Configuration for Science Fiction Writing

This directory contains Continue.dev configuration for creative writing assistance, optimized for science fiction authorship rather than code generation.

## Quick Start

1. **Install Continue.dev** extension in VS Code

2. **Configure your model** in `~/.continue/config.yaml`:
   ```yaml
   models:
     - name: Llama 3.1 8B (RAG-Enhanced Writing)
       provider: openai
       model: meta-llama/Llama-3.1-8B-Instruct
       apiBase: http://localhost:8001/v1
       apiKey: EMPTY
       contextLength: 100000
       completionOptions:
         temperature: 0.85
         maxTokens: 2000
   ```

3. **Start the servers:**
   ```bash
   # Terminal 1: vLLM server
   ./serve_vllm.sh
   
   # Terminal 2: RAG proxy
   ./serve_rag_proxy.sh scifi_world
   ```

4. **Open VS Code** and press `Ctrl+L` to chat with your AI writing assistant

## Directory Structure

```
.continue/
├── README.md                # This file
├── CONFIG_NOTES.md          # Detailed configuration reference
├── rules/
│   └── scifi_writer.md      # Creative writing rules (auto-applied)
└── benchmarks/
    └── VALIDATION_RESULTS.md # Configuration test results
```

## How It Works

- **Rules** in `rules/` are automatically prepended to every request
- `scifi_writer.md` overrides Continue's default code-focused behavior
- Responses focus on narrative prose, not code generation
- RAG proxy (port 8001) automatically injects worldbuilding context

## Key Features

| Feature | Benefit |
|---------|---------|
| Creative writing focus | Narrative prose instead of code blocks |
| RAG integration | Automatic character/worldbuilding context |
| Always-on rules | No manual activation needed |
| Local inference | Privacy-first, no cloud APIs |

## Testing Your Setup

1. Open Continue chat (`Ctrl+L`)
2. Click the rules icon (pen above toolbar)
3. Verify `scifi_writer.md` appears in rules list
4. Test with: "Write a scene where Elena discovers an alien artifact"
5. Response should be narrative prose, not code

## Troubleshooting

**Code-focused responses:** Check rules icon shows `scifi_writer.md` is loaded

**Rules not showing:** Restart VS Code after adding rule files

**Connection errors:** Verify servers running on ports 8000 and 8001

## See Also

- [CONFIG_NOTES.md](CONFIG_NOTES.md) — Advanced configuration options
- [benchmarks/VALIDATION_RESULTS.md](benchmarks/VALIDATION_RESULTS.md) — Test results
- [docs/VSCODE_WRITING_SETUP.md](../docs/VSCODE_WRITING_SETUP.md) — Complete VS Code setup guide
