# VS Code Science Fiction Writing Setup

Configure VS Code to use your local RAG-enhanced vLLM for agentic science fiction writing.

## Architecture

```
VS Code Extension → Port 8001 (RAG Proxy) → Port 8000 (vLLM)
                         ↓
                    Auto-retrieves:
                    - Character profiles
                    - Worldbuilding details
                    - Plot continuity
                    - Writing style guides
```

## Prerequisites

1. **RAG Setup Complete:**
   ```bash
   cd ~/scifi-llm/RAG
   ./0_create_venv_with_deps.sh
   ./1_ingest.py
   ./2_embed_and_store.py
   ```

2. **Servers Running:**
   ```bash
   # Terminal 1: vLLM
   cd ~/scifi-llm
   ./serve_vllm.sh
   
   # Terminal 2: RAG Proxy
   ./serve_rag_proxy.sh scifi_world
   ```

## VS Code Extension Setup

### Option 1: Continue.dev (Recommended)

**Install Extension:**
- Open VS Code
- Install "Continue" extension
- Press `Ctrl+Shift+P` → "Continue: Open Config"

**Configure `~/.continue/config.json`:**
```json
{
  "models": [
    {
      "title": "Llama 3.1 8B (RAG-Enhanced)",
      "provider": "openai",
      "model": "meta-llama/Llama-3.1-8B-Instruct",
      "apiBase": "http://localhost:8001/v1",
      "apiKey": "EMPTY",
      "contextLength": 100000,
      "completionOptions": {
        "temperature": 0.85,
        "maxTokens": 2000
      }
    },
    {
      "title": "Llama 3.1 8B (Direct, No RAG)",
      "provider": "openai",
      "model": "meta-llama/Llama-3.1-8B-Instruct",
      "apiBase": "http://localhost:8000/v1",
      "apiKey": "EMPTY",
      "contextLength": 100000,
      "completionOptions": {
        "temperature": 0.85,
        "maxTokens": 2000
      }
    }
  ]
}
```

**Usage:**
- Open your science fiction manuscript
- Press `Ctrl+L` to open Continue chat
- Select "Llama 3.1 8B (RAG-Enhanced)"
- Ask questions - automatically gets context from your worldbuilding docs!

**Examples:**
```
"Describe Elena's reaction to seeing the alien homeworld for the first time"
→ Auto-retrieves: Elena's personality, alien planet description, previous reactions

"Write the next scene where the crew discovers the ancient artifact"
→ Auto-retrieves: Crew roster, artifact lore, previous discoveries

"How would Elena address the crew after the battle?"
→ Auto-retrieves: Elena's leadership style, battle details, crew dynamics
```

### Option 2: Cody by Sourcegraph

**Install Extension:**
- Install "Cody" extension
- Settings → "Cody: Custom Configuration"

**Configure `.vscode/settings.json`:**
```json
{
  "cody.serverEndpoint": "http://localhost:8001",
  "cody.autocomplete.enabled": true,
  "cody.autocomplete.languages": {
    "*": true
  }
}
```

### Option 3: GitHub Copilot (Advanced)

GitHub Copilot doesn't officially support custom endpoints, but you can use a proxy:

**Configure via proxy:**
```bash
# Use a tool like mitmproxy to redirect Copilot traffic
# This is complex - Continue.dev is recommended instead
```

## VS Code Settings for Science Fiction Writing

**Create `.vscode/settings.json` in your manuscript folder:**
```json
{
  "files.associations": {
    "*.md": "markdown"
  },
  "markdown.extension.toc.levels": "1..6",
  "editor.wordWrap": "on",
  "editor.lineNumbers": "off",
  "editor.minimap.enabled": false,
  "editor.fontSize": 14,
  "editor.fontFamily": "'Courier New', monospace",
  "workbench.colorTheme": "Quiet Light",
  
  "continue.telemetryEnabled": false,
  "continue.enableTabAutocomplete": true
}
```

## Workflow: Agentic Science Fiction Writing

### 1. Document Your World

```
your-manuscript/
├── worldbuilding/
│   ├── species/
│   │   ├── arcturians.md
│   │   └── humans.md
│   ├── planets/
│   │   ├── arcturus-iv.md
│   │   └── earth.md
│   └── technology/
│       ├── ftl-drives.md
│       └── weapons.md
├── characters/
│   ├── elena-vasquez.md
│   ├── commander-chen.md
│   └── dr-malik.md
├── chapters/
│   ├── chapter-01.md
│   ├── chapter-02.md
│   └── outline.md
└── style-guides/
    ├── voice.md
    └── conventions.md
```

### 2. Embed Your Documents

```bash
# Copy to RAG data directory
cp -r your-manuscript/* ~/scifi-llm/RAG/data/

# Re-embed
cd ~/scifi-llm/RAG
./1_ingest.py
./2_embed_and_store.py --collection scifi_world

# Restart RAG proxy to pick up changes
# Ctrl+C in Terminal 2, then:
cd ~/scifi-llm
./serve_rag_proxy.sh scifi_world
```

### 3. Write with AI Assistance

**In VS Code with Continue:**

