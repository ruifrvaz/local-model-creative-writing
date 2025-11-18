# Configure Continue.dev for Creative Writing

**Priority:** 2  
**Status:** Not Started  
**Created:** 2025-11-18

## Description

Continue.dev has a default system context optimized for code assistance. It needs to be reconfigured for creative science fiction writing instead. The chat responses are currently too code-oriented and need a writing-focused system prompt.

## Problem

- Continue assumes coding use case by default
- System prompts reference code completion, refactoring, debugging
- Need to shift context to: creative writing, narrative consistency, worldbuilding

## Acceptance Criteria

- [ ] Locate Continue.dev system prompt configuration
- [ ] Create custom system prompt for science fiction writing
- [ ] Configure prompt to emphasize:
  - Creative narrative generation
  - Character consistency
  - Worldbuilding adherence
  - Dialogue and prose quality
  - NO code-specific instructions
- [ ] Test that chat responses focus on writing, not coding
- [ ] Document configuration in `chatUI/README.md`

## Research Needed

- Continue.dev system prompt configuration location
- Options: `.continue/config.yaml`, custom prompts, rules system
- Check if Continue supports custom system prompts per model
- Investigate `.continue/rules/` directory for context injection

## Potential Solutions

1. **Custom system prompt in config:**
   ```yaml
   models:
     - name: Creative Writing Assistant
       systemMessage: "You are a science fiction writing assistant..."
   ```

2. **Continue rules system:**
   - `.continue/rules/` directory for custom instructions
   - May override default coding context

3. **Model-specific prompts:**
   - Different system prompts per model in config
   - RAG-enhanced model gets writing-focused prompt

## Success Criteria

Ask Continue: "Help me write a dramatic scene"
- ✓ Should suggest narrative techniques, pacing, character emotions
- ✗ Should NOT suggest code structure, functions, or refactoring

## Notes

- User observed Continue is "too code oriented" despite pointing to creative writing model
- May need to check Continue.dev documentation for custom prompts
- RAG context injection is working, but base system prompt needs adjustment
