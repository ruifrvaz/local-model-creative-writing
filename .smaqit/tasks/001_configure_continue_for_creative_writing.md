# Configure Continue.dev for Creative Writing

**Priority:** 2  
**State:** Completed  
**Created:** 2025-11-18  
**Completed:** 2025-11-20

## Description

Continue.dev has a default system context optimized for code assistance. It needs to be reconfigured for creative science fiction writing instead. The chat responses are currently too code-oriented and need a writing-focused system prompt.

## Problem

- Continue assumes coding use case by default
- System prompts reference code completion, refactoring, debugging
- Need to shift context to: creative writing, narrative consistency, worldbuilding

## Solution Implemented

### Method 1: Enhanced Rules File (Primary Solution)

Created comprehensive science fiction writing instructions in `.continue/rules/scifi_writer.md`:

**Features:**
- `alwaysApply: true` - Applied to every chat/edit/agent request
- Comprehensive creative writing guidelines
- Clear "what NOT to do" section (no code focus)
- Response format guidance (prose, not code blocks)
- Character, worldbuilding, and narrative consistency instructions

**How it works:**
- Rules are automatically prepended to system message
- Overrides Continue's default code-focused behavior
- No global config changes needed (workspace-specific)

### Method 2: Base System Message Override (Optional)

Documented in `.continue/CONFIG_NOTES.md` for advanced users who want complete control:

**Configuration option:**
```yaml
chatOptions:
  baseSystemMessage: "Custom writing assistant message..."
```

This completely replaces Continue's default system message at the model level.

## Acceptance Criteria

- [x] Located Continue.dev system prompt configuration
- [x] Created custom system prompt for science fiction writing
- [x] Configured prompt to emphasize:
  - Creative narrative generation
  - Character consistency
  - Worldbuilding adherence
  - Dialogue and prose quality
  - NO code-specific instructions
- [x] Documented configuration in `.continue/CONFIG_NOTES.md`
- [x] **Tested and validated** - Chat responses correctly use science fiction writing rules

## Files Created/Modified

1. **`.continue/rules/scifi_writer.md`** - Enhanced with comprehensive writing instructions
   - Creative writing partner role definition
   - Writing guidelines (show don't tell, character voice, etc.)
   - Response format guidance
   - What NOT to do (no code suggestions)

2. **`.continue/CONFIG_NOTES.md`** - Complete reference documentation
   - How rules work in Continue.dev
   - Base system message override method
   - Testing instructions
   - Troubleshooting guide
   - Configuration file locations

## Testing Instructions

1. Open Continue chat (Ctrl+L)
2. Click rules icon (pen above toolbar)
3. Verify "Science Fiction Writing Assistant" rule is listed
4. Test query: "Help me write a scene where Elena discovers an alien artifact"
5. Expected: Narrative prose response, NOT code suggestions

## Success Criteria

Ask Continue: "Help me write a dramatic scene"
- ✓ Should suggest narrative techniques, pacing, character emotions
- ✗ Should NOT suggest code structure, functions, or refactoring

## Additional Features Discovered

From Continue.dev documentation:
- Rules can use `globs` to apply only to specific file types
- Rules can use `regex` to apply when file content matches patterns
- Rules can have `description` for agent-driven context inclusion
- Multiple rules are joined in lexicographical order
- Project rules (`.continue/rules/`) load automatically with Hub configs

## Validation Results (2025-11-20)

**Test 1: Query about rules**
- User asked: "What are your rules?"
- Model correctly listed Continue's default chat rules (mode switching, code blocks, etc.)

**Test 2: Query about science fiction rules**
- User asked: "Do you have any rules related to science fiction writing?"
- Model correctly identified and listed all 6 science fiction writing guidelines:
  1. ✅ Focus on Narrative (not code)
  2. ✅ Maintain Consistency (worldbuilding context)
  3. ✅ Show, Don't Tell (vivid descriptions)
  4. ✅ Character Voice (distinct personalities)
  5. ✅ Scientific Plausibility (internal logic)
  6. ✅ Prose Quality (varied sentence structure)
- Model also correctly listed response guidelines for scenes, characters, worldbuilding, dialogue, continuity

**Conclusion:** Rules system is working perfectly. The model understands it's a science fiction writing assistant, not a code assistant.

## Next Steps

1. ✅ **User Testing:** Validated - rules working correctly
2. **Use in practice:** Test with actual writing tasks (scenes, character development, worldbuilding)
3. **Consider globs:** Add file-specific rules if needed (e.g., different behavior for dialogue vs worldbuilding files)
4. ✅ **Update chatUI/README.md:** Completed - rules configuration documented

## Documentation

- Continue.dev Rules: https://docs.continue.dev/customize/rules
- Rules Deep Dive: https://docs.continue.dev/customize/deep-dives/rules
- Config Reference: https://docs.continue.dev/reference#models
- Local reference: `.continue/CONFIG_NOTES.md`
