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
   ./serve_vllm.sh                    # Terminal 1: vLLM
   ./serve_rag_proxy.sh scifi_world   # Terminal 2: RAG proxy
   ```

4. **Open VS Code** and press `Ctrl+L` to chat with your AI writing assistant

5. **Verify rules are loaded:** Click rules icon (pen above toolbar), confirm `scifi_writer.md` appears

## Directory Structure

```
.continue/
├── README.md                    # This file
├── rules/
│   └── scifi_writer.md          # Creative writing rules (auto-applied)
└── benchmarks/
    ├── VALIDATION_RESULTS.md    # Configuration test results
    └── rag_comparison_samples.md # RAG vs Direct comparison examples
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

## How Rules Work

Rules in `.continue/rules/*.md` override Continue's default code-focused behavior:

1. Rules are loaded in **lexicographical order**
2. Rules with `alwaysApply: true` are included in every request
3. Rules are prepended to the system message
4. RAG proxy (port 8001) automatically injects worldbuilding context

**Current setup:** `scifi_writer.md` — Always applied, science fiction writing instructions

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Open chat panel |
| `Ctrl+I` | Inline edit selection |
| `Ctrl+Shift+R` | Refactor selection |
| `Ctrl+Shift+M` | Add file to context |

## Configuration Presets

### Creative Writing (Default)
```yaml
completionOptions:
  temperature: 0.85
  presence_penalty: 0.6
  maxTokens: 2000
```

### Technical Descriptions
```yaml
completionOptions:
  temperature: 0.6
  maxTokens: 800
```

### Dialogue
```yaml
completionOptions:
  temperature: 0.9
  presence_penalty: 0.7
  maxTokens: 1500
```

## Advanced: Override Base System Message

For complete control, add `chatOptions.baseSystemMessage` to your model config:

```yaml
models:
  - name: Llama 3.1 8B (RAG-Enhanced Writing)
    provider: openai
    model: meta-llama/Llama-3.1-8B-Instruct
    apiBase: http://localhost:8001/v1
    apiKey: EMPTY
    chatOptions:
      baseSystemMessage: |
        You are an expert science fiction writing assistant. Your purpose is to help authors 
        craft compelling narratives, develop characters, build fictional universes, and write 
        engaging prose. You do not write code or provide programming assistance.
```

## Advanced: File-Specific Rules

Use `globs` in rule frontmatter to apply rules only to certain files:

```yaml
---
name: Dialogue-Specific Rule
globs: ["**/dialogues/*.md", "**/chapters/*.md"]
description: Special handling for dialogue scenes
---

When writing dialogue, ensure each character has a distinct voice...
```

## Testing RAG Integration

Compare **Port 8001** (RAG) vs **Port 8000** (Direct) with:
> "Write a 200-word scene about Captain Vasquez"

**With RAG:** Uses character profiles, worldbuilding, established crew names  
**Without RAG:** Generic names, no universe connection

See `benchmarks/rag_comparison_samples.md` for example outputs.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Code-focused responses | Check rules icon shows `scifi_writer.md` is loaded |
| Rules not showing | Restart VS Code; verify file is in `rules/` with `.md` extension |
| Connection errors | Verify servers on ports 8000 and 8001: `curl http://localhost:8000/health` |
| Responses ignore worldbuilding | Test RAG: `cd ~/scifi-llm/RAG && benchmarks/4_query.py --interactive` |

## Configuration File Locations

| Location | Purpose |
|----------|---------|
| `~/.continue/config.yaml` | Global (user-level) config |
| `.continue/rules/*.md` | Project rules (recommended) |

## See Also

- [Continue.dev Rules Documentation](https://docs.continue.dev/customize/rules)
- [Config Reference](https://docs.continue.dev/reference#models)
- [benchmarks/VALIDATION_RESULTS.md](benchmarks/VALIDATION_RESULTS.md) — Test results
- [docs/VSCODE_WRITING_SETUP.md](../docs/VSCODE_WRITING_SETUP.md) — Complete VS Code setup guide