```
You: "I need to write a scene where Elena meets the Arcturian ambassador"

AI: [Retrieves context automatically]
- Elena's diplomatic experience from characters/elena-vasquez.md
- Arcturian biology and culture from worldbuilding/species/arcturians.md
- Previous first contact protocol from chapters/chapter-03.md

AI: "Captain Elena Vasquez stood at the airlock, her hand instinctively 
checking her translator implant. The Arcturians, she reminded herself, 
could sense emotional states through their telepathic abilities. She 
steadied her breathing, projecting calm confidence as the door cycled..."
```

**Query Examples:**
- "What color are Arcturian eyes?" → Retrieves species description
- "Has Elena been to this planet before?" → Searches chapter summaries
- "Write dialogue showing Elena's leadership style" → References character profile
- "Continue this scene maintaining the established tone" → Uses style guide

### 4. Maintain Continuity

**Before writing a new chapter:**
```
You: "Summarize what happened in the last 3 chapters"

AI: [Retrieves from chapters/]
- Chapter summaries
- Character development arcs
- Plot threads

You: "What unresolved plot threads should I address?"

AI: [Retrieves and analyzes]
- Artifact mystery from chapter 2
- Elena's promise to the crew in chapter 5
- Alien signal detected in chapter 7
```

### 5. Consistency Checks

```
You: "Does this description of the FTL drive match what I wrote earlier?"

AI: [Retrieves from worldbuilding/technology/ftl-drives.md]
"Your earlier description specified a 'quantum entanglement drive' 
powered by exotic matter, but this passage mentions 'warp coils.' 
Let me suggest a revision..."
```

## Performance Tuning

### For Creative Writing (Default)
```json
{
  "completionOptions": {
    "temperature": 0.85,        // Creative but not random
    "top_p": 0.95,             // Diverse word choices
    "presence_penalty": 0.6,   // Avoid repetition
    "frequency_penalty": 0.3,  // Slight variation
    "maxTokens": 2000          // Longer responses
  }
}
```

### For Technical Descriptions
```json
{
  "completionOptions": {
    "temperature": 0.6,        // More factual
    "maxTokens": 800
  }
}
```

### For Dialogue
```json
{
  "completionOptions": {
    "temperature": 0.9,        // Natural variation
    "presence_penalty": 0.7,   // Unique voices
    "maxTokens": 1500
  }
}
```

## Keyboard Shortcuts (Continue.dev)

| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Open chat |
| `Ctrl+I` | Inline edit |
| `Ctrl+Shift+R` | Refactor selection |
| `Ctrl+Shift+M` | Add to context |

## Troubleshooting

### "Model not responding"
```bash
# Check RAG proxy is running
curl http://localhost:8001/health

# Check vLLM is running
curl http://localhost:8000/health

# Restart if needed
cd ~/scifi-llm
./serve_rag_proxy.sh scifi_world
```

### "Responses don't use my worldbuilding"
```bash
# Check documents are embedded
cd ~/scifi-llm/RAG
./3_test_retrieval.py --interactive

# Try query: "What are Arcturians?"
# Should return relevant chunks
```

### "Context is wrong/outdated"
```bash
# Re-embed documents
cd ~/scifi-llm/RAG
./1_ingest.py --force
./2_embed_and_store.py --collection scifi_world

# Restart proxy
# Ctrl+C in RAG proxy terminal, then:
cd ~/scifi-llm
./serve_rag_proxy.sh scifi_world
```

### "Responses are too generic"
- Increase `top_k` to retrieve more context
- Check document chunking size (should be 1000-1500 chars for narrative)
- Verify documents are well-structured with clear headers

## Tips for Best Results

### 1. Structure Your Documents Well
```markdown
# Character: Captain Elena Vasquez

## Basic Info
- Age: 38
- Rank: Captain
- Ship: ISS Endeavor

## Personality
- Driven by duty
- Protective of crew
- Cautious in first contact

## Background
- Colony survivor
- Military academy graduate
- 15 years in fleet
```

### 2. Use Consistent Naming
- Always refer to "Captain Elena Vasquez" not "Elena" / "the Captain" / "Vasquez"
- Makes retrieval more accurate

### 3. Update Documents Regularly
```bash
# After writing new chapters
cp your-manuscript/chapters/chapter-10.md ~/scifi-llm/RAG/data/chapters/
cd ~/scifi-llm/RAG
./1_ingest.py
./2_embed_and_store.py
```

### 4. Test Retrieval Quality
```bash
cd ~/scifi-llm/RAG
./3_test_retrieval.py --interactive

# Try queries like:
"Elena's background"
"Arcturian culture"
"FTL technology"
```

### 5. Use Specific Prompts
❌ "Write a scene"
✅ "Write a scene where Elena negotiates with the Arcturian ambassador, showing her diplomatic experience and the cultural protocols I established"

## Advanced: Custom RAG Context

You can customize what context gets retrieved by modifying `5_serve_rag_proxy.py`:

```python
# Adjust retrieval parameters
def retrieve_context(query: str, top_k: int = 5) -> str:
    # For character queries, search more broadly
    if "character" in query.lower() or "personality" in query.lower():
        top_k = 10
    
    # For worldbuilding, prioritize recent documents
    if "planet" in query.lower() or "species" in query.lower():
        # Add recency weighting
        pass
    
    # ... existing code ...
```

## Summary

Your setup:
- ✅ Local vLLM (GPU-accelerated, private)
- ✅ RAG proxy (auto-retrieves your worldbuilding)
- ✅ VS Code integration (seamless writing experience)
- ✅ Maintains continuity (characters, plot, world)