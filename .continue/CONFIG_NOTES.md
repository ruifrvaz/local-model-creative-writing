# Continue.dev Configuration Notes

## Overriding Default Chat System Message

Continue.dev has a code-focused default system message. For science fiction writing, you can override it:

### Method 1: Using Rules (Recommended for Project)

Rules in `.continue/rules/*.md` are automatically prepended to the system message. The rule `scifi_writer.md` provides comprehensive creative writing instructions that override the code-focused defaults.

**How it works:**
1. Rules are loaded in lexicographical order
2. Rules with `alwaysApply: true` are included in every request
3. Rules are joined with newlines to form the complete system message
4. Base chat system message comes last (can be overridden)

**Current setup:**
- `.continue/rules/scifi_writer.md` - Always applied, science fiction writing instructions

### Method 2: Override Base System Message (Model-Level)

For complete control, override the base system message in your config file using `chatOptions.baseSystemMessage`:

**Global config location:** `~/.continue/config.yaml` or `~/.continue/config.json`

**Example YAML configuration:**

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
    chatOptions:
      baseSystemMessage: |
        You are an expert science fiction writing assistant. Your purpose is to help authors 
        craft compelling narratives, develop characters, build fictional universes, and write 
        engaging prose. You do not write code or provide programming assistance.
        
        Focus on:
        - Creative storytelling and narrative structure
        - Character development and dialogue
        - Worldbuilding and scientific plausibility
        - Prose quality and writing craft
        - Story continuity and consistency
    roles:
      - chat
      - edit
      - apply
```

**Example JSON configuration:**

```json
{
  "models": [
    {
      "title": "Llama 3.1 8B (RAG-Enhanced Writing)",
      "provider": "openai",
      "model": "meta-llama/Llama-3.1-8B-Instruct",
      "apiBase": "http://localhost:8001/v1",
      "apiKey": "EMPTY",
      "contextLength": 100000,
      "completionOptions": {
        "temperature": 0.85,
        "maxTokens": 2000
      },
      "chatOptions": {
        "baseSystemMessage": "You are an expert science fiction writing assistant. Your purpose is to help authors craft compelling narratives, develop characters, build fictional universes, and write engaging prose. You do not write code or provide programming assistance.\n\nFocus on:\n- Creative storytelling and narrative structure\n- Character development and dialogue\n- Worldbuilding and scientific plausibility\n- Prose quality and writing craft\n- Story continuity and consistency"
      },
      "roles": ["chat", "edit", "apply"]
    }
  ]
}
```

### Testing Your Configuration

1. **Open Continue chat** (Ctrl+L)
2. **Click the rules icon** (pen icon above toolbar)
3. **Verify** `scifi_writer.md` appears in the rules list
4. **Test with a query:**
   ```
   "Help me write a scene where Elena discovers an alien artifact"
   ```
5. **Expected behavior:** Response should be narrative prose, not code suggestions

### Troubleshooting

**Problem:** Continue still gives code-focused responses

**Solutions:**
1. **Check rules are loaded:** Click rules icon, verify `scifi_writer.md` is listed
2. **Verify alwaysApply:** Rule should have `alwaysApply: true` in frontmatter
3. **Override base message:** Add `chatOptions.baseSystemMessage` to model config
4. **Restart VS Code:** Sometimes needed after config changes

**Problem:** Rules file not showing up

**Solutions:**
1. File must be in `.continue/rules/` (not `.continue/rule/`)
2. File must have `.md` extension
3. YAML frontmatter must be valid (between `---` markers)
4. Restart VS Code to reload rules

**Problem:** Want different behavior for different files

**Solution:** Use `globs` in rule frontmatter:

```yaml
---
name: Dialogue-Specific Rule
globs: ["**/dialogues/*.md", "**/chapters/*.md"]
description: Special handling for dialogue scenes
---

When writing dialogue, ensure each character has a distinct voice...
```

## Configuration File Locations

- **Global (user-level):** `~/.continue/config.yaml` or `~/.continue/config.json`
- **Project (workspace):** `.continue/config.yaml` or `.continue/config.json` (not recommended)
- **Rules (project):** `.continue/rules/*.md` (recommended approach)

## See Also

- Continue.dev Rules Documentation: https://docs.continue.dev/customize/rules
- Config Reference: https://docs.continue.dev/reference#models
- Deep Dive on Rules: https://docs.continue.dev/customize/deep-dives/rules
